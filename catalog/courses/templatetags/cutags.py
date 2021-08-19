import datetime
from django import template

from courses.models import Course

register = template.Library()

@register.filter(name='to_date')
def to_date(value):
    return datetime.date.fromisoformat(value)

@register.filter(name='removeslash')
def removeslash(value):
    return value.replace('/', '::')

def unslash(value):
    return value.replace('::', '/')

@register.filter(name='semester_id2term')
def semester_id2term(value):
    return Course.get_term_by_semester_id(value)

