"""Best-effort text heuristics for fields that raw ATS APIs rarely expose
as structured data (seniority level, years of experience, degree
requirement). These are intentionally simple substring/regex checks - good
enough for a v0 pipeline, not a substitute for an NLP model.
"""
import re

LEVEL_PATTERNS = [
    ("intern", ["intern", "internship", "co-op"]),
    ("staff", ["staff", "principal", "distinguished"]),
    ("senior", ["senior", "sr.", "sr ", "lead "]),
    ("junior", ["junior", "jr.", "jr ", "entry level", "entry-level", "new grad", "graduate"]),
]

DEGREE_PATTERNS = [
    ("phd", [r"\bph\.?d\b", r"\bdoctorate\b"]),
    ("master", [r"\bmaster'?s?\b", r"\bmba\b", r"\bm\.s\.\b"]),
    ("bachelor", [r"\bbachelor'?s?\b", r"\bundergraduate degree\b", r"\bb\.s\.\b", r"\bbs/ba\b"]),
]

YEARS_PATTERN = re.compile(r"(\d+)\+?\s*(?:-\s*\d+\s*)?years? of (?:relevant )?experience", re.IGNORECASE)


def guess_level(title: str) -> str:
    lowered = title.lower()
    for level, keywords in LEVEL_PATTERNS:
        if any(keyword in lowered for keyword in keywords):
            return level
    return "unknown"


def guess_degree_requirement(text: str) -> str:
    lowered = text.lower()
    for degree, patterns in DEGREE_PATTERNS:
        if any(re.search(pattern, lowered) for pattern in patterns):
            return degree
    return "none"


def guess_min_years_experience(text: str) -> int | None:
    match = YEARS_PATTERN.search(text)
    if not match:
        return None
    return int(match.group(1))
