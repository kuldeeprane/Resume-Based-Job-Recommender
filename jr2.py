import streamlit as st
import os
import tempfile
from utils.parser import extract_text_from_pdf
from utils.embeddings import generate_embedding, store_embedding
from utils.semantic_skills import extract_skills, find_missing_skills_semantically
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

from utils.qdrant_client import client

# Setup
st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("Resume Matcher – Get Job Recommendations Instantly")

# Load model & Qdrant client
model = SentenceTransformer("all-mpnet-base-v2")
# qdrant = QdrantClient(path="./local_qdrant", prefer_grpc=True)
collection_name = "jds1"

# File upload
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    with st.spinner("Parsing your resume..."):
        resume_text = extract_text_from_pdf(file_path)

    os.remove(file_path)

    if resume_text:
        st.success("Resume parsed successfully!")
        st.text_area("Resume Text", resume_text, height=300)

        with st.spinner("Generating embedding and checking duplicates..."):
            success, resume_id = store_embedding(resume_text)

        if success:
            st.success("Resume embedding stored in vector DB!")
        else:
            st.warning("Duplicate resume detected. Using cached embedding.")

        resume_embedding = generate_embedding(resume_text)
        resume_vector = resume_embedding.tolist()

        # 🔍 Search jobs directly in Qdrant
        with st.spinner("Finding job matches..."):
            results = client.search(
                collection_name=collection_name,
                query_vector=resume_vector,
                limit=5
            )

        st.subheader("Top Job Recommendations")

        resume_skills = extract_skills(resume_text)

        for r in results:
            payload = r.payload
            jd_skills = [s.strip() for s in payload.get("skills", "").split(",")]
            missing_skills = find_missing_skills_semantically(jd_skills, resume_skills)

            st.markdown(f"**{payload.get('title', 'Unknown Job')}**")
            st.markdown(f"**Relevance Score**: `{round(r.score * 100, 2)}%`")
            st.markdown(f"**Missing Skills**: `{', '.join(missing_skills)}`")
            # st.markdown(f"**Job Description**: {payload.get('description', '')}")
            st.markdown(f"**Required Skills**: `{payload.get('skills', '')}`")
            st.markdown("---")
    else:
        st.error("Could not extract text from resume. Try a different file.")
else:
    st.info("Upload your resume to get started.")
