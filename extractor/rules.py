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
