import re
import datetime
from typing import List, Dict
from rapidfuzz import fuzz
from services.esco import get_skill_cache, add_custom_skills

FUZZY_THRESHOLD = 88

EDUCATION_KEYWORDS = {
    "phd":       ["phd", "doctorate", "ph.d", "doctor of philosophy"],
    "masters":   ["master", "msc", "m.sc", "mba", "m.eng", "graduate degree"],
    "bachelors": ["bachelor", "bsc", "b.sc", "b.eng", "undergraduate", "b.a."],
    "associate": ["associate", "diploma", "hnd"],
}

IMPLIED_SKILLS = {
    "react":          ["html", "css", "javascript"],
    "angular":        ["html", "css", "typescript"],
    "vue":            ["html", "css", "javascript"],
    "next.js":        ["html", "css", "javascript", "react"],
    "node.js":        ["javascript"],
    "django":         ["python", "html", "css"],
    "flask":          ["python"],
    "fastapi":        ["python"],
    "spring boot":    ["java"],
    "ruby on rails":  ["ruby"],
}


def extract_skills(text: str, custom_skills: List[str] = []) -> Dict:
    if custom_skills:
        add_custom_skills(custom_skills)

    text_lower = text.lower()

    return {
        "detected_skills":  _detect_skills(text_lower),
        "experience_years": _estimate_experience(text),
        "education_level":  _detect_education(text_lower),
        "name":             _extract_name(text),
        "email":            _extract_email(text),
        "phone":            _extract_phone(text),
        "raw_text":         text,
    }


def _detect_skills(text_lower: str) -> List[str]:
    skill_map = get_skill_cache()
    words = re.findall(r'[\w\.\+\#/]+', text_lower)
    found = set()

    # Exact phrase matching
    for skill_key, aliases in skill_map.items():
        for alias in aliases:
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill_key)
                break

    # Fuzzy matching on individual words
    for word in words:
        if len(word) < 4:
            continue
        for skill_key, aliases in skill_map.items():
            if skill_key in found:
                continue
            for alias in aliases:
                if len(alias) < 4:
                    continue
                if fuzz.ratio(word, alias) >= FUZZY_THRESHOLD:
                    found.add(skill_key)
                    break

    # Add implied skills
    implied = set()
    for skill in list(found):
        for implied_skill in IMPLIED_SKILLS.get(skill, []):
            if implied_skill not in found:
                implied.add(implied_skill)

    return sorted(found | implied)


def _estimate_experience(text: str) -> int:
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s*[:\-]?\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+of\s+experience',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    year_ranges = re.findall(
        r'(20\d\d|19\d\d)\s*[-–—]\s*(20\d\d|present|now|current)',
        text, re.IGNORECASE
    )
    if year_ranges:
        total = 0
        current_year = datetime.datetime.now().year
        for start, end in year_ranges:
            s = int(start)
            e = current_year if end.lower() in ["present", "now", "current"] else int(end)
            total += max(0, e - s)
        return min(total, 40)

    return 0


def _detect_education(text_lower: str) -> str:
    for level, keywords in EDUCATION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return level
    return "unknown"


def _extract_name(text: str) -> str:
    for line in text.split("\n")[:10]:
        line = line.strip()
        if 2 <= len(line.split()) <= 4 and not any(c.isdigit() for c in line):
            if not any(kw in line.lower() for kw in ["email", "phone", "address", "linkedin", "github", "cv", "resume"]):
                return line
    return "Unknown"


def _extract_email(text: str) -> str:
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w{2,}', text)
    return match.group(0) if match else ""


def _extract_phone(text: str) -> str:
    match = re.search(r'(\+?\d[\d\s\-\(\)]{7,15}\d)', text)
    return match.group(0).strip() if match else ""