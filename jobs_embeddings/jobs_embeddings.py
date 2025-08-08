import hashlib
import pickle
import pandas as pd
import torch
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

# ---------------- Setup ----------------
QDRANT_COLLECTION = "jds1"
PICKLE_FILE_PATH = "NoteBooks/job_embeddings.pkl" # <<< UPDATE THIS IF NEEDED

# client = QdrantClient(
#     path="local_qdrant",      # for local run
#     prefer_grpc=True
# )

client = QdrantClient(
    url="https://39956cec-f784-48b6-bb33-95fb804da005.eu-central-1-0.aws.cloud.qdrant.io", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.yn4xkHmrSJtmPVh4ketUXUHFP5JXs1EqDlvRUHi-uM0",       # for storing embeddings in online qdrant cluster
    timeout=60
)

# Hash generator
def hash_to_uuid(text: str):
    return hashlib.md5(text.encode()).hexdigest()

# Ensure Qdrant collection exists
def ensure_collection(vector_size: int):
    # Check vector_size to handle potential empty data
    if not vector_size:
        raise ValueError("Cannot create collection, vector size is zero. Your data might be empty.")
        
    if not client.collection_exists(collection_name=QDRANT_COLLECTION):
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"-> Collection '{QDRANT_COLLECTION}' created.")
    else:
        print(f"-> Collection '{QDRANT_COLLECTION}' already exists.")

# Function to store embeddings from a DataFrame into Qdrant
def store_embeddings_in_qdrant(df: pd.DataFrame, batch_size=50):
    # Determine vector size from the first embedding
    vector_size = len(df.iloc[0]['embedding']) if not df.empty else 0
    ensure_collection(vector_size=vector_size)

    for i in tqdm(range(0, len(df), batch_size), desc="Uploading to Qdrant"):
        batch_df = df.iloc[i:i + batch_size]
        points = []

        for _, row in batch_df.iterrows():
            text_hash = hash_to_uuid(row["combined_text"])
            
            point = PointStruct(
                id=text_hash,
                vector=row["embedding"].tolist(),
                payload={
                    "title": row["title"],
                    "description": row["description"],
                    "skills": row["skills"],
                    "jdUrl": row.get("jdUrl", ""),  # Safely get jdUrl, default to empty
                    "fjd": row.get("formatjd"),
                    "hash": text_hash
                }
            )
            points.append(point)

        if points:
            client.upsert(
                collection_name=QDRANT_COLLECTION,
                points=points,
                wait=False
            )

    print("-> All embeddings stored in Qdrant.")

# MAIN
if __name__ == "__main__":
    # 1. Load the pre-computed embeddings from your pickle file
    print(f"-> Loading precomputed embeddings from: {PICKLE_FILE_PATH}")
    with open(PICKLE_FILE_PATH, "rb") as f:
        jd_embeddings_from_pickle = pickle.load(f)

    # 2. Convert the list of dictionaries into a pandas DataFrame
    print("-> Converting loaded data to DataFrame...")
    jobs_df = pd.DataFrame(jd_embeddings_from_pickle)

    if not jobs_df.empty:
        # 3. Prepare DataFrame for upload by creating the 'combined_text' field
        # This is needed to generate a consistent hash for the Qdrant Point ID.
        jobs_df['combined_text'] = (
            jobs_df['title'].fillna('') + ' ' +
            jobs_df['skills'].fillna('') + ' ' +
            jobs_df['description'].fillna('')
        )
        
        # 4. Call the function to store the data in Qdrant
        store_embeddings_in_qdrant(jobs_df)
    else:
        print("-> The pickle file is empty or contains no data. Nothing to do.")