from typing import Dict, List

EDUCATION_RANK = {
    "phd": 4,
    "masters": 3,
    "bachelors": 2,
    "associate": 1,
    "unknown": 0,
}


def calculate_score(job: Dict, candidate: Dict) -> Dict:
    skill_score      = _skill_match(job["required_skills"], candidate["detected_skills"])
    experience_score = _experience_match(job["experience_years"], candidate["experience_years"])
    education_score  = _education_match(job["education"], candidate["education_level"])
    semantic_score   = candidate.get("semantic_similarity", 0.0)

    final = (
        skill_score      * 0.40 +
        semantic_score   * 0.25 +
        experience_score * 0.25 +
        education_score  * 0.10
    )

    matched = [s for s in job["required_skills"] if s in candidate["detected_skills"]]
    missing = [s for s in job["required_skills"] if s not in candidate["detected_skills"]]

    return {
        "final_score":      round(final * 100, 1),
        "skill_score":      round(skill_score * 100, 1),
        "experience_score": round(experience_score * 100, 1),
        "education_score":  round(education_score * 100, 1),
        "semantic_score":   round(semantic_score * 100, 1),
        "matched_skills":   matched,
        "missing_skills":   missing,
        "detected_skills":  candidate["detected_skills"],
        "experience_years": candidate["experience_years"],
        "education_level":  candidate["education_level"],
        "explanation":      _explain(matched, missing, candidate["experience_years"], job["experience_years"]),
    }


def _skill_match(required: List[str], detected: List[str]) -> float:
    if not required:
        return 0.0
    matched = sum(1 for s in required if s in detected)
    return matched / len(required)


def _experience_match(required_years: int, candidate_years: int) -> float:
    if required_years == 0:
        return 1.0
    if candidate_years >= required_years:
        return 1.0
    return candidate_years / required_years


def _education_match(required_edu: str, candidate_edu: str) -> float:
    required_rank  = EDUCATION_RANK.get(required_edu.lower(), 0)
    candidate_rank = EDUCATION_RANK.get(candidate_edu.lower(), 0)
    if required_rank == 0:
        return 1.0
    if candidate_rank >= required_rank:
        return 1.0
    return candidate_rank / required_rank


def _explain(matched: List[str], missing: List[str], cand_exp: int, req_exp: int) -> str:
    parts = []
    parts.append(f"Matched {len(matched)} of {len(matched) + len(missing)} required skills.")
    if missing:
        parts.append(f"Missing: {', '.join(missing)}.")
    if cand_exp >= req_exp:
        parts.append(f"Experience requirement met ({cand_exp} years).")
    else:
        parts.append(f"Experience below requirement ({cand_exp}/{req_exp} years).")
    return " ".join(parts)