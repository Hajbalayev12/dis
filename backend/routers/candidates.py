from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from services.parser import parse_cv
from services.skill_extractor import extract_skills
from services.matcher import compute_similarity
from services.scorer import calculate_score

router = APIRouter()

@router.post("/analyze")
async def analyze_candidates(
    job_title: str = Form(...),
    required_skills: str = Form(...),
    experience_years: int = Form(...),
    education: str = Form(...),
    description: str = Form(...),
    files: List[UploadFile] = File(...)
):
    req_skills = [s.strip().lower() for s in required_skills.split(",")]

    job = {
        "title": job_title,
        "required_skills": req_skills,
        "experience_years": experience_years,
        "education": education,
        "description": description,
    }

    results = []

    for file in files:
        content = await file.read()

        raw_text = parse_cv(content, file.filename)
        candidate_data = extract_skills(raw_text)
        candidate_data["filename"] = file.filename

        similarity = compute_similarity(job["description"], raw_text)
        candidate_data["semantic_similarity"] = similarity

        score_result = calculate_score(job, candidate_data)
        score_result["filename"] = file.filename
        score_result["name"] = candidate_data.get("name", file.filename)

        results.append(score_result)

    results.sort(key=lambda x: x["final_score"], reverse=True)

    return {"job": job, "candidates": results}