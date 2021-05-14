from functools import reduce
from operator import __or__

from django.db.models import Q
from django.shortcuts import render

from courses.models import Course
from courses import utils


def index(request):
    q_term = request.GET.get('term', '').strip()
    if q_term:
        q_semester, q_year = q_term.rsplit(" ", 1)
    else:
        q_semester, q_year = None, None
    q_year = int(q_year)
    q_query = request.GET.get('q', '')
    q_department = request.GET.get('dep', '')
    q_level = request.GET.getlist('lvl', [])
    q_day = request.GET.getlist('d', [])

    course_list = Course.objects

    # filter
    if q_term:
        course_list = course_list.filter(year=q_year).filter(semester=q_semester)
    if q_department:
        course_list = course_list.filter(department=q_department)
    if q_level:
        pass # TODO
        #course_list = course_list.filter(l=q_level)
    if q_day:
        qs = [Q(scheduled_days__contains=day.upper()) for day in q_day]
        qs = reduce(__or__, qs)
        course_list = course_list.filter(qs)
    if q_query:
        course_list = course_list.filter(
            Q(course_descr__icontains=q_query)
            | Q(instructor__icontains=q_query)
            | Q(course_title__icontains=q_query)
            | Q(course_subtitle__icontains=q_query))

    # order
    course_list = course_list.order_by('course_code')[:60]

    # available filters
    semesters = Course.objects.order_by("-year", "semester").values('year', 'semester').distinct()
    departments = Course.objects.order_by("department").values('department').distinct()

    print(q_department)
    context = {
        # filters
        'q_year': q_year,
        'q_semester': q_semester,
        'q_department': q_department,
        'q_query': q_query,
        'q_day': q_day,
        # content
        "course_list": course_list,
        "semesters": semesters,
        "departments": departments,
        "days": utils.DAYS
    }

    return render(request, 'index.html', context)


