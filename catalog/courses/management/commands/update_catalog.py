from datetime import datetime
import json

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import DataError
from django.db.utils import OperationalError
from django.core.exceptions import ValidationError

from courses.models import Course


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('semesters', nargs='+', type=str)

    def handle(self, *args, **options):
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
                for line in fclasses:
                    course = json.loads(line)
                    # find existing one
                    obj = Course.objects.filter(year=year,
                                                semester=semester,
                                                call_number=course['call_number'])
                    if len(obj) > 0:
                        obj = obj[0]
                    else:
                        # create if doesn't exist
                        obj = Course(year=year,
                                     semester=semester,
                                     call_number=course['call_number'])

                    # update fields
                    for key in course.keys():
                        if hasattr(obj, key):
                            val = course[key]
                            if key.startswith('scheduled_time_') and val:
                                val = datetime.strptime(course[key], "%I:%M%p").time()
                            if val == '':
                                val = None
                            setattr(obj, key, val)

                    try:
                        obj.save()
                    except (DataError, OperationalError, ValidationError):
                        print("Error while processing:", course)
                        raise

                    if num % 419 == 0:
                        print("Processed:", num, "/", num_lines)
                    num += 1
            print("Finished for", num, "classes.")
        print('Done.')

