import json
import logging
from os.path import dirname, abspath

from django.core.management.base import BaseCommand

from catalog import settings
from courses.models import Instructor


class Command(BaseCommand):
    help = 'Updates instructors info'

    instructor_fields = ['culpa_link', 'culpa_reviews_count', 'culpa_nugget', 'wikipedia_link']

    def __init__(self, *args, **kwargs):
        self.data_files_location = settings.CATALOG_LOCATION
        self.setup_logger()
        super(Command, self).__init__(*args, **kwargs)

    def setup_logger(self):
        log_filename = "management.log"

        self.logger = logging.getLogger(__name__)
        log_format = '[%(threadName)s] %(levelname)s %(asctime)s - %(message)s'
        logging.basicConfig(level=logging.ERROR,
                            format=log_format)
        log_file_handler = logging.FileHandler(settings.CATALOG_LOGS_DIR + '/' + log_filename)
        log_file_handler.setFormatter(logging.Formatter(log_format))
        self.logger.addHandler(log_file_handler)
        self.logger.setLevel(logging.DEBUG)

    def handle(self, *args, **options):
        self.logger.info("Starting update_instructors.py")
        import_filename = self.data_files_location + "/instructors/instructors.json"
        num_lines = sum(1 for _ in open(import_filename))
        with open(import_filename) as fclasses:
            num = 1
            for line in fclasses:
                instructor_json = json.loads(line)

                # add instructor
                obj, _ = Instructor.get_by_name(instructor_json['name'])
                # update fields
                for field_name in Command.instructor_fields:
                    if instructor_json[field_name]:
                        val = instructor_json[field_name]
                        if 'culpa_nugget' == field_name:
                            val = Command.convert_nugget(val)
                        setattr(obj, field_name, val)

                if 'culpa_reviews' in instructor_json.keys():
                    obj.culpa_reviews = instructor_json['culpa_reviews']

                if 'gscholar' in instructor_json.keys() and instructor_json['gscholar']:
                    gscholar = instructor_json['gscholar']
                    obj.gscholar_json = json.dumps(gscholar)
                    obj.gscholar_hindex = gscholar['hindex']
                    obj.gscholar_hindex5y = gscholar['hindex5y']
                    obj.gscholar_id = gscholar['scholar_id']

                if 'gta' in instructor_json.keys() and instructor_json['gta']:
                    obj.great_teacher_award = int(instructor_json['gta'])

                obj.save()

                if num % 250 == 0:
                    print("Processed:", num, "/", num_lines)
                num += 1
        self.logger.info("Done update_instructors.py")

    @staticmethod
    def convert_nugget(nugget_json):
        if nugget_json == 'silver':
            return 's'
        if nugget_json == 'gold':
            return 'g'
        return None
