from django.contrib import admin
from .models import Course, Instructor, CatalogUpdate


class CatalogUpdateAdmin(admin.ModelAdmin):
    raw_id_fields = ('related_class', 'related_instructor')


admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(CatalogUpdate, CatalogUpdateAdmin)
