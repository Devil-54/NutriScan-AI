from __future__ import annotations

import re
from dataclasses import dataclass

PARSER_VERSION = "1.0.0"

_PREFIX_RE = re.compile(r"^\s*ingredients?\s*:\s*", re.IGNORECASE)
_DELIMITER_RE = re.compile(r"[,;\n\r•\u2022]+")
_MULTISPACE_RE = re.compile(r"\s+")
_INS_HYPHEN_RE = re.compile(r"\bINS[\s-]+(\d+)", re.IGNORECASE)
_TRAILING_PUNCT_RE = re.compile(r"^[\s.\-–—:;,]+|[\s.\-–—:;,]+$")
_PAREN_RE = re.compile(r"^(.*?)\(([^)]*)\)\s*(.*)$")
_ROMAN_OR_DIGITS_RE = re.compile(r"^(?:[ivx]+|\d+)$", re.IGNORECASE)
_HAS_ALNUM_RE = re.compile(r"[a-zA-Z0-9]")

# Parenthetical content recognized as a redundant synonym of the preceding term - dropped, not split.
_SYNONYM_DROP = {"maida"}

# Standalone-token normalization (applied after splitting/cleaning).
_STANDARDIZATION_MAP = {
    "maida": "Refined Wheat Flour",
    "vit c": "Vitamin C",
    "vit. c": "Vitamin C",
}


@dataclass(frozen=True)
class ParsedIngredients:
    ingredients: list[str]
    count: int


def _normalize_ins_codes(text: str) -> str:
    return _INS_HYPHEN_RE.sub(r"INS \1", text)


def _split_raw(text: str) -> list[str]:
    text = _PREFIX_RE.sub("", text)
    text = _normalize_ins_codes(text)
    parts = _DELIMITER_RE.split(text)
    return [p for p in parts if p is not None]


def _clean_token(token: str) -> str:
    token = _TRAILING_PUNCT_RE.sub("", token)
    token = _MULTISPACE_RE.sub(" ", token).strip()
    return token


def _is_glued_code_suffix(original: str, outer: str, inner: str) -> bool:
    """True for e.g. '500(ii)' - digit immediately followed by '(' with no space,
    and the parenthetical content is a roman numeral or plain number (a code
    variant suffix, not a separate ingredient)."""
    glue_point = original[: len(outer) + 1]
    return glue_point.endswith(f"{outer}(") and outer[-1:].isdigit() and bool(_ROMAN_OR_DIGITS_RE.match(inner.strip()))


def _expand_parentheses(token: str) -> list[str]:
    match = _PAREN_RE.match(token)
    if not match:
        return [token]

    outer, inner, rest = match.group(1).strip(), match.group(2).strip(), match.group(3).strip()

    if _is_glued_code_suffix(token, outer, inner):
        combined = f"{outer}({inner})"
        return [combined] + ([rest] if rest else [])

    if inner.lower() in _SYNONYM_DROP:
        return ([outer] if outer else []) + ([rest] if rest else [])

    result = ([outer] if outer else []) + ([inner] if inner else [])
    if rest:
        result.append(rest)
    return result


def _standardize(token: str) -> str:
    return _STANDARDIZATION_MAP.get(token.lower(), token)


def parse_ingredients(ocr_text: str) -> ParsedIngredients:
    if not ocr_text or not ocr_text.strip():
        return ParsedIngredients(ingredients=[], count=0)

    raw_tokens = _split_raw(ocr_text)

    expanded: list[str] = []
    for raw in raw_tokens:
        cleaned = _clean_token(raw)
        if not cleaned:
            continue
        expanded.extend(_expand_parentheses(cleaned))

    final: list[str] = []
    seen: set[str] = set()
    for item in expanded:
        item = _clean_token(item)
        if not item or not _HAS_ALNUM_RE.search(item):
            continue
        item = _standardize(item)
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        final.append(item)

    return ParsedIngredients(ingredients=final, count=len(final))
