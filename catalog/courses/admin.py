from django.contrib import admin

# Register your models here.

from .models import Course, Instructor

admin.site.register(Course)
admin.site.register(Instructor)
