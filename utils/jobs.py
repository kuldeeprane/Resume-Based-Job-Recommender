import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle
import os

model = SentenceTransformer("all-mpnet-base-v2")

# def load_job_descriptions():
#     # Load CSV instead of JSON
#     return pd.read_csv("data/job_descriptions.csv")

    
def generate_jd_embeddings(jobs):
    jd_embeddings = []
    for job in jobs:
        embedding = model.encode(job["description"])
        jd_embeddings.append({
            "job_id": job["job_id"],
            "title": job["title"],
            "description": job["description"],
            "skills": job["skills"],
            "embedding": embedding
        })
    return jd_embeddings
    

def get_jd_embeddings():
    # Builds the path relative to the current file
    # path = os.path.join("NoteBooks", "demo_embeddings.pkl")
    path = os.path.join("NoteBooks", "job_embeddings.pkl")
    
    with open(path, "rb") as f:
        return pickle.load(f)

