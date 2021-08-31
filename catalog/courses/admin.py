from django.contrib import admin
from .models import Course, Instructor, CatalogUpdate, CatalogImports


class CatalogUpdateAdmin(admin.ModelAdmin):
    raw_id_fields = ('related_class', 'related_instructor')


admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(CatalogImports)
admin.site.register(CatalogUpdate, CatalogUpdateAdmin)
