import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "cv_matcher.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            required_skills TEXT,
            experience_years INTEGER,
            education   TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id        INTEGER NOT NULL,
            candidate_name TEXT,
            filename      TEXT,
            email         TEXT,
            phone         TEXT,
            final_score   REAL,
            skill_score   REAL,
            experience_score REAL,
            education_score  REAL,
            semantic_score   REAL,
            matched_skills   TEXT,
            missing_skills   TEXT,
            extra_skills     TEXT,
            experience_years INTEGER,
            education_level  TEXT,
            recommendation   TEXT,
            explanation      TEXT,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized.")


def save_job(job: dict) -> int:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (title, description, required_skills, experience_years, education, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        job["title"],
        job["description"],
        json.dumps(job["required_skills"]),
        job["experience_years"],
        job["education"],
        datetime.utcnow().isoformat(),
    ))
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    return job_id


def save_analysis(job_id: int, result: dict):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analyses (
            job_id, candidate_name, filename, email, phone,
            final_score, skill_score, experience_score, education_score, semantic_score,
            matched_skills, missing_skills, extra_skills,
            experience_years, education_level, recommendation, explanation, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        result.get("name", ""),
        result.get("filename", ""),
        result.get("email", ""),
        result.get("phone", ""),
        result.get("final_score", 0),
        result.get("skill_score", 0),
        result.get("experience_score", 0),
        result.get("education_score", 0),
        result.get("semantic_score", 0),
        json.dumps(result.get("matched_skills", [])),
        json.dumps(result.get("missing_skills", [])),
        json.dumps(result.get("extra_skills", [])),
        result.get("experience_years", 0),
        result.get("education_level", ""),
        result.get("recommendation", ""),
        result.get("explanation", ""),
        datetime.utcnow().isoformat(),
    ))
    conn.commit()
    conn.close()


def get_all_jobs() -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.*, COUNT(a.id) as candidate_count,
               MAX(a.final_score) as top_score
        FROM jobs j
        LEFT JOIN analyses a ON j.id = a.job_id
        GROUP BY j.id
        ORDER BY j.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["required_skills"] = json.loads(d["required_skills"])
        result.append(d)
    return result


def get_job_results(job_id: int) -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM analyses
        WHERE job_id = ?
        ORDER BY final_score DESC
    """, (job_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["matched_skills"] = json.loads(d["matched_skills"])
        d["missing_skills"] = json.loads(d["missing_skills"])
        d["extra_skills"]   = json.loads(d["extra_skills"])
        result.append(d)
    return result