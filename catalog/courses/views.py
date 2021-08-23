from functools import reduce
from operator import __or__
from typing import List

from urllib import parse

from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.shortcuts import render, get_object_or_404, get_list_or_404

from courses.models import Course, Instructor, CatalogUpdate
from courses import utils
from courses.templatetags.cutags import unslash


def _get_last_updated():
    return Course.objects.order_by('-added_date')[0].added_date


def _get_levels(q_level: List[str]) -> List[int]:
    # convert level queries ['5000-7000'] into [5000, 6000, 7000]
    result = []
    def normz_lvl(level):
        level = int(level) // 1000 * 1000
        assert 0 < level < 10000
        return level
    for lvl in q_level:
        if '-' in lvl:
            lvl_s, lvl_e = lvl.split('-', 1)
            for l in range(normz_lvl(lvl_s), normz_lvl(lvl_e)+1, 1000):
                result.append(normz_lvl(l))
        else:
            result.append(normz_lvl(lvl))
    return result


def index(request):
    q_term = request.GET.get('term', '').strip()
    if q_term:
        q_semester, q_year = q_term.rsplit(" ", 1)
        q_year = int(q_year)
    else:
        interested_term = utils.Term.get_interested_term()
        q_semester, q_year = interested_term.semester.capitalize(), interested_term.year
        q_term = interested_term.get_term_descr()

    q_query = request.GET.get('q', '')
    q_department = request.GET.get('dep')
    if not q_department:
        if request.COOKIES.get(utils.COOKIE_LAST_SEARCHED_DEPARTMENT):
            q_department = request.COOKIES.get(utils.COOKIE_LAST_SEARCHED_DEPARTMENT)
        else:
            q_department = 'Computer Science'
    q_level = request.GET.getlist('lvl', [])
    q_day = request.GET.getlist('d', [])

    course_list = Course.objects

    # filter
    if q_term:
        course_list = course_list.filter(year=q_year).filter(semester=q_semester)
    if q_department:
        course_list = course_list.filter(department=q_department)
    if q_level:
        # create db filter
        qs = []
        for lvl in _get_levels(q_level):
            qs.append(Q(level__gte=lvl, level__lte=lvl+999))
        qs = reduce(__or__, qs)
        course_list = course_list.filter(qs)
    if q_day:
        qs = [Q(scheduled_days__contains=day.upper()) for day in q_day]
        qs = reduce(__or__, qs)
        course_list = course_list.filter(qs)
    if q_query:
        course_list = course_list.filter(
            Q(course_descr__icontains=q_query)
            | Q(instructor__name__icontains=q_query)
            | Q(course_title__icontains=q_query)
            | Q(course_subtitle__icontains=q_query))
    q_extra_options = q_level or q_day

    # order
    course_list = course_list \
        .prefetch_related('instructor') \
        .order_by('semester_id', 'level', 'section_key')  # TODO pagination

    # pagination
    page_number = request.GET.get('p')
    paginator = Paginator(course_list, 100)
    page_obj = paginator.get_page(page_number)

    page_url = request.path
    if request.META['QUERY_STRING']:
        q = parse.parse_qs(request.META['QUERY_STRING'])
        if 'p' in q.keys():
            del q['p']
        page_url = page_url + '?' + parse.urlencode(q, doseq=True)
    else:
        page_url = page_url + '?'

    # available filters
    semesters = Course.objects.order_by("-year", "semester").values('year', 'semester').distinct()
    departments = Course.objects.order_by("department").values('department').distinct()

    context = {
        'menu': 'search',
        'page_url': page_url,
        # filters
        'q_year': q_year,
        'q_semester': q_semester,
        'q_department': q_department,
        'q_query': q_query,
        'q_day': q_day,
        'q_level': q_level,
        'q_extra_options': q_extra_options,
        # content
        "course_list": course_list,
        'page_obj': page_obj,
        "semesters": semesters,
        "departments": departments,
        "days": utils.DAYS,
        # last updated
        'last_updated': _get_last_updated(),
    }

    response = render(request, 'index.html', context)
    response.set_cookie(utils.COOKIE_LAST_SEARCHED_DEPARTMENT, q_department)
    return response


def deps_list(request):
    deps = Course.objects.values("department")\
        .annotate(count_instructors=Count('instructor__id', distinct=True),
                  count_classes=Count('course_code', distinct=True)) \
        .order_by('department')

    context = {
        'menu': 'deps',
        'deps': deps,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'departments.html', context)


def department(request, department: str):
    clss = Course.objects\
        .filter(department=unslash(department))\
        .values("course_code","course_title","course_subtitle")\
        .annotate(count_instructors=Count('instructor__id', distinct=True),
                  last_taught=Max('semester_id'))\
        .order_by('level', 'course_code', 'course_title', 'course_subtitle')

    instructors = Instructor.objects\
        .filter(course__department=unslash(department))\
        .values("name", "wikipedia_link","culpa_link","culpa_reviews_count") \
        .annotate(count_classes=Count('course__id', distinct=True),
                  last_taught=Max('course__semester_id')) \
        .order_by("name")

    last_semesters = Course.objects \
        .filter(department=unslash(department)) \
        .values("year", "semester") \
        .annotate(count_classes=Count('id', distinct=True)) \
        .order_by('-semester_id')[0:4]

    context = {
        'menu': 'deps',
        'department': department,
        'classes': clss,
        'instructors': instructors,
        'last_semesters': last_semesters,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'department.html', context)


def course_list_terms(request, course_code: str):
    courses = get_list_or_404(Course.objects.prefetch_related('instructor').order_by('-semester_id'),
                              course_code=course_code)
    context = {
        'courses': courses,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'course_terms.html', context)


def course(request, course_code: str, term: str):
    year, semester = term.split('-', 1)
    courses = get_list_or_404(Course.objects.prefetch_related('instructor'),
                              course_code=course_code, year=year, semester=semester)
    context = {
        'courses': courses,
        'course_code': course_code,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'course.html', context)


def instructor_view(request, instructor_name: str):
    instr = get_object_or_404(Instructor, name=instructor_name)
    courses = Course.objects \
        .all() \
        .filter(instructor=instr)
    departments = courses \
        .values('department') \
        .distinct() \
        .values_list('department', flat = True)

    context = {
        'instructor': instr,
        'courses': courses.order_by('-semester_id'),
        'departments': departments,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'instructor.html', context)


def updates(request):
    page_number = request.GET.get('p')

    updates = CatalogUpdate.objects \
        .prefetch_related('related_instructor', 'related_class') \
        .order_by('-added_date') \
        .prefetch_related('related_class')

    paginator = Paginator(updates, 100)
    page_obj = paginator.get_page(page_number)

    context = {
        'menu': 'updates',
        'page_obj': page_obj,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'updates.html', context)


def about(request):
    return render(request, 'about.html', {
        'menu': 'about',
        'last_updated': _get_last_updated(),
    })
