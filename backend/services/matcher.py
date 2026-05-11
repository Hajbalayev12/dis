from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_similarity(job_description: str, cv_text: str) -> float:
    if not job_description.strip() or not cv_text.strip():
        return 0.0

    embeddings = model.encode([job_description, cv_text])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

    return float(np.clip(score, 0.0, 1.0))