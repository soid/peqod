import datetime

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


class Term:
    SEMESTER_NAMES = ['spring', 'summer', 'fall']

    def __init__(self, year: int, semester: str):
        self.year = year
        semester = semester.lower()
        assert semester in ['spring', 'fall', 'summer']
        self.semester = semester

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
