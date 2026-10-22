from __future__ import annotations

import re

_MULTI_SPACE = re.compile(r"\s+")
_INS_HYPHEN = re.compile(r"\bINS[\s-]*(\d+)", re.IGNORECASE)
_E_NUMBER = re.compile(r"\bE[\s-]?(\d{3,4}[a-zA-Z]?)\b", re.IGNORECASE)

# E-number -> INS-number is a 1:1 numeric mapping in virtually all cases (same codex additive numbering).
def normalize_e_to_ins(text: str) -> str:
    return _E_NUMBER.sub(lambda m: f"INS {m.group(1)}", text)


def normalize_ins_spacing(text: str) -> str:
    return _INS_HYPHEN.sub(r"INS \1", text)


def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.strip()
    name = _MULTI_SPACE.sub(" ", name)
    name = normalize_e_to_ins(name)
    name = normalize_ins_spacing(name)
    if not re.match(r"^INS\b", name, re.IGNORECASE):
        name = name.title() if name.isupper() or name.islower() else name
    return name.strip()


# Small internal alias -> canonical mapping (no external dataset dependency).
CANONICAL_ALIAS_MAP: dict[str, str] = {
    "sucrose": "Sugar",
    "brown sugar": "Sugar",
    "cane sugar": "Sugar",
    "ins322": "Lecithin",
    "ins 322": "Lecithin",
    "lecithin": "Lecithin",
}


def resolve_canonical_name(name: str) -> str:
    normalized = normalize_name(name)
    return CANONICAL_ALIAS_MAP.get(normalized.lower(), normalized)
