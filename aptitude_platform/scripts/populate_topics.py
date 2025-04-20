from aptitude.models import Topic, Level

def run():
    level_map = {level.name: level for level in Level.objects.all()}

    topics_data = [
    # Quantitative Aptitude
    {
        "name": "Number System",
        "slug": "number-system",
        "category": "quant",
        "description": "Covers integers, factors, multiples, divisibility, etc.",
        "levels": ["ENTRY", "PSU", "GOVT", "CAT"]
    },
    {
        "name": "HCF and LCM",
        "slug": "hcf-lcm",
        "category": "quant",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT"]
    },
    {
        "name": "Simplification",
        "slug": "simplification",
        "category": "quant",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT"]
    },
    {
        "name": "Ratio and Proportion",
        "slug": "ratio-proportion",
        "category": "quant",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT", "CAT"]
    },
    {
        "name": "Percentages",
        "slug": "percentages",
        "category": "quant",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT", "CAT"]
    },
    {
        "name": "Profit and Loss",
        "slug": "profit-loss",
        "category": "quant",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT", "CAT"]
    },
    {
        "name": "Simple Interest",
        "slug": "simple-interest",
        "category": "quant",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT"]
    },
    {
        "name": "Compound Interest",
        "slug": "compound-interest",
        "category": "quant",
        "description": "",
        "levels": ["PSU", "GOVT", "CAT"]
    },
    {
        "name": "Time and Work",
        "slug": "time-and-work",
        "category": "quant",
        "description": "",
        "levels": ["PSU", "GOVT", "CAT"]
    },
    {
        "name": "Time, Speed, Distance",
        "slug": "time-speed-distance",
        "category": "quant",
        "description": "",
        "levels": ["PSU", "GOVT", "CAT"]
    },
    {
        "name": "Boats and Streams",
        "slug": "boats-streams",
        "category": "quant",
        "description": "",
        "levels": ["GOVT", "CAT"]
    },
    {
        "name": "Pipes and Cisterns",
        "slug": "pipes-cisterns",
        "category": "quant",
        "description": "",
        "levels": ["GOVT", "CAT"]
    },
    {
        "name": "Averages",
        "slug": "averages",
        "category": "quant",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT", "CAT"]
    },
    {
        "name": "Permutations & Combinations",
        "slug": "permutations-combinations",
        "category": "quant",
        "description": "",
        "levels": ["CAT", "UPSC", "ADV"]
    },
    {
        "name": "Probability",
        "slug": "probability",
        "category": "quant",
        "description": "",
        "levels": ["CAT", "UPSC", "ADV"]
    },
    {
        "name": "Mixtures and Alligations",
        "slug": "mixtures-alligations",
        "category": "quant",
        "description": "",
        "levels": ["PSU", "GOVT", "CAT"]
    },
    {
        "name": "Mensuration",
        "slug": "mensuration",
        "category": "quant",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT"]
    },
    {
        "name": "Algebra (Basic)",
        "slug": "algebra-basic",
        "category": "quant",
        "description": "",
        "levels": ["GOVT", "CAT", "UPSC"]
    },
    {
        "name": "Algebra (Advanced)",
        "slug": "algebra-advanced",
        "category": "quant",
        "description": "",
        "levels": ["CAT", "UPSC", "ADV"]
    },
    {
        "name": "Geometry",
        "slug": "geometry",
        "category": "quant",
        "description": "",
        "levels": ["CAT", "UPSC"]
    },
    {
        "name": "Trigonometry",
        "slug": "trigonometry",
        "category": "quant",
        "description": "",
        "levels": ["UPSC", "ADV"]
    },

    # Logical Reasoning
    {
        "name": "Blood Relations",
        "slug": "blood-relations",
        "category": "logical",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT"]
    },
    {
        "name": "Direction Sense",
        "slug": "direction-sense",
        "category": "logical",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT"]
    },
    {
        "name": "Coding-Decoding",
        "slug": "coding-decoding",
        "category": "logical",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT"]
    },
    {
        "name": "Number Series",
        "slug": "number-series",
        "category": "logical",
        "description": "",
        "levels": ["ENTRY", "PSU", "GOVT"]
    },
    {
        "name": "Verbal Reasoning",
        "slug": "verbal-reasoning",
        "category": "logical",
        "description": "",
        "levels": ["PSU", "GOVT", "CAT"]
    },
    {
        "name": "Logical Deductions",
        "slug": "logical-deductions",
        "category": "logical",
        "description": "",
        "levels": ["CAT", "UPSC"]
    },
    {
        "name": "Syllogisms",
        "slug": "syllogisms",
        "category": "logical",
        "description": "",
        "levels": ["PSU", "GOVT", "CAT"]
    },
    {
        "name": "Seating Arrangement",
        "slug": "seating-arrangement",
        "category": "logical",
        "description": "",
        "levels": ["GOVT", "CAT"]
    },
    {
        "name": "Puzzles",
        "slug": "puzzles",
        "category": "logical",
        "description": "",
        "levels": ["GOVT", "CAT", "ADV"]
    },
    {
        "name": "Data Sufficiency",
        "slug": "data-sufficiency",
        "category": "logical",
        "description": "",
        "levels": ["CAT", "ADV"]
    },
    {
        "name": "Input-Output (Machine Logic)",
        "slug": "input-output",
        "category": "logical",
        "description": "",
        "levels": ["PSU", "CAT", "ADV"]
    },

    # Verbal Ability
    {
        "name": "Reading Comprehension",
        "slug": "reading-comprehension",
        "category": "verbal",
        "description": "",
        "levels": ["ENTRY", "GOVT", "CAT", "UPSC"]
    },
    {
        "name": "Sentence Correction",
        "slug": "sentence-correction",
        "category": "verbal",
        "description": "",
        "levels": ["ENTRY", "PSU", "CAT"]
    },
    {
        "name": "Para Jumbles",
        "slug": "para-jumbles",
        "category": "verbal",
        "description": "",
        "levels": ["GOVT", "CAT"]
    },
    {
        "name": "Vocabulary (Synonyms/Antonyms)",
        "slug": "vocabulary",
        "category": "verbal",
        "description": "",
        "levels": ["ENTRY", "GOVT", "CAT"]
    },
    {
        "name": "Fill in the Blanks",
        "slug": "fill-blanks",
        "category": "verbal",
        "description": "",
        "levels": ["ENTRY", "PSU", "CAT"]
    },
    {
        "name": "Cloze Test",
        "slug": "cloze-test",
        "category": "verbal",
        "description": "",
        "levels": ["GOVT", "CAT"]
    },
    {
        "name": "One Word Substitution",
        "slug": "one-word-substitution",
        "category": "verbal",
        "description": "",
        "levels": ["GOVT", "CAT"]
    },
    {
        "name": "Idioms and Phrases",
        "slug": "idioms-phrases",
        "category": "verbal",
        "description": "",
        "levels": ["PSU", "GOVT", "CAT"]
    },
    {
        "name": "Error Spotting",
        "slug": "error-spotting",
        "category": "verbal",
        "description": "",
        "levels": ["PSU", "GOVT", "CAT"]
    },
]

    for data in topics_data:
        topic, created = Topic.objects.get_or_create(
            name=data["name"],
            slug=data["slug"],
            category=data["category"],
            description=data["description"]
        )
        topic.levels.set([level_map[level] for level in data["levels"]])


# Future Technical Topics (category: tech)
# - Data Structures (Basics): ENTRY, ADV
# - Operating Systems: ENTRY, ADV
# - DBMS & SQL: ENTRY, ADV
# - Computer Networks: ENTRY, ADV
# - Programming Logic: ENTRY, ADV
