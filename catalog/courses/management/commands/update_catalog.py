import argparse
from datetime import datetime, date
import json

from django.core.management.base import BaseCommand
from django.db.utils import DataError
from django.db.utils import OperationalError
from django.core.exceptions import ValidationError

from courses.models import Course, Instructor, CatalogUpdate


class Command(BaseCommand):
    help = 'Updates provided semester classes'

    def add_arguments(self, parser):
        parser.add_argument('--overwrite-date', type=str, default=None)
        parser.add_argument('--dry-run', default=False, action='store_true')
        parser.add_argument('semesters', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['overwrite_date']:
            update_date = date.fromisoformat(options['overwrite_date'])
        else:
            update_date = date.today()

        for term in options['semesters']:
            tmp = term.split('-')
            year = int(tmp[0])
            semester = tmp[1]
            print("Running for", term)

            import_filename = "/columbia-catalog-data/classes/" \
                              + str(year) + "-" + semester.capitalize() + ".json"
            num_lines = sum(1 for _ in open(import_filename))
            with open(import_filename) as fclasses:
                num = 1
                updated_count = 0
                for line in fclasses:
                    course = json.loads(line)
                    # find existing one
                    obj = Course.objects.filter(year=year,
                                                semester=semester,
                                                call_number=course['call_number'])
                    update = CatalogUpdate()
                    update.added_date = update_date
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
                            if val != getattr(obj, key, None):
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

                    if options['dry_run']:
                        if update.typ:
                            print(update, update.diff)
                    else:
                        try:
                            obj.save()
                            if update.typ:
                                update.save()
                                updated_count += 1
                        except (DataError, OperationalError, ValidationError):
                            print("Error while processing:", course)
                            raise

                    if num % 419 == 0:
                        print("Processed:", num, "/", num_lines, '(' + str(updated_count), 'updated)')
                    num += 1
            print("Finished for", num, "classes.")
            # TODO: delete classes absent in the json file
        print('Done.')

