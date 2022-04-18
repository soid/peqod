import datetime
from functools import reduce
from operator import __or__, __and__
from typing import List

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max, F
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views.decorators.cache import cache_page

from courses.models import Course, Instructor, CatalogUpdate
from courses import utils
from courses.templatetags import cutags
from courses.templatetags.cutags import unslash
from courses.utils import Term

CACHE_GET_LAST_UPDATED = "_get_last_updated"
CACHE_DEP_LIST_PAGE = "department_list_page"
CACHE_DEPARTMENTS = "departments"


def _get_last_updated():
    result = cache.get(CACHE_GET_LAST_UPDATED)
    if not result:
        tmp = Course.objects.order_by('-added_date')
        if len(tmp) > 0:
            result = tmp[0].added_date
        else:
            result = datetime.date(1970, 1, 1)  # no data found
        cache.set(CACHE_GET_LAST_UPDATED, result, 60*60 * 24)  # 24 hours cache
    return result


def _get_departments():
    result = cache.get(CACHE_DEPARTMENTS)
    if not result:
        result = Course.objects.order_by("department").values('department').distinct()
        cache.set(CACHE_DEPARTMENTS, result, 60*60 * 24)  # 24 hours cache
    return result


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


def _get_courses_enrollment_js(courses):
    result = []
    term = None
    term_start = ''
    dates = set()
    max_value = 5
    for c in courses:
        if term is None:
            term = Term(c.year, c.semester)
            term_start = term.get_term_start_date().isoformat()
        if c.enrollment:
            dates.update(c.enrollment.keys())
    if len(dates) <= 3:
        return ''  # don't display the graph when too little data is available
    dates = sorted(list(dates))
    for dt in dates:
        year, month, day = dt.split('-', 2)
        # js Date receives index of month
        enr_all = [str(c.enrollment[dt]['cur']) if dt in c.enrollment else 'null' for c in courses]
        max_value = max([max_value] +
                        [c.enrollment[dt]['cur'] for c in courses if dt in c.enrollment])
        annotation = "null"
        if term_start == dt:
            annotation = '"Semester starts"'
        result.append("[new Date(%s, %s, %s), %s, %s],"
                      % (year, int(month)-1, day, annotation, ",".join(enr_all)))

    result_str = ""
    for c in courses:
        instr_str = str(c.call_number)
        if c.instructor:
            instr_str = c.instructor.name + " / " + instr_str
        result_str += "data.addColumn('number', '%s');\n" % instr_str
    result_str += "data.addRows([\n" + "\n".join(result) + "]);\n"
    result_str += "enableChart = true;\n"
    result_str += "chatMaxValue = %s;\n" % int(max_value * 1.05)  # upper bound of the graph

    return result_str


QUERY_POINTS_MIN = 0
QUERY_POINTS_MAX = 25


def classes(request):
    q_term = request.GET.get('term', '').strip()
    save_term = True
    if not q_term and request.COOKIES.get(utils.COOKIE_LAST_USED_TERM):
        q_term = request.COOKIES.get(utils.COOKIE_LAST_USED_TERM)
    if q_term:
        if q_term != "ALL":
            q_semester, q_year = q_term.rsplit(" ", 1)
            q_year = int(q_year)
        else:
            q_year = q_semester = None
    else:
        # use default
        save_term = False  # don't save default option
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
    q_time_start = request.GET.get('st', '00:00')
    q_time_end = request.GET.get('et', '23:00')
    q_max_enrollment = request.GET.get('enr_max', None)
    q_free_space = request.GET.get('fs', '') == 'on'
    q_points_min = request.GET.get('pts', QUERY_POINTS_MIN)
    q_points_max = request.GET.get('pts_max', QUERY_POINTS_MAX)
    q_points_min, q_points_max = int(q_points_min), int(q_points_max)

    display_fields = set(['scheduled_time', 'instructor', 'points'])

    course_list = Course.objects

    # filter
    if q_term and q_term != "ALL":
        course_list = course_list.filter(year=q_year).filter(semester=q_semester)
    if q_term == "ALL":
        display_fields.add("term")
    if q_department:
        if q_department != "ALL":
            course_list = course_list.filter(department=q_department)
        else:
            display_fields.add("department")
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
    if q_time_start:
        course_list = course_list.filter(scheduled_time_start__gte=datetime.time.fromisoformat(q_time_start))
    if q_time_end:
        course_list = course_list.filter(scheduled_time_end__lte=datetime.time.fromisoformat(q_time_end))
    if q_max_enrollment:
        num = int(q_max_enrollment)
        course_list = course_list.filter(enrollment_max__lte=num)
        display_fields.add("enrollment")
    if q_free_space:
        course_list = course_list.filter(enrollment_cur__lt=F("enrollment_max"))
        display_fields.add("enrollment")
    if q_points_min > 0:
        course_list = course_list.filter(points_min__gte=q_points_min)
    if q_points_max < 25:
        course_list = course_list.filter(points_max__lte=q_points_max)
    if q_query:
        course_list = course_list.filter(
            Q(course_descr__icontains=q_query)
            | Q(instructor__name__icontains=q_query)
            | Q(course_code__icontains=q_query)
            | Q(course_title__icontains=q_query)
            | Q(course_subtitle__icontains=q_query))
    q_extra_options = q_level or q_day \
        or (q_time_start != '06:00' and q_time_start != '00:00') \
        or (q_time_end != '23:00') \
        or q_max_enrollment \
        or q_free_space \
        or (q_points_min != QUERY_POINTS_MIN or q_points_max != QUERY_POINTS_MAX)

    # order
    course_list = course_list \
        .prefetch_related('instructor') \
        .order_by('semester_id', 'level', 'section_key')

    # precompute very similar classes (have only different schedule or instructor), so we display them as a single card
    i = 0
    results_per_page = 100
    prev_c = None
    for c in course_list:
        c.view_instructors = []
        c.view_scheduled_days = []
        if prev_c is not None \
                and prev_c.course_code == c.course_code \
                and prev_c.course_title == c.course_title \
                and prev_c.course_subtitle == c.course_subtitle:
            if prev_c.instructor and c.instructor \
                    and prev_c.instructor.name != c.instructor.name:
                prev_c.view_instructors.append(c.instructor)
                c.view_instructors = prev_c.view_instructors  # next refer to the previous which is the first
                c.view_skip = True
            if prev_c.scheduled_days != c.scheduled_days or prev_c.scheduled_time_start != c.scheduled_time_start:
                prev_c.view_scheduled_days.append((c.scheduled_days, c.scheduled_time_start, c.scheduled_time_end))
                c.view_scheduled_days = prev_c.view_scheduled_days  # next refer to the previous which is the first
                c.view_skip = True

        prev_c = c
        i += 1
        if i >= results_per_page:
            break

    # pagination
    page_number = request.GET.get('p')
    paginator = Paginator(course_list, results_per_page)
    page_obj = paginator.get_page(page_number)

    page_url = utils.get_page_url(request)

    # available filters
    semesters = Course.objects.order_by("-year", "semester").values('year', 'semester').distinct()

    context = {
        'menu': 'classes',
        'page_url': page_url,
        # filters
        'q_year': q_year,
        'q_semester': q_semester,
        'q_term': q_term,
        'q_department': q_department,
        'q_query': q_query,
        'q_day': q_day,
        'q_time_start': q_time_start,
        'q_time_end': q_time_end,
        'q_level': q_level,
        'q_max_enrollment': q_max_enrollment,
        'q_free_space': q_free_space,
        'q_extra_options': q_extra_options,
        'q_points_min': q_points_min,
        'q_points_max': q_points_max,
        'display_fields': display_fields,
        # content
        "course_list": course_list,
        'page_obj': page_obj,
        "semesters": semesters,
        "departments": _get_departments(),
        "days": utils.DAYS,
        # last updated
        'last_updated': _get_last_updated(),
    }

    response = render(request, 'index.html', context)
    response.set_cookie(utils.COOKIE_LAST_SEARCHED_DEPARTMENT, q_department)
    if save_term:
        response.set_cookie(utils.COOKIE_LAST_USED_TERM, q_term, max_age=60*60 * 48)
    return response


@cache_page(60 * 60 * 24, key_prefix=CACHE_DEP_LIST_PAGE)
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


def department_view(request, department_name: str):
    clss = Course.objects\
        .filter(department=unslash(department_name))\
        .values("course_code","course_title","course_subtitle")\
        .annotate(count_instructors=Count('instructor__id', distinct=True),
                  last_taught=Max('semester_id'))\
        .order_by('level', 'course_code', 'course_title', 'course_subtitle')

    instructors = Instructor.objects\
        .filter(course__department=unslash(department_name))\
        .values("name", "wikipedia_link", "culpa_link", "culpa_nugget", "culpa_reviews_count",
                "gscholar_id", "gscholar_hindex", "great_teacher_award") \
        .annotate(count_classes=Count('course__id', distinct=True),
                  last_taught=Max('course__semester_id')) \
        .order_by("name")

    last_semesters = Course.objects \
        .filter(department=unslash(department_name)) \
        .values("year", "semester") \
        .annotate(count_classes=Count('id', distinct=True)) \
        .order_by('-semester_id')[0:4]

    context = {
        'menu': 'deps',
        'department': department_name,
        'classes': clss,
        'instructors': instructors,
        'last_semesters': last_semesters,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'department.html', context)


def course_list_terms(request, course_code: str):
    course_code = cutags.course_code_unurlize(course_code)
    courses = get_list_or_404(Course.objects.prefetch_related('instructor').order_by('-semester_id'),
                              course_code=course_code)
    context = {
        'courses': courses,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'course_terms.html', context)


def course(request, course_code: str, term: str):
    course_code = cutags.course_code_unurlize(course_code)
    year, semester = term.split('-', 1)
    year = int(year)
    courses = get_list_or_404(Course.objects.prefetch_related('instructor'),
                              course_code=course_code, year=year, semester=semester)
    last_terms = utils.Term.get_last_four_terms()
    course_term = utils.Term(year, semester)

    is_latest_term = course_term in last_terms

    context = {
        'courses': courses,
        'enrollment_js': _get_courses_enrollment_js(courses),
        'course_code': course_code,
        'is_latest_term': is_latest_term,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'course.html', context)


def course_section(request, term: str, call_number: str):
    year, semester = term.split('-', 1)
    year = int(year)
    courses = get_list_or_404(Course.objects.prefetch_related('instructor'),
                              call_number=call_number, year=year, semester=semester)
    last_terms = utils.Term.get_last_four_terms()
    course_term = utils.Term(year, semester)
    course_code = courses[0].course_code

    is_latest_term = course_term in last_terms

    context = {
        'courses': courses,
        'show_sections_link': True,
        'course_term': course_term,
        'enrollment_js': _get_courses_enrollment_js(courses),
        'course_code': course_code,
        'is_latest_term': is_latest_term,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'course.html', context)


def instructor_view(request, instructor_name: str):
    instructor_name = cutags.prof_unurlize(instructor_name)
    instr = get_object_or_404(Instructor, name=instructor_name)
    courses = Course.objects \
        .all() \
        .filter(instructor=instr)
    departments = courses \
        .values('department') \
        .distinct() \
        .values_list('department', flat=True)

    context = {
        'instructor': instr,
        'courses': courses.order_by('-semester_id'),
        'departments': departments,
        'last_updated': _get_last_updated(),
    }
    return render(request, 'instructor.html', context)


def instructors(request):
    q_name = request.GET.get('name', '')

    context = {
        'menu': 'instructors',
        'q_name': q_name,
        'no_request': q_name == '',
        'last_updated': _get_last_updated(),
    }

    if q_name and q_name != '':
        q_name = q_name.strip()
        qs = []
        for part in q_name.split():
            qs.append(Q(name__icontains=part))
        qs = reduce(__and__, qs)
        instructors = Instructor.objects.all()
        instructors = instructors.filter(qs)

        instructors = instructors\
            .values("name", "culpa_link", "culpa_reviews_count", "culpa_nugget", "wikipedia_link",
                    "gscholar_id", "gscholar_hindex", "great_teacher_award") \
            .annotate(count_classes=Count('course__id'),
                      last_taught=Max('course__semester_id')) \
            .order_by('name')

        # pagination
        page_number = request.GET.get('p')
        paginator = utils.FasterDjangoPaginator(instructors, 50)
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['paginator'] = paginator
        context['page_url'] = utils.get_page_url(request)

    return render(request, 'instructors.html', context)


def updates(request):
    page_number = request.GET.get('p')

    updates = CatalogUpdate.objects \
        .prefetch_related('related_instructor', 'related_class') \
        .order_by('-added_date') \
        .prefetch_related('related_class')

    # filter departments if requested
    deps_filter = request.GET.getlist('dep')
    if not deps_filter and request.COOKIES.get(utils.COOKIE_LAST_DEPARTMENTS):
        deps_filter = request.COOKIES.get(utils.COOKIE_LAST_DEPARTMENTS).split("|")
    if len(deps_filter) > 0:
        qs = []
        for dep in deps_filter:
            qs.append(Q(department=dep))
        qs = reduce(__or__, qs)
        updates = updates.filter(qs)

    paginator = Paginator(updates, 100)
    page_obj = paginator.get_page(page_number)

    context = {
        'menu': 'updates',
        'page_obj': page_obj,
        "departments": _get_departments(),
        'deps_filter': deps_filter,
        'last_updated': _get_last_updated(),
    }
    response = render(request, 'updates.html', context)
    if deps_filter:
        ck = "|".join(deps_filter)
        if len(ck) < 4096:
            response.set_cookie(utils.COOKIE_LAST_DEPARTMENTS, ck, 60*60 * 24 * 90)
    return response


def about(request):
    return render(request, 'about.html', {
        'menu': 'about',
        'last_updated': _get_last_updated(),
    })
