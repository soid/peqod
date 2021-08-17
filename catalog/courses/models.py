from __future__ import annotations

import datetime
import json

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
    level = models.PositiveSmallIntegerField()

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
    culpa_reviews = models.JSONField(null=True)
    wikipedia_link = models.URLField(null=True)

    @staticmethod
    def get_by_name(name: str) -> Instructor:
        """Returns instructor and a boolean indicating if it's a new instructor"""
        obj = Instructor.objects.filter(name=name)
        if len(obj) > 0:
            return obj[0], False
        else:
            obj = Instructor(name=name)
            return obj, True

class CatalogUpdate(models.Model):
    T_NEW_CLASS = 1
    T_NEW_INSTRUCTOR = 2
    T_DELETED_CLASS = 4
    T_CHANGED_TIME = 8
    T_CHANGED_INSTRUCTOR = 16
    T_CHANGED_DESCRIPTION = 32
    T_CHANGED_LOCATION = 64

    added_date = models.DateField('date added')
    typ = models.IntegerField(default=0)  # bit set of changes
    related_class = models.ForeignKey('Course', null=True, on_delete=models.CASCADE)
    related_instructor = models.ForeignKey('Instructor', null=True, on_delete=models.CASCADE)
    diff = models.TextField(null=True)

    def add_typ(self, typ_to_add: int):
        assert typ_to_add > 0
        self.typ |= typ_to_add

    def check_typ(self, typ):
        return typ & self.typ != 0

    def get_diff(self):
        if not hasattr(self, '_diff_cache'):
            self._diff_cache = json.loads(self.diff)
            for k, val in self._diff_cache.items():
                if 'scheduled_time' in k and val:
                    self._diff_cache[k] = datetime.time.fromisoformat(val)
        return self._diff_cache

    @staticmethod
    def new_class():
        return CatalogUpdate(typ=CatalogUpdate.T_NEW_CLASS)

    def is_T_NEW_CLASS(self):
        return self.check_typ(CatalogUpdate.T_NEW_CLASS)

    def is_T_NEW_INSTRUCTOR(self):
        return self.check_typ(CatalogUpdate.T_NEW_INSTRUCTOR)

    def is_T_DELETED_CLASS(self):
        return self.check_typ(CatalogUpdate.T_DELETED_CLASS)

    def is_T_CHANGED_TIME(self):
        return self.check_typ(CatalogUpdate.T_CHANGED_TIME)

    def is_T_CHANGED_INSTRUCTOR(self):
        return self.check_typ(CatalogUpdate.T_CHANGED_INSTRUCTOR)

    def is_T_CHANGED_DESCRIPTION(self):
        return self.check_typ(CatalogUpdate.T_CHANGED_DESCRIPTION)

    def is_T_CHANGED_LOCATION(self):
        return self.check_typ(CatalogUpdate.T_CHANGED_LOCATION)
