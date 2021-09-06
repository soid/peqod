import datetime
from urllib import parse

from django.core.paginator import Paginator
from django.db.models import Aggregate, CharField
from django.utils.functional import cached_property

DAYS = [
    ('m', 'Monday'),
    ('t', 'Tuesday'),
    ('w', 'Wednesday'),
    ('r', 'Thursday'),
    ('f', 'Friday'),
    ('s', 'Saturday'),
    ('u', 'Sunday')
]
COOKIE_LAST_SEARCHED_DEPARTMENT = 'last_searched_dep'


def get_page_url(request):
    page_url = request.path
    if request.META['QUERY_STRING']:
        q = parse.parse_qs(request.META['QUERY_STRING'])
        if 'p' in q.keys():
            del q['p']
        page_url = page_url + '?' + parse.urlencode(q, doseq=True)
    else:
        page_url = page_url + '?'
    return page_url


class Term:
    SEMESTER_NAMES = ['spring', 'summer', 'fall']

    def __init__(self, year: int, semester: str):
        self.year = year
        semester = semester.lower()
        assert semester in ['spring', 'fall', 'summer']
        self.semester = semester

    def __repr__(self):
        return "Term(" + str(self.year) + ", " + self.semester + ")"

    def __eq__(self, other):
        return self.year == other.year and self.semester == other.semester

    @staticmethod
    def get_interested_term():
        """ Get currently interested term based on current date,
        e.g. late in the fall semester people are interested in spring semester
        """
        today = datetime.date.today()
        td = (today.month, today.day)
        if td <= (4, 1):
            semester = 'Spring'
        elif td <= (6, 20):
            semester = 'Summer'
        elif td <= (11, 1):
            semester = 'Fall'
        else:
            semester = 'Spring'
        return Term(today.year, semester)

    @staticmethod
    def get_last_four_terms():
        i = 4
        term = Term.get_interested_term()
        result = [term]
        while i > 0:
            term = term.get_previous_term()
            result.append(term)
            i -= 1
        return result

    def get_term_descr(self):
        return self.semester.capitalize() + ' ' + str(self.year)

    def get_term_key(self):
        return str(self.year) + '=' + self.semester.capitalize()

    def get_previous_term(self):
        year = self.year
        sem_num = Term.SEMESTER_NAMES.index(self.semester)
        sem_num -= 1
        if sem_num < 0:
            year -= 1
            sem_num = len(Term.SEMESTER_NAMES) - 1
        return Term(year, Term.SEMESTER_NAMES[sem_num])


# taken from https://stackoverflow.com/questions/10340684/group-concat-equivalent-in-django
class Concat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(distinct)s%(expressions)s)'

    def __init__(self, expression, distinct=False, **extra):
        super(Concat, self).__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            output_field=CharField(),
            **extra)


# taken from https://stackoverflow.com/questions/31740039/django-rest-framework-pagination-extremely-slow-count
class FasterDjangoPaginator(Paginator):
    @cached_property
    def count(self):
        # only select 'id' for counting, much cheaper
        return self.object_list.values('id').count()
