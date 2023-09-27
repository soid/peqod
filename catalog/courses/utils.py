import datetime
import json
from collections import defaultdict
from typing import List
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

    # estimated start of semester
    def get_term_start_date(self):
        known_terms = {
            (2021, 'summer'): datetime.date(2021, 5, 3),
            (2021, 'fall'): datetime.date(2021, 9, 9),
            (2023, 'spring'): datetime.date(2023, 1, 17),
            (2023, 'summer'): datetime.date(2023, 5, 22),
            (2023, 'fall'): datetime.date(2023, 9, 5),
            (2024, 'spring'): datetime.date(2024, 1, 16),
            (2024, 'fall'): datetime.date(2024, 9, 3),
        }
        term_t = self.year, self.semester
        if term_t in known_terms:
            return known_terms[term_t]

        # rough estimate of when semester starts
        if self.semester == 'fall':
            return datetime.date(self.year, 9, 5)
        if self.semester == 'spring':
            return datetime.date(self.year, 1, 16)
        if self.semester == 'summer':
            return datetime.date(self.year, 5, 20)

    def get_term_end_date(self):
        known_terms = {
            (2021, 'summer'): datetime.date(2021, 8, 6),
            (2021, 'fall'): datetime.date(2021, 9, 9),
            (2023, 'spring'): datetime.date(2023, 5, 1),
            (2023, 'summer'): datetime.date(2023, 8, 11),
            (2023, 'fall'): datetime.date(2023, 12, 12),
            (2024, 'spring'): datetime.date(2024, 4, 29),
            (2024, 'fall'): datetime.date(2024, 12, 11),
        }
        term_t = self.year, self.semester
        if term_t in known_terms:
            return known_terms[term_t]

        # rough estimate of when semester starts
        if self.semester == 'fall':
            return datetime.date(self.year, 12, 15)
        if self.semester == 'spring':
            return datetime.date(self.year, 5, 3)
        if self.semester == 'summer':
            return datetime.date(self.year, 8, 10)

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


def lazy_read_json(filename: str):
    """
    :return generator returning (json_obj, pos, lenth)

    >>> test_objs = [{'a': 11, 'b': 22, 'c': {'abc': 'z', 'zzz': {}}}, \
                {'a': 31, 'b': 42, 'c': [{'abc': 'z', 'zzz': {}}]}, \
                {'a': 55, 'b': 66, 'c': [{'abc': 'z'}, {'z': 3}, {'y': 3}]}, \
                {'a': 71, 'b': 62, 'c': 63}]
    >>> json_str = json.dumps(test_objs, indent=4, sort_keys=True)
    >>> _create_file("/tmp/test.json", [json_str])
    >>> g = lazy_read_json("/tmp/test.json")
    >>> next(g)
    ({'a': 11, 'b': 22, 'c': {'abc': 'z', 'zzz': {}}}, 120, 116)
    >>> next(g)
    ({'a': 31, 'b': 42, 'c': [{'abc': 'z', 'zzz': {}}]}, 274, 152)
    >>> next(g)
    ({'a': 55, 'b': 66, 'c': [{'abc': 'z'}, {'z': 3}, {'y': 3}]}, 505, 229)
    >>> next(g)
    ({'a': 71, 'b': 62, 'c': 63}, 567, 62)
    >>> next(g)
    Traceback (most recent call last):
      ...
    StopIteration
    """
    with open(filename) as fh:
        state = 0
        json_str = ''
        cb_depth = 0  # curly brace depth
        line = fh.readline()
        while line:
            if line[-1] == "\n":
                line = line[:-1]
            line_strip = line.strip()
            if state == 0 and line == '[':
                state = 1
                pos = fh.tell()
            elif state == 1 and line_strip == '{':
                state = 2
                json_str += line + "\n"
            elif state == 2:
                if len(line_strip) > 0 and line_strip[-1] == '{':  # count nested objects
                    cb_depth += 1

                json_str += line + "\n"
                if cb_depth == 0 and (line_strip == '},' or line_strip == '}'):
                    # end of parsing an object
                    if json_str[-2:] == ",\n":
                        json_str = json_str[:-2]  # remove trailing comma
                    state = 1
                    obj = json.loads(json_str)
                    yield obj, pos, len(json_str)
                    pos = fh.tell()
                    json_str = ""
                elif line_strip == '}' or line_strip == '},':
                    cb_depth -= 1

            line = fh.readline()


class IndexedJsonFile:
    """Loads a json file (json per line), keeps in memory only the index.
    Loads rows when requested. Saves memory

    >>> test_objs = [{"a": 1, "b": "axcc"}, \
                     {"a": 123, "b": "axdasdc"}, \
                     {"a": 23, "b": "aa3332c"}, \
                     {"a": 3, "b": "ac1111"}]
    >>> _create_file("/tmp/test.json", [json.dumps(test_objs, indent=4, sort_keys=True)])
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
            for obj, pos, length in lazy_read_json(self.filename):
                index_value = obj[self.index_column]
                self.index[index_value].append((pos, length))

    def get_list(self, key):
        result = []
        for pos, length in self.index[key]:
            self.fh.seek(pos)
            line = self.fh.read(length)
            obj = json.loads(line)
            result.append(obj)
        return result


days2num = defaultdict(lambda: 10)
days2num.update({"M": 0, "T": 1, "W": 2, "R": 3, "F": 4, "S": 5, "U": 6})
num2dayname = {0: "Monday", 1: "Tuesday", 2: "Wednesday",
               3: "Thursday", 4: "Friday",
               5: "Saturday", 6: "Sunday",
               10: "n/a"}
day2icalday = {0: "MO", 1: "TU", 2: "WE",
               3: "TH", 4: "FR",
               5: "SA", 6: "SU",
               10: ""}


def day2num(days):
    return [days2num[x] for x in days]


def days2ical(days):
    return [day2icalday[x] for x in day2num(days)]


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

