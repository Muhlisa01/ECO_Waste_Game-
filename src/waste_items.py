import random

WASTE_ITEMS = [
    {"label": "Shokolad qog'ozi", "category": "Paper"},
    {"label": "Gazeta varaqasi", "category": "Paper"},
    {"label": "Kitobdan parchasi", "category": "Paper"},
    {"label": "Plastik suv shishasi", "category": "Plastic"},
    {"label": "Konserva bankasi", "category": "Plastic"},
    {"label": "Yog'li idish", "category": "Plastic"},
    {"label": "Shisha banka", "category": "Glass"},
    {"label": "Sharob shishasi", "category": "Glass"},
    {"label": "Kosmetika shishasi", "category": "Glass"},
    {"label": "Meva po'stlog'i", "category": "Food"},
    {"label": "Choy qoldiqlari", "category": "Food"},
    {"label": "Pitsa qutisi", "category": "Food"},
    {"label": "Eskirgan mato", "category": "Garbage"},
    {"label": "Niqob qog'ozi", "category": "Garbage"},
    {"label": "Chiqindiga aylangan idish", "category": "Garbage"}
]

CATEGORY_NAMES = {
    "Plastic": "Plastik",
    "Paper": "Qog'oz",
    "Glass": "Shisha",
    "Food": "Organik",
    "Garbage": "Axlat"
}

COLOR_MAP = {
    "Plastic": (245, 127, 23),
    "Paper": (25, 118, 210),
    "Glass": (120, 144, 156),
    "Food": (110, 163, 74),
    "Garbage": (66, 66, 66)
}


def get_allowed_categories(level):
    if level == 1:
        return ["Plastic", "Paper", "Glass"]
    if level == 2:
        return ["Plastic", "Paper", "Glass", "Food"]
    return ["Plastic", "Paper", "Glass", "Food", "Garbage"]


def get_random_waste(level):
    allowed = get_allowed_categories(level)
    # Be defensive: skip entries missing 'category' to avoid KeyError
    choices = [item for item in WASTE_ITEMS if item.get("category") in allowed]
    if not choices:
        # fallback: include any item that has a category
        choices = [item for item in WASTE_ITEMS if item.get("category")]
    if not choices:
        # last resort: pick any item
        return random.choice(WASTE_ITEMS)
    return random.choice(choices)
