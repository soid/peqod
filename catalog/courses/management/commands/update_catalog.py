from django.core.management.base import BaseCommand, CommandError
from django.db.utils import DataError
from django.db.utils import OperationalError
from courses.models import Course
import json


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

            with open("/columbia-catalog-data/classes/" + year + "-" + semester.capitalize() + ".json") as fclasses:
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
                            setattr(obj, key, course[key])

                    try:
                        obj.save()
                    except (DataError, OperationalError):
                        print("Error while processing:", course)
                        raise

                    if num % 419 == 0:
                        print("Processed:", num)
                    num += 1
            print("Finished for", num, "classes.")
        print('Done.')

