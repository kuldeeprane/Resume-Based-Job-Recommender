from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
import os
from dotenv import load_dotenv

load_dotenv()
# Local (embedded) Qdrant – NO DOCKER NEEDED
client = QdrantClient(
    path="./local_qdrant",  # Saves db files in this folder
    prefer_grpc=True
)

print(client.get_collections())

def create_collection():
    client.recreate_collection(
        collection_name="resumes",
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),  # Fixed vector size
    )

try:
    client.get_collection(collection_name="resumes")
except Exception:
    create_collection()
