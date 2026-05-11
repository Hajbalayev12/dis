from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import jobs, candidates

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

@app.get("/")
def root():
    return {"status": "CV Matching System is running"}