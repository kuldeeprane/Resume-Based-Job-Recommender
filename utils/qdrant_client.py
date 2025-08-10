from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
# Local (embedded) Qdrant – NO DOCKER NEEDED
client = QdrantClient(
    path="./local_qdrant",  # Saves db files in this folder
    prefer_grpc=True
)

client = QdrantClient(
    url=st.secrets["QDRANT_URL"],
    api_key=st.secrets["QDRANT_API_KEY"],
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
