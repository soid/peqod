from django.db import models


class Course(models.Model):
    year = models.PositiveSmallIntegerField()
    semester = models.CharField(max_length=6)

    call_number = models.IntegerField()
    class_id = models.CharField(max_length=24)
    section_key = models.CharField(max_length=24)

    course_code = models.CharField(max_length=16)
    course_title = models.CharField(max_length=128)
    course_subtitle = models.CharField(max_length=128)
    course_descr = models.TextField()

    instructor = models.CharField(max_length=128)
    instructor_culpa_link = models.URLField()
    instructor_culpa_reviews_count = models.PositiveSmallIntegerField()
    # instructor_culpa_nugget
    instructor_wikipedia_link = models.URLField()
    link = models.URLField()

    # campus
    department = models.CharField(max_length=128)
    department_code = models.CharField(max_length=12)

    scheduled_time_start = models.TimeField()
    scheduled_time_end = models.TimeField()
    scheduled_days = models.CharField(max_length=7)

    location = models.CharField(max_length=128)
    # method_of_instruction
    # open_to
    points = models.PositiveSmallIntegerField()
    # prerequisites
    # type

    added_date = models.DateTimeField('date added')

