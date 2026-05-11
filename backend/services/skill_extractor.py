import re
import datetime
from typing import List, Dict

SKILL_MAP = {
    "python": ["python", "python3"],
    "javascript": ["javascript", "js", "es6"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "react.js", "reactjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "angular": ["angular", "angularjs"],
    "node": ["node", "node.js", "nodejs"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],
    "sql": ["sql", "mysql", "postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo"],
    "docker": ["docker"],
    "git": ["git", "github", "gitlab"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "sass", "scss"],
    "rest": ["rest", "restful"],
    "aws": ["aws", "amazon web services"],
    "linux": ["linux", "ubuntu"],
    "java": ["java"],
    "csharp": ["c#", "csharp"],
    "cpp": ["c++", "cpp"],
}

IMPLIED_SKILLS = {
    "react":   ["html", "css", "javascript"],
    "angular": ["html", "css", "typescript"],
    "vue":     ["html", "css", "javascript"],
    "node":    ["javascript"],
    "django":  ["python", "html", "css"],
    "flask":   ["python"],
    "fastapi": ["python"],
}

EDUCATION_KEYWORDS = {
    "phd": ["phd", "doctorate", "ph.d"],
    "masters": ["master", "msc", "m.sc", "mba"],
    "bachelors": ["bachelor", "bsc", "b.sc", "undergraduate"],
    "associate": ["associate", "diploma"],
}


def extract_skills(text: str) -> Dict:
    text_lower = text.lower()
    return {
        "detected_skills": _detect_skills(text_lower),
        "experience_years": _estimate_experience(text),
        "education_level": _detect_education(text_lower),
        "name": _extract_name(text),
        "raw_text": text,
    }


def _detect_skills(text_lower: str) -> List[str]:
    found = []
    for skill_key, aliases in SKILL_MAP.items():
        for alias in aliases:
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill_key)
                break

    implied = []
    for skill in found:
        if skill in IMPLIED_SKILLS:
            for implied_skill in IMPLIED_SKILLS[skill]:
                if implied_skill not in found and implied_skill not in implied:
                    implied.append(implied_skill)

    return found + implied


def _estimate_experience(text: str) -> int:
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s*[:\-]?\s*(\d+)\+?\s*years?',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    year_ranges = re.findall(
        r'(20\d\d|19\d\d)\s*[-–]\s*(20\d\d|present|now)',
        text,
        re.IGNORECASE
    )
    if year_ranges:
        total = 0
        current_year = datetime.datetime.now().year
        for start, end in year_ranges:
            s = int(start)
            e = current_year if end.lower() in ["present", "now"] else int(end)
            total += max(0, e - s)
        return min(total, 30)

    return 0


def _detect_education(text_lower: str) -> str:
    for level, keywords in EDUCATION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return level
    return "unknown"


def _extract_name(text: str) -> str:
    for line in text.split("\n"):
        line = line.strip()
        if 2 <= len(line.split()) <= 5 and not any(c.isdigit() for c in line):
            return line
    return "Unknown"