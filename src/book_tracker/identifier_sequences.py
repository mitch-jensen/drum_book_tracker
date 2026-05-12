import re

ROMAN_NUMERALS = (
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
    "XIII",
    "XIV",
    "XV",
    "XVI",
    "XVII",
    "XVIII",
    "XIX",
    "XX",
    "XXI",
    "XXII",
    "XXIII",
    "XXIV",
    "XXV",
    "XXVI",
    "XXVII",
    "XXVIII",
    "XXIX",
    "XXX",
    "XXXI",
    "XXXII",
    "XXXIII",
    "XXXIV",
    "XXXV",
    "XXXVI",
    "XXXVII",
    "XXXVIII",
    "XXXIX",
    "XL",
    "XLI",
    "XLII",
    "XLIII",
    "XLIV",
    "XLV",
    "XLVI",
    "XLVII",
    "XLVIII",
    "XLIX",
    "L",
)

_ROMAN_INDEX = {identifier: index for index, identifier in enumerate(ROMAN_NUMERALS, 1)}
_LETTER_SUFFIX_RE = re.compile(r"^(?P<prefix>.+?)(?P<suffix>[A-Za-z])$")


def _letter_range(start: str, end: str) -> list[str] | None:
    if len(start) != 1 or len(end) != 1 or not start.isalpha() or not end.isalpha():
        return None
    if start.isupper() != end.isupper():
        return None

    start_ord = ord(start)
    end_ord = ord(end)
    if start_ord > end_ord:
        return None

    return [chr(value) for value in range(start_ord, end_ord + 1)]


def _number_range(start: str, end: str) -> list[str] | None:
    if not start.isdecimal() or not end.isdecimal():
        return None

    start_int = int(start)
    end_int = int(end)
    if start_int > end_int:
        return None

    return [str(value) for value in range(start_int, end_int + 1)]


def _roman_range(start: str, end: str) -> list[str] | None:
    if start not in _ROMAN_INDEX or end not in _ROMAN_INDEX:
        return None

    start_index = _ROMAN_INDEX[start]
    end_index = _ROMAN_INDEX[end]
    if start_index > end_index:
        return None

    return list(ROMAN_NUMERALS[start_index - 1 : end_index])


def _letter_suffix_range(start: str, end: str) -> list[str] | None:
    start_match = _LETTER_SUFFIX_RE.fullmatch(start)
    end_match = _LETTER_SUFFIX_RE.fullmatch(end)
    if start_match is None or end_match is None:
        return None
    if start_match["prefix"] != end_match["prefix"]:
        return None

    suffixes = _letter_range(start_match["suffix"], end_match["suffix"])
    if suffixes is None:
        return None

    return [f"{start_match['prefix']}{suffix}" for suffix in suffixes]


def generate_identifier_sequence(start: str, end: str) -> list[str]:
    """Generate a simple ordered exercise identifier sequence."""
    normalized_start = start.strip()
    normalized_end = end.strip()

    if normalized_start.isdecimal() and normalized_end.isdecimal() and int(normalized_start) > int(normalized_end):
        msg = "Start must be less than or equal to end."
        raise ValueError(msg)
    if normalized_start in _ROMAN_INDEX and normalized_end in _ROMAN_INDEX and _ROMAN_INDEX[normalized_start] > _ROMAN_INDEX[normalized_end]:
        msg = "Start must be less than or equal to end."
        raise ValueError(msg)
    if len(normalized_start) == 1 and len(normalized_end) == 1 and normalized_start > normalized_end:
        msg = "Start must be less than or equal to end."
        raise ValueError(msg)

    for generator in (_number_range, _roman_range, _letter_range, _letter_suffix_range):
        identifiers = generator(normalized_start, normalized_end)
        if identifiers is not None:
            return identifiers

    msg = "Enter a supported identifier range: numbers, letters, roman numerals, or a shared prefix with letter suffixes."
    raise ValueError(msg)


def identifier_positions(identifiers: list[str]) -> dict[str, int]:
    """Return zero-based positions for generated identifiers."""
    return {identifier: index for index, identifier in enumerate(identifiers)}
