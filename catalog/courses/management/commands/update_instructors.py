import json
from django.core.management.base import BaseCommand

from courses.models import Instructor


class Command(BaseCommand):
    help = 'Updates instructors info'

    instructor_fields = ['culpa_link', 'culpa_reviews_count', 'culpa_nugget', 'wikipedia_link']

    def handle(self, *args, **options):
        import_filename = "/columbia-catalog-data/instructors/instructors.json"
        num_lines = sum(1 for _ in open(import_filename))
        with open(import_filename) as fclasses:
            num = 1
            for line in fclasses:
                instructor_json = json.loads(line)
                obj = Instructor.get_by_name(instructor_json['name'])
                # update fields
                for field_name in Command.instructor_fields:
                    if instructor_json[field_name]:
                        val = instructor_json[field_name]
                        if 'culpa_nugget' == field_name:
                            val = Command.convert_nugget(val)
                        setattr(obj, field_name, val)
                obj.save()
                if num % 250 == 0:
                    print("Processed:", num, "/", num_lines)
                num += 1

    @staticmethod
    def convert_nugget(nugget_json):
        if nugget_json == 'silver':
            return 's'
        if nugget_json == 'gold':
            return 'g'
        return None