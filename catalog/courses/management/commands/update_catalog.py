import logging
from datetime import datetime, date, timezone
import json
from os import listdir
from os.path import getmtime, dirname, abspath
from typing import Dict, List
import pandas as pd

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db.utils import DataError, IntegrityError
from django.db.utils import OperationalError
from django.core.exceptions import ValidationError

from catalog import settings
from courses import utils, views
from courses.models import Course, Instructor, CatalogUpdate, CatalogImports


class Command(BaseCommand):
    help = 'Updates provided semester classes'

    def __init__(self, *args, **kwargs):
        self.data_files_location = settings.CATALOG_LOCATION + '/classes/'
        self.data_enrollment_files_location = settings.CATALOG_LOCATION + '/classes-enrollment/'
        self.setup_logger()
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('--overwrite-date', type=str, default=None)
        parser.add_argument('--dry-run', default=False, action='store_true',
                            help="do not update database, print in console")
        parser.add_argument('--no-updates', default=False, action='store_true',
                            help="do not generate updates for this run")
        parser.add_argument('semesters', nargs='+', type=str, help="semesters (e.g. 2021-Fall), or ALL")

    def setup_logger(self):
        log_filename = "management.log"

        self.logger = logging.getLogger(__name__)
        log_format = '[%(threadName)s] %(levelname)s %(asctime)s - %(message)s'
        logging.basicConfig(level=logging.ERROR,
                            format=log_format)
        this_dir = dirname(abspath(__file__))
        log_file_handler = logging.FileHandler(this_dir + '/' + log_filename)
        log_file_handler.setFormatter(logging.Formatter(log_format))
        self.logger.addHandler(log_file_handler)
        self.logger.setLevel(logging.DEBUG)

    def handle(self, *args, **options):
        self.logger.info("Starting update_catalog.py")
        if options['overwrite_date']:
            update_date = date.fromisoformat(options['overwrite_date'])
        else:
            update_date = date.today()

        semesters = options['semesters']
        if 'ALL' in semesters:
            assert len(semesters) == 1
            semesters = self.get_changed_semesters()

        for term in semesters:
            tmp = term.split('-')
            year = int(tmp[0])
            semester = tmp[1]
            self.logger.info("Running for %s", term)

            # list current call numbers in db, so we can remove those not in json
            cur_call_numbers = Course.objects\
                .filter(year=year, semester=semester)\
                .values('department')\
                .annotate(call_numbers=utils.Concat('call_number'))
            cur_call_numbers: Dict[str, List[int]] = {
                item['department']: set(int(x) for x in item['call_numbers'].split(','))
                for item in cur_call_numbers
            }

            # read enrollment file
            enrollment_fn = self.data_enrollment_files_location \
                            + str(year) + "-" + semester.capitalize() + ".json"
            enrollment_df = pd.read_json(enrollment_fn, lines=True, dtype=object)
            enrollment_df.set_index('call_number', inplace=True)

            # read classes file
            import_filename = self.data_files_location \
                              + str(year) + "-" + semester.capitalize() + ".json"
            num_lines = sum(1 for _ in open(import_filename))
            with open(import_filename) as fclasses:
                num = 1
                updated_count = 0
                for line in fclasses:
                    course = json.loads(line)
                    # skip bad data
                    if 'course_title' not in course or not course['course_title']:
                        self.logger.info("WARNING: No course_title, skipping: %s", course)
                        continue
                    # find existing one
                    obj = Course.objects.filter(year=year,
                                                semester=semester,
                                                call_number=course['call_number'])
                    update = CatalogUpdate()
                    update.added_date = update_date
                    update.year = year
                    update.semester = semester
                    update.department = course['department']
                    update_diff = {}
                    if len(obj) > 0:
                        obj = obj[0]
                    else:
                        # create if doesn't exist
                        obj = Course(year=year,
                                     semester=semester,
                                     call_number=course['call_number'])
                        update.add_typ(CatalogUpdate.T_NEW_CLASS)

                    update.related_class = obj

                    # instructor
                    if course['instructor']:
                        instructor, is_new_instr = Instructor.get_by_name(course['instructor'])

                        if obj.instructor is not None and obj.instructor != instructor:
                            update.add_typ(CatalogUpdate.T_CHANGED_INSTRUCTOR)
                            update_diff['old_instructor'] = obj.instructor.name
                            update_diff['new_instructor'] = instructor.name

                        obj.instructor = instructor
                        update.related_instructor = instructor

                        instructor.save()

                        if is_new_instr:
                            update.add_typ(CatalogUpdate.T_NEW_INSTRUCTOR)

                    # update fields
                    for key in course.keys():
                        if key.startswith('instructor'):
                            continue
                        if hasattr(obj, key):
                            val = course[key]
                            val_ser = val
                            old_val_ser = getattr(obj, key, None)
                            if key.startswith('scheduled_time_'):
                                if val:
                                    val = datetime.strptime(course[key], "%I:%M%p").time()
                                    val_ser = val.isoformat()
                                if old_val_ser:
                                    old_val_ser = old_val_ser.isoformat()
                            if val == '':
                                val = None
                            # adjust CatalogUpdate
                            val_db = getattr(obj, key, None)
                            if type(val) != type(val_db) and val_db is not None and val is not None:
                                # cast to the same type as in db
                                val = type(val_db)(val)
                            if val != val_db:
                                flag_add_diff = True
                                if key.startswith('scheduled_'):
                                    update.add_typ(CatalogUpdate.T_CHANGED_TIME)
                                elif key == 'course_descr':
                                    update.add_typ(CatalogUpdate.T_CHANGED_DESCRIPTION)
                                elif key == 'location':
                                    update.add_typ(CatalogUpdate.T_CHANGED_LOCATION)
                                else:
                                    flag_add_diff = False
                                if flag_add_diff:
                                    update_diff['old_' + key] = old_val_ser
                                    update_diff['new_' + key] = val_ser

                            # update db
                            setattr(obj, key, val)

                    update.diff = json.dumps(update_diff)

                    # update enrollment
                    if course['call_number'] in enrollment_df.index:
                        course_enr_row = enrollment_df.loc[course['call_number']]
                        course_enr = course_enr_row['enrollment']
                        obj.enrollment = course_enr

                        last_dt = max(course_enr.keys())
                        # print("course_enr[last_dt]", course_enr[last_dt], last_dt)
                        obj.enrollment_cur = course_enr[last_dt]['cur']
                        obj.enrollment_max = course_enr[last_dt]['max']

                    # remove from list of call numbers in current db
                    if course['department'] in cur_call_numbers.keys():
                        if int(course['call_number']) in cur_call_numbers[course['department']]:
                            cur_call_numbers[course['department']].remove(int(course['call_number']))

                    # save updated course
                    if options['dry_run']:
                        if update.typ:
                            self.logger.info("%s %s", update, update.diff)
                    else:
                        try:
                            obj.save()
                            if update.typ and not options['no_updates']:
                                update.save()
                                updated_count += 1
                        except (DataError, OperationalError, ValidationError, IntegrityError):
                            self.logger.error("Error while processing: %s", course)
                            raise

                    if num % 419 == 0:
                        self.logger.info("Processed: %d / %d (%d updated)", num, num_lines, updated_count)
                    num += 1

            ts = getmtime(import_filename)
            modification_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            ci = CatalogImports.objects.filter(term=term).first()
            if not ci:
                ci = CatalogImports(term=term)
            ci.last_modified_date = modification_dt
            ci.save()

            # delete classes absent in the json file
            deleted_count = 0
            deleted_ids = []
            for department, cns in cur_call_numbers.items():
                for call_number in cns:
                    course = Course.objects.filter(year=year, semester=semester,
                                                   department=department, call_number=call_number).first()
                    if not course:
                        self.logger.warning("Couldn't find class even though it's in current db list. "
                                            "Department: %s; call number: %d", department, call_number)
                        continue

                    update = CatalogUpdate()
                    update.add_typ(CatalogUpdate.T_DELETED_CLASS)
                    update.added_date = update_date
                    update.year = year
                    update.semester = semester
                    update.department = department
                    update_diff = {
                        'course_title': course.course_title,
                        'course_subtitle': course.course_subtitle,
                        'course_code': course.course_code,
                        'call_number': course.call_number,
                        'scheduled_days': course.scheduled_days,
                    }
                    if course.scheduled_time_start:
                        update_diff['scheduled_time_start'] = course.scheduled_time_start.isoformat()
                    if course.scheduled_time_end:
                        update_diff['scheduled_time_end'] = course.scheduled_time_end.isoformat()
                    if course.instructor:
                        update.related_instructor = course.instructor
                    update.diff = json.dumps(update_diff)

                    update.save()
                    course.delete()
                    deleted_ids.append(course.call_number)
                    deleted_count += 1
            self.logger.info("Deleted %d classes (%s)", deleted_count, deleted_ids)
            self.logger.info("Finished updating %d classes for %s", num, term)

        cache.delete_many([views.CACHE_GET_LAST_UPDATED,
                           views.CACHE_DEP_LIST_PAGE])
        self.logger.info('Done.')

    def get_changed_semesters(self):
        """Find JSON files for semesters that were changed"""
        result = []
        for fn in listdir(self.data_files_location):
            if fn.endswith('.json'):
                term, _ = fn.split('.', 1)
                cat_imp = CatalogImports.objects.filter(term=term).first()
                if cat_imp:
                    ts = getmtime(self.data_files_location + '/' + fn)
                    modification_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                    if modification_dt == cat_imp.last_modified_date:
                        # skip, not modified
                        continue
                result.append(term)
        return result
