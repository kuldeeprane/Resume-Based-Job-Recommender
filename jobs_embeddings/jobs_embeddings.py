import hashlib
import pickle
import pandas as pd
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

# ---------------- Setup ----------------
QDRANT_COLLECTION = "jds1"
client = QdrantClient(
    path="local_qdrant",  # Local disk-based DB
    prefer_grpc=True
)
model = SentenceTransformer("all-mpnet-base-v2")

# ✅ Hash generator
def hash_to_uuid(text: str):
    return hashlib.md5(text.encode()).hexdigest()

# ✅ Ensure Qdrant collection exists
def ensure_collection(vector_size: int = 768):
    if not client.collection_exists(QDRANT_COLLECTION):
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        print(f"-> Collection '{QDRANT_COLLECTION}' created.")
    else:
        print(f"-> Collection '{QDRANT_COLLECTION}' already exists.")

#  Generate embeddings from CSV
def generate_embeddings_from_csv(csv_path: str):
    df = pd.read_csv(csv_path)
    
    required_cols = ['Title', 'job_description_clean', 'Required Skills']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    jd_embeddings = []
    for _, row in df.iterrows():
        combined_text = f"{row['Title']} {row['Required Skills']} {row['job_description_clean']}"
        embedding = model.encode(combined_text)

        jd_embeddings.append({
            "title": row["Title"],
            "description": row["job_description_clean"],
            "skills": row["Required Skills"],
            "embedding": embedding
        })

    return jd_embeddings

#  Store embeddings in Qdrant
def store_embeddings_in_qdrant(jd_embeddings: list, batch_size=100):
    ensure_collection(vector_size=len(jd_embeddings[0]['embedding']))

    for i in tqdm(range(0, len(jd_embeddings), batch_size), desc="Uploading to Qdrant"):
        batch = jd_embeddings[i:i + batch_size]
        points = []

        for item in batch:
            text_hash = hash_to_uuid(item["title"] +item["skills"]+ item["description"])
            point = PointStruct(
                id=text_hash,
                vector=item["embedding"].tolist(),
                payload={
                    "title": item["title"],
                    "description": item["description"],
                    "skills": item["skills"],
                    "hash": text_hash
                }
            )
            points.append(point)

        if points:
            client.upsert(
                collection_name=QDRANT_COLLECTION,
                points=points
            )

    print("-> All embeddings stored in Qdrant.")

#  MAIN
if __name__ == "__main__":
    use_csv = False  # Change to False if you want to load from pickle
    if use_csv:
        csv_path = "./jobs.csvpath"  # Update this with your actual CSV file
        print(f"-> Reading jobs from CSV: {csv_path}")
        jd_embeddings = generate_embeddings_from_csv(csv_path)
    else:
        print("-> Loading precomputed embeddings from pickle")
        with open("NoteBooks/demo_embeddings.pkl", "rb") as f:
            jd_embeddings = pickle.load(f)

    store_embeddings_in_qdrant(jd_embeddings)
