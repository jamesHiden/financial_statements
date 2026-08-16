"""Parsing helpers for the number formats Codal statement tables use.

Replaces the old num2words/word2number round-trip in convert_to_en.py with a
direct string parse: strip thousands separators, treat parentheses as a
negative sign, and normalize Persian/Arabic digits to ASCII.
"""
import re

_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_DIGIT_TRANSLATION = {ord(p): str(i) for i, p in enumerate(_PERSIAN_DIGITS)}
_DIGIT_TRANSLATION.update({ord(a): str(i) for i, a in enumerate(_ARABIC_DIGITS)})

_PLACEHOLDER_RE = re.compile(r"^[\s\-–—.]*$")


def parse_number(raw: object) -> float | None:
    """Parse a Codal table cell into a float, or None if it holds no value.

    Handles thousands separators (','), parenthesized negatives ('(1,234)'),
    Persian/Arabic digits, and blank/placeholder cells ('-', '', NaN).
    """
    if raw is None:
        return None
    text = str(raw).translate(_DIGIT_TRANSLATION).strip()
    if not text or text.lower() == "nan" or _PLACEHOLDER_RE.match(text):
        return None

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]
    text = text.replace(",", "").replace("٬", "").strip()
    if text.startswith("-"):
        negative = True
        text = text[1:]

    if not re.fullmatch(r"\d+(\.\d+)?", text):
        return None

    value = float(text)
    return -value if negative else value
