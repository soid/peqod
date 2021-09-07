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
    if value is None:
        return ""
    return Course.get_term_by_semester_id(value)


# use nice urls e.g. _ in instructor names instead of %20

@register.filter(name='prof_urlize')
def prof_urlize(value):
    return value.replace(' ', '_')


def prof_unurlize(value):
    return value.replace('_', ' ')


@register.filter(name='course_code_urlize')
def course_code_urlize(value):
    return value.replace(' ', '-')


def course_code_unurlize(value):
    return value.replace('-', ' ')
