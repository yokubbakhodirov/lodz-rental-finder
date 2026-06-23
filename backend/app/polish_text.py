DIACRITIC_MAP = {
    "ą": "a",
    "ć": "c",
    "ę": "e",
    "ł": "l",
    "ń": "n",
    "ó": "o",
    "ś": "s",
    "ź": "z",
    "ż": "z",
}


def fold_polish(text: str) -> str:
    """Strip Polish diacritics so e.g. "Baluty" matches "Bałuty".

    Polish ł/ą/etc. aren't combining accents, so Unicode NFD normalization
    won't strip them on its own — needed because users often type district
    names without diacritics.
    """
    lowered = text.lower()
    return "".join(DIACRITIC_MAP.get(ch, ch) for ch in lowered)
