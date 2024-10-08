# The purpose of this file is to make a list of departments with canonical names

# Department name to canonical name (if it's different only)
dep2canonical = {
    "Accounting (ACCT)": "Accounting",
    "African American and African Diaspora": "African American and African Diaspora Studies",
    "African Studies, Institute of": "African Studies",
    "African-American Studies, Institute for Research in": "African American Studies",
    "Africana Studies (AFRS)": "Africana Studies",
    "Africana Studies (AFSB)": "Africana Studies",
    "American Studies @Barnard": "American Studies (Barnard)",
    "Anthropology @Barnard": "Anthropology (Barnard)",
    "Architecture @Barnard": "Architecture (Barnard)",
    "Art History @Barnard": "Art History (Barnard)",
    "Asian and Middle East @Barnard": "Asian and Middle Eastern Studies (Barnard)",
    "Athena Center for Leadership Studies @Barnard": "Athena Center for Leadership Studies (Barnard)",
    "Biological Sciences @Barnard": "Biological Sciences (Barnard)",
    "BARNARD SUMMER PROGRAMS": "Summer Programs (Barnard)",
    "Chemistry @Barnard": "Chemistry (Barnard)",
    "Classics @Barnard": "Classics (Barnard)",
    "Cntr Environ Rsch & Conservat": "Center for Environmental Research and Conservation",
    "Cognitive Science @Barnard": "Cognitive Science (Barnard)",
    "Comparative Literature and Society @Barnard": "Comparative Literature and Society (Barnard)",
    "Comparative Literature and Society, Center for": "Comparative Literature and Society",
    "Comparative Literature and Society, Institute for": "Comparative Literature and Society",
    "Computer Science @Barnard": "Computer Science (Barnard)",
    "Consortium for Critical Interdisciplinary Studies @Barnard": "Consortium for Critical Interdisciplinary Studies (Barnard)",
    "Core (A&S;)": "Core Curriculum",
    "Core (A&S)": "Core Curriculum",
    "Dance @Barnard": "Dance (Barnard)",
    "DATA SCIENCE INS": "Data Science Institute",
    "Economics @Barnard": "Economics (Barnard)",
    "Education @Barnard": "Education (Barnard)",
    "English @Barnard": "English (Barnard)",
    "Environmental Sciences @Barnard": "Environmental Sciences (Barnard)",
    "Epidemiology: Exec Master Program": "Epidemiology",
    "Executive Classes in HPM": "Executive Classes in Health Policy and Management",
    "Film @Barnard": "Film (Barnard)",
    "First-Year Seminar Program @Barnard": "First-Year Seminar Program (Barnard)",
    "First-Year Writing @Barnard": "First-Year Writing (Barnard)",
    "French @Barnard": "French (Barnard)",
    "German @Barnard": "German (Barnard)",
    "Health Policy & Management": "Health Policy and Management",
    "History @Barnard": "History (Barnard)",
    "Human Nutrition, Institute of": "Institute of Human Nutrition",
    "Human Rights (HRTB)": "Human Rights",
    "Humanities (College)": "Humanities",
    "Information & Knowledge Strat": "Information and Knowledge Strategy",
    "Institute for Israel & Jewish Studies": "Institute for Israel and Jewish Studies",
    "Institute for Study of Human Rights": "Institute for the Study of Human Rights",
    "Interdepartmental (Engineering)": "Interdepartmental Engineering",
    "Italian @Barnard": "Italian (Barnard)",
    "Jazz Studies, Center for": "Center for Jazz Studies",
    "Latin-American & Carib RS": "Latin American and Caribbean Studies",
    "Mathematics @Barnard": "Mathematics (Barnard)",
    "Medieval and Renaissance Studies @Barnard": "Medieval and Renaissance Studies (Barnard)",
    "Music @Barnard": "Music (Barnard)",
    "Negotiation & Conflict Resolution": "Negotiation and Conflict Resolution",
    "Neurological Surgery (NEUS)": "Neurological Surgery",
    "Neuroscience & Behavior @Barnard": "Neuroscience and Behavior (Barnard)",
    "Neurosurgery (NUSR)": "Neurosurgery",
    "Non Profit Management": "Non-Profit Management",
    "OFFC OF THE REGISTRAR": "Office of the Registrar",
    "ONLINE MS IN EPIDEMIOLOGY": "Online MS in Epidemiology",
    "Otolaryngology / Head and Neck Surgery": "Otolaryngology/Head and Neck Surgery",
    "Philosophy @Barnard": "Philosophy (Barnard)",
    "Physical Education @Barnard": "Physical Education (Barnard)",
    "Physics and Astronomy @Barnard": "Physics and Astronomy (Barnard)",
    "Physiology & Cellular Biophysics": "Physiology and Cellular Biophysics",
    "Political Science @Barnard": "Political Science (Barnard)",
    "Pre-College Program (Barnard)": "Pre-College Programs (Barnard)",
    "Pre-College Programs (SHSP)": "Pre-College Programs",
    "Psychology @Barnard": "Psychology (Barnard)",
    "Rehabilitation Medicine (RMED)": "Rehabilitation Medicine",
    "Religion @Barnard": "Religion (Barnard)",
    "Russian Eurasian E. European": "Russian, Eurasian, and East European Studies",
    "Scholars of Distinction @Barnard": "Scholars of Distinction (Barnard)",
    "SCHOOL OF PROFESSIONAL STUDIES": "School of Professional Studies",
    "School of Professional Studies (DVSP)": "School of Professional Studies",
    "School of Professional Studies (SCEN)": "School of Professional Studies",
    "School of Professional Studies (SPS)": "School of Professional Studies",
    "Science and Public Policy @Barnard": "Science and Public Policy (Barnard)",
    "Slavic Languages @Barnard": "Slavic Languages (Barnard)",
    "Sociology @Barnard": "Sociology (Barnard)",
    "Summer Session (SS)": "Summer Session",
    "Summer Session (SUMM)": "Summer Session",
    "Theatre @Barnard": "Theatre (Barnard)",
    "Union Theological Seminary (UTSD)": "Union Theological Seminary",
    "Urban Studies @Barnard": "Urban Studies (Barnard)"
}


def create_reverse_mapping(department_map):
    reverse_map = {}
    for original, canonical in department_map.items():
        if canonical not in reverse_map:
            reverse_map[canonical] = []
        reverse_map[canonical].append(original)
    return reverse_map


canonical2deps = create_reverse_mapping(dep2canonical)
