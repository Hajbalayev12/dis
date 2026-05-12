from fastapi import APIRouter
from database import get_all_jobs, get_job_results

router = APIRouter()

@router.get("/")
def get_jobs():
    return get_all_jobs()

@router.get("/{job_id}/results")
def get_results(job_id: int):
    return get_job_results(job_id)