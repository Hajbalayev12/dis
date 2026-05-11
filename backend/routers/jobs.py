from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

jobs_db = []

class JobCreate(BaseModel):
    title: str
    required_skills: List[str]
    experience_years: int
    education: str
    description: str

@router.post("/")
def create_job(job: JobCreate):
    job_data = job.dict()
    job_data["id"] = len(jobs_db) + 1
    jobs_db.append(job_data)
    return job_data

@router.get("/")
def get_jobs():
    return jobs_db