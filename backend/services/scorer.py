from typing import Dict, List

EDUCATION_RANK = {
    "phd":       4,
    "masters":   3,
    "bachelors": 2,
    "associate": 1,
    "unknown":   0,
}


def calculate_score(job: Dict, candidate: Dict) -> Dict:
    skill_score      = _skill_match(job["required_skills"], candidate["detected_skills"])
    experience_score = _experience_match(job["experience_years"], candidate["experience_years"])
    education_score  = _education_match(job["education"], candidate["education_level"])
    semantic_score   = candidate.get("semantic_similarity", 0.0)

    # Bonus: candidate has extra skills beyond required
    bonus = _extra_skills_bonus(job["required_skills"], candidate["detected_skills"])

    raw_final = (
        skill_score      * 0.40 +
        semantic_score   * 0.25 +
        experience_score * 0.20 +
        education_score  * 0.10 +
        bonus            * 0.05
    )

    # Clamp to 100
    final = min(raw_final, 1.0)

    matched = [s for s in job["required_skills"] if s in candidate["detected_skills"]]
    missing = [s for s in job["required_skills"] if s not in candidate["detected_skills"]]
    extra   = [s for s in candidate["detected_skills"] if s not in job["required_skills"]]

    return {
        "final_score":      round(final * 100, 1),
        "skill_score":      round(skill_score * 100, 1),
        "experience_score": round(experience_score * 100, 1),
        "education_score":  round(education_score * 100, 1),
        "semantic_score":   round(semantic_score * 100, 1),
        "bonus_score":      round(bonus * 100, 1),
        "matched_skills":   matched,
        "missing_skills":   missing,
        "extra_skills":     extra[:10],  # top 10 extra skills
        "detected_skills":  candidate["detected_skills"],
        "experience_years": candidate["experience_years"],
        "education_level":  candidate["education_level"],
        "recommendation":   _recommend(final),
        "explanation":      _explain(
            matched, missing, extra,
            candidate["experience_years"], job["experience_years"],
            candidate["education_level"], job["education"],
            semantic_score
        ),
    }


def _skill_match(required: List[str], detected: List[str]) -> float:
    if not required:
        return 0.0
    matched = sum(1 for s in required if s in detected)
    ratio   = matched / len(required)

    # Partial credit curve — being close still scores well
    if ratio >= 0.9:
        return 1.0
    elif ratio >= 0.7:
        return 0.85 + (ratio - 0.7) * 0.75
    elif ratio >= 0.5:
        return 0.65 + (ratio - 0.5) * 1.0
    else:
        return ratio * 1.3


def _experience_match(required_years: int, candidate_years: int) -> float:
    if required_years == 0:
        return 1.0
    if candidate_years >= required_years:
        # Bonus for exceeding requirement (up to 10% extra)
        excess = min((candidate_years - required_years) / required_years, 0.1)
        return min(1.0 + excess, 1.0)
    ratio = candidate_years / required_years
    # Soft penalty — being close still scores reasonably
    return round(ratio ** 0.75, 4)


def _education_match(required_edu: str, candidate_edu: str) -> float:
    required_rank  = EDUCATION_RANK.get(required_edu.lower(), 0)
    candidate_rank = EDUCATION_RANK.get(candidate_edu.lower(), 0)
    if required_rank == 0:
        return 1.0
    if candidate_rank >= required_rank:
        return 1.0
    if candidate_rank == 0:
        return 0.3
    return round(candidate_rank / required_rank, 4)


def _extra_skills_bonus(required: List[str], detected: List[str]) -> float:
    """Small bonus for having skills beyond what's required."""
    extra = [s for s in detected if s not in required]
    if not extra:
        return 0.0
    # Max bonus capped at 1.0 (5% of final score)
    return min(len(extra) / 20, 1.0)


def _recommend(score: float) -> str:
    if score >= 0.85:
        return "Strong Match — Highly Recommended"
    elif score >= 0.70:
        return "Good Match — Recommended"
    elif score >= 0.55:
        return "Partial Match — Consider for Interview"
    elif score >= 0.40:
        return "Weak Match — Review Manually"
    else:
        return "Poor Match — Not Recommended"


def _explain(
    matched: List[str],
    missing: List[str],
    extra: List[str],
    cand_exp: int,
    req_exp: int,
    cand_edu: str,
    req_edu: str,
    semantic: float,
) -> str:
    parts = []

    # Skills
    total = len(matched) + len(missing)
    parts.append(f"Matched {len(matched)}/{total} required skills.")
    if missing:
        parts.append(f"Missing skills: {', '.join(missing)}.")
    if extra:
        parts.append(f"Additional skills detected: {', '.join(extra[:5])}.")

    # Experience
    if req_exp == 0:
        parts.append("No experience requirement set.")
    elif cand_exp >= req_exp:
        parts.append(f"Experience requirement met ({cand_exp} yrs vs {req_exp} required).")
    else:
        parts.append(f"Experience below requirement ({cand_exp} yrs vs {req_exp} required).")

    # Education
    cand_rank = EDUCATION_RANK.get(cand_edu.lower(), 0)
    req_rank  = EDUCATION_RANK.get(req_edu.lower(), 0)
    if cand_rank >= req_rank:
        parts.append(f"Education requirement met ({cand_edu}).")
    else:
        parts.append(f"Education below requirement ({cand_edu} vs {req_edu} required).")

    # Semantic
    if semantic >= 0.75:
        parts.append("CV content is highly relevant to the job description.")
    elif semantic >= 0.50:
        parts.append("CV content is moderately relevant to the job description.")
    else:
        parts.append("CV content has low relevance to the job description.")

    return " ".join(parts)