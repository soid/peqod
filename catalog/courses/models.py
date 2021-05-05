from django.db import models


class Course(models.Model):
    year = models.PositiveSmallIntegerField()
    semester = models.CharField(max_length=6)

    call_number = models.IntegerField()
    class_id = models.CharField(max_length=24)
    section_key = models.CharField(max_length=24)

    course_code = models.CharField(max_length=16)
    course_title = models.CharField(max_length=128)
    course_subtitle = models.CharField(max_length=128, null=True)
    course_descr = models.TextField(null=True)

    instructor = models.CharField(max_length=128, null=True)
    instructor_culpa_link = models.URLField(null=True)
    instructor_culpa_reviews_count = models.PositiveSmallIntegerField(null=True)
    # instructor_culpa_nugget
    instructor_wikipedia_link = models.URLField(null=True)
    link = models.URLField(null=True)

    # campus
    department = models.CharField(max_length=128)
    department_code = models.CharField(max_length=12)

    scheduled_time_start = models.TimeField(null=True)
    scheduled_time_end = models.TimeField(null=True)
    scheduled_days = models.CharField(max_length=7, null=True)

    location = models.CharField(max_length=128, null=True)
    # method_of_instruction
    # open_to
    points = models.CharField(max_length=6)
    # prerequisites
    # type

    added_date = models.DateTimeField('date added', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year', 'semester', 'call_number'], name='class per semester')
        ]
