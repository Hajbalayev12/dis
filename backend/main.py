from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import jobs, candidates
from services.esco import fetch_esco_skills
from database import init_db

app = FastAPI(title="CV Matching System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router,       prefix="/api/jobs",       tags=["Jobs"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])


@app.on_event("startup")
async def startup_event():
    init_db()
    await fetch_esco_skills(limit=500)


@app.get("/")
def root():
    return {"status": "CV Matching System is running"}