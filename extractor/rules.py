# extractor/rules.py

# Titles/designations to detect near PERSON names
TITLE_PATTERNS = [
    # Government
    "Minister", "Union Minister", "Cabinet Minister", "Minister of State", "MoS",
    "Chief Minister", "Deputy Chief Minister",
    "Home Minister", "Finance Minister", "Law Minister", "Education Minister",

    # Civil service / administration
    "Secretary", "Chief Secretary", "Joint Secretary", "Additional Secretary",
    "Commissioner", "Director",

    # Judiciary
    "Judge", "Justice", "Chief Justice", "Additional Judge",

    # Academia / admin (commonly on gov/institution sites)
    "Professor", "Vice Chancellor", "Registrar", "Dean"
]
TITLE_WORDS = [
    # Government
    "Minister", "Secretary", "Deputy Secretary", "Additional Secretary",
    "Joint Secretary", "Commissioner", "Deputy Commissioner",
    "Chief", "Director", "Assistant Director",

    # DOJ-specific (USA)
    "Attorney General", "Deputy Attorney General", "Associate Attorney General",
    "Assistant Attorney General", "Solicitor General", "U.S. Attorney",
    "United States Attorney", "Inspector General", "Chief of Staff",

    # Judiciary
    "Judge", "Justice", "Chief Justice",

    # University (for your other tests)
    "Chancellor", "Vice Chancellor", "Pro Vice Chancellor",
    "Registrar", "Dean", "Professor", "Head of Department", "HOD"
]

