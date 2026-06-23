import re

from .models import Brief
from .polish_text import fold_polish

LODZ_DISTRICTS = ["Polesie", "Śródmieście", "Górna", "Bałuty", "Widzew"]

ROOM_WORDS: dict[str, int] = {
    "studio": 1,
    "kawalerka": 1,
    "1 room": 1,
    "one room": 1,
    "2 room": 2,
    "two room": 2,
    "3 room": 3,
    "three room": 3,
    "4 room": 4,
    "four room": 4,
}

BUDGET_RE = re.compile(r"(\d{3,5})\s*(pln|zł|zl)?")
ROOM_DIGIT_RE = re.compile(r"(\d)\s*[- ]?room")
RENOVATED_RE = re.compile(r"renovat|new|modern|good condition|nice")


def parse_brief(raw_text: str) -> Brief:
    text = raw_text.lower()
    folded_text = fold_polish(raw_text)

    budget_match = BUDGET_RE.search(text)
    budget_pln = int(budget_match.group(1)) if budget_match else None

    rooms: int | None = None
    room_digit_match = ROOM_DIGIT_RE.search(text)
    if room_digit_match:
        rooms = int(room_digit_match.group(1))
    else:
        for word, count in ROOM_WORDS.items():
            if word in text:
                rooms = count
                break

    districts = [d for d in LODZ_DISTRICTS if fold_polish(d) in folded_text]

    wants_renovated = bool(RENOVATED_RE.search(text))

    return Brief(
        raw_text=raw_text,
        budget_pln=budget_pln,
        rooms=rooms,
        districts=districts,
        wants_renovated=wants_renovated,
    )
