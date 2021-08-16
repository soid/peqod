import datetime
from django import template


register = template.Library()

@register.filter(name='to_date')
def to_date(value):
    return datetime.date.fromisoformat(value)

@register.filter(name='removeslash')
def removeslash(value):
    return value.replace('/', '::')

def unslash(value):
    return value.replace('::', '/')
