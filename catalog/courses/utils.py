import datetime
import json
from collections import defaultdict
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
COOKIE_LAST_USED_TERM = 'last_used_term'
COOKIE_LAST_DEPARTMENTS = 'last_update_departments'


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
        year = today.year
        if td <= (3, 20):
            semester = 'Spring'
        elif td <= (4, 1):
            semester = 'Summer'
        elif td <= (10, 20):
            semester = 'Fall'
        else:
            semester = 'Spring'
            year += 1
        return Term(year, semester)

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
        return str(self.year) + '-' + self.semester.capitalize()

    def get_term_start_date(self):
        known_terms = {
            (2021, 'summer'): datetime.date(2021, 6, 2),
            (2021, 'fall'): datetime.date(2021, 9, 9),
        }
        term_t = self.year, self.semester
        if term_t in known_terms:
            return known_terms[term_t]

        # rough estimate of when semester starts
        if self.semester == 'fall':
            return datetime.date(self.year, 9, 5)
        if self.semester == 'spring':
            return datetime.date(self.year, 1, 18)
        if self.semester == 'summer':
            return datetime.date(self.year, 6, 1)

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


def _create_file(filename, lines):
    # cause doctest can't input new line characters :(
    f = open(filename, "w")
    for line in lines:
        f.write(line)
        f.write("\n")
    f.close()


class IndexedJsonFile:
    """Loads a json file (json per line), keeps in memory only the index.
    Loads rows when requested. Saves memory

    >>> _create_file("/tmp/test.json", ['{"a": 1, "b": "axcc"}', \
         '{"a": 123, "b": "axdasdc"}','{"a": 23, "b": "aa3332c"}','{"a": 3, "b": "ac1111"}'])
    >>> obj = IndexedJsonFile("/tmp/test.json", "a")
    >>> obj.get_list(123)
    [{'a': 123, 'b': 'axdasdc'}]
    >>> obj.get_list(1)
    [{'a': 1, 'b': 'axcc'}]
    >>> obj.get_list(23)
    [{'a': 23, 'b': 'aa3332c'}]
    >>> obj.get_list(10000000)
    []
    >>> obj.get_list(3)
    [{'a': 3, 'b': 'ac1111'}]
    >>> obj = IndexedJsonFile(None, "a")
    >>> obj.get_list(1)
    []
    """

    def __init__(self, filename: str, index_column: str):
        self.filename = filename
        self.index_column = index_column

        # index
        self.index = defaultdict(lambda: [])  # index_value -> [file locations]
        if filename:
            self.fh = open(self.filename, 'r')
            pos = 0
            line = self.fh.readline()
            while line:
                obj = json.loads(line)
                index_value = obj[self.index_column]
                self.index[index_value].append(pos)
                pos = self.fh.tell()
                line = self.fh.readline()

    def get_list(self, key):
        result = []
        for pos in self.index[key]:
            self.fh.seek(pos)
            line = self.fh.readline()
            obj = json.loads(line)
            result.append(obj)
        return result


