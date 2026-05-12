from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response
from typing import List
from services.parser import parse_cv, parse_cv_sections
from services.skill_extractor import extract_skills, _estimate_experience
from services.matcher import compute_similarity
from services.scorer import calculate_score
from services.report import generate_report
from database import save_job, save_analysis, get_job_results, get_all_jobs

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
        "title":            job_title,
        "required_skills":  req_skills,
        "experience_years": experience_years,
        "education":        education,
        "description":      description,
    }

    job_id  = save_job(job)
    results = []

    for file in files:
        content = await file.read()

        sections  = parse_cv_sections(content, file.filename)
        full_text = sections["full"]

        skill_text = sections.get("skills", "") + "\n" + full_text
        exp_text   = sections.get("experience", "") + "\n" + full_text

        candidate_data = extract_skills(skill_text, custom_skills=req_skills)
        candidate_data["experience_years"] = _estimate_experience(exp_text)
        candidate_data["filename"]         = file.filename
        candidate_data["sections"]         = {
            k: v[:300] for k, v in sections.items() if k != "full"
        }

        similarity = compute_similarity(job["description"], full_text)
        candidate_data["semantic_similarity"] = similarity

        score_result             = calculate_score(job, candidate_data)
        score_result["filename"] = file.filename
        score_result["name"]     = candidate_data.get("name", file.filename)
        score_result["email"]    = candidate_data.get("email", "")
        score_result["phone"]    = candidate_data.get("phone", "")
        score_result["sections"] = candidate_data.get("sections", {})

        save_analysis(job_id, score_result)
        results.append(score_result)

    results.sort(key=lambda x: x["final_score"], reverse=True)

    return {"job": job, "job_id": job_id, "candidates": results}


@router.get("/history")
def get_history():
    return get_all_jobs()


@router.get("/{job_id}/report")
def download_report(job_id: int):
    jobs = get_all_jobs()
    job  = next((j for j in jobs if j["id"] == job_id), None)
    if not job:
        return Response(content="Job not found", status_code=404)

    candidates = get_job_results(job_id)
    pdf_bytes  = generate_report(job, candidates)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f"attachment; filename=report_{job_id}.pdf"
        }
    )