from __future__ import annotations
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

    instructor = models.ForeignKey('Instructor', null=True, on_delete=models.CASCADE)
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
    edited_date = models.DateTimeField('date edited', auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year', 'semester', 'call_number'], name='class per semester')
        ]

    def get_term(self) -> str:
        return str(self.year) + "-" + self.semester


class Instructor(models.Model):
    name = models.CharField(max_length=128)
    culpa_link = models.URLField(null=True)
    culpa_reviews_count = models.PositiveSmallIntegerField(null=True)
    culpa_nugget = models.CharField(max_length=1, null=True)
    wikipedia_link = models.URLField(null=True)

    @staticmethod
    def get_by_name(name: str) -> Instructor:
        obj = Instructor.objects.filter(name=name)
        if len(obj) > 0:
            return obj[0]
        else:
            obj = Instructor(name=name)
            return obj
