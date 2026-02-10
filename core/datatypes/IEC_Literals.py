from __future__ import annotations

import datetime
import re

_BASE_PREFIXES = {
    "2": 2,
    "8": 8,
    "10": 10,
    "16": 16,
}

_TYPE_PREFIXES = {
    "BOOL",
    "BYTE",
    "WORD",
    "DWORD",
    "LWORD",
    "SINT",
    "INT",
    "DINT",
    "LINT",
    "USINT",
    "UINT",
    "UDINT",
    "ULINT",
    "REAL",
    "LREAL",
    "STRING",
    "WSTRING",
    "TIME",
    "DATE",
}

_TIME_UNITS_MS = {
    "d": 86400000.0,
    "h": 3600000.0,
    "m": 60000.0,
    "s": 1000.0,
    "ms": 1.0,
    "us": 0.001,
    "ns": 0.000001,
}

_TIME_TOKEN_RE = re.compile(r"(\d+(?:\.\d+)?)(MS|US|NS|D|H|M|S)", re.IGNORECASE)


def parse_iec_int_literal(text: str) -> int:
    s = text.strip()
    if not s:
        raise ValueError("Empty integer literal")

    sign = 1
    if s[0] in "+-":
        sign = -1 if s[0] == "-" else 1
        s = s[1:].strip()

    if s.lower().startswith("0x"):
        return sign * int(s, 16)

    parts = s.split("#")
    if len(parts) == 1:
        base = 10
        digits = parts[0]
    elif len(parts) == 2:
        left, right = parts
        left_upper = left.strip().upper()
        if left_upper in _BASE_PREFIXES:
            base = _BASE_PREFIXES[left_upper]
            digits = right
        elif left_upper in _TYPE_PREFIXES:
            base = 10
            digits = right
        else:
            raise ValueError("Invalid integer literal prefix")
    elif len(parts) == 3:
        _, base_part, digits = parts
        base_upper = base_part.strip().upper()
        if base_upper not in _BASE_PREFIXES:
            raise ValueError("Invalid integer literal base")
        base = _BASE_PREFIXES[base_upper]
    else:
        raise ValueError("Invalid integer literal format")

    digits = digits.strip().replace("_", "")
    if not digits:
        raise ValueError("Empty integer literal digits")

    return sign * int(digits, base)


def parse_iec_real_literal(text: str) -> float:
    s = text.strip()
    if not s:
        raise ValueError("Empty real literal")

    if "#" in s:
        s = s.split("#")[-1]

    s = s.strip().replace("_", "")
    if not s:
        raise ValueError("Empty real literal digits")

    return float(s)


def parse_iec_bool_literal(text: str) -> bool:
    s = text.strip()
    if not s:
        raise ValueError("Empty BOOL literal")

    if "#" in s:
        s = s.split("#")[-1]

    s_upper = s.strip().upper()
    if s_upper == "TRUE":
        return True
    if s_upper == "FALSE":
        return False

    return bool(parse_iec_int_literal(s))


def parse_iec_string_literal(text: str) -> str:
    s = text.strip()
    if not s:
        return ""

    upper = s.upper()
    if upper.startswith("STRING#") or upper.startswith("WSTRING#"):
        s = s.split("#", 1)[1]

    s = s.strip()
    if len(s) >= 2 and ((s[0] == "'" and s[-1] == "'") or (s[0] == '"' and s[-1] == '"')):
        s = s[1:-1]

    return s


def parse_iec_time_literal(text: str) -> int:
    s = text.strip()
    if not s:
        raise ValueError("Empty TIME literal")

    upper = s.upper()
    if upper.startswith("TIME#"):
        s = s[5:]
    elif upper.startswith("T#"):
        s = s[2:]

    s = s.strip().replace("_", "")
    if not s:
        raise ValueError("Empty TIME literal")

    sign = 1
    if s[0] in "+-":
        sign = -1 if s[0] == "-" else 1
        s = s[1:].strip()

    if not s:
        raise ValueError("Empty TIME literal")

    if re.fullmatch(r"\d+", s):
        return sign * int(s)

    total_ms = 0.0
    index = 0
    for match in _TIME_TOKEN_RE.finditer(s):
        if match.start() != index:
            raise ValueError("Invalid TIME literal format")
        index = match.end()
        value = float(match.group(1))
        unit = match.group(2).lower()
        total_ms += value * _TIME_UNITS_MS[unit]

    if index != len(s):
        raise ValueError("Invalid TIME literal format")

    return int(round(sign * total_ms))


def parse_iec_date_literal(text: str) -> datetime.date:
    s = text.strip()
    if not s:
        raise ValueError("Empty DATE literal")

    upper = s.upper()
    if upper.startswith("DATE#"):
        s = s.split("#", 1)[1]
    elif upper.startswith("D#"):
        s = s.split("#", 1)[1]

    s = s.strip()
    if not s:
        raise ValueError("Empty DATE literal")

    return datetime.date.fromisoformat(s)
