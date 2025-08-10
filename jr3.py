import streamlit as st
import os
import tempfile
from sentence_transformers import SentenceTransformer


# --- Assume your utility functions are in their respective files ---
from utils.parser import extract_text_from_pdf
from utils.embeddings import generate_embedding
from utils.semantic_skills import find_missing_skills_semantically, extract_skills_from_resume
from utils.description_format import format_job_description
from utils.qdrant_client import client

# client = QdrantClient(
#     url=st.secrets["QDRANT_URL"],
#     api_key=st.secrets["QDRANT_API_KEY"],
# )

# ====================================================================
# 1. HELPER FUNCTION DEFINITION
# ====================================================================
def process_resume_and_display_results(file_path, collection_name):
    """
    Takes a file path, processes the resume, and displays job matches.
    """
    with st.spinner("Parsing your resume..."):
        resume_text = extract_text_from_pdf(file_path)

    if resume_text:
        st.success("Resume parsed successfully!")
        st.text_area("Parsed Resume Text", resume_text, height=200)

        with st.spinner("Finding job matches..."):
            resume_embedding = generate_embedding(resume_text)
            resume_vector = resume_embedding.tolist()

            results = client.search(
                collection_name=collection_name,
                query_vector=resume_vector,
                limit=5
            )

        st.subheader("Top Job Recommendations")
        extracted_skills = extract_skills_from_resume(resume_text)
        resume_skills = [skill.lower() for skill in extracted_skills]
        string_resume_skills = ', '.join(resume_skills)

        for r in results:
            payload = r.payload
            title = payload.get('title', 'Unknown Job').title()
            job_url = payload.get('jdUrl', '')
            
            if job_url:
                st.markdown(f"**[{title}]({job_url})**")
            else:
                st.markdown(f"**{title}**")

            st.markdown(f"**Relevance Score**: `{round(r.score * 100, 2)}%`")
            
            # --- UI IMPROVEMENT: All details are now inside the expander ---
            with st.expander("View Details & Skills Analysis"):
                
                # --- BUG FIX: Use 'description' key, not 'fjd' ---
                description_text = payload.get('fjd', 'No description available.')
                formatted_description = format_job_description(description_text)
                st.markdown("#### Full Job Description")
                st.markdown(formatted_description, unsafe_allow_html=True)
                st.markdown("---")

                st.markdown("#### Skills Analysis")
                jd_skills = [s.strip().lower() for s in payload.get("skills", "").split(",") if s]
                missing_skills = find_missing_skills_semantically(jd_skills, resume_skills)
                
                st.markdown(f"**Resume Skills**: `{string_resume_skills}`")
                st.markdown(f"**Required Skills**: `{payload.get('skills', '')}`")
                st.markdown(f"**Missing Skills**: `{', '.join(missing_skills) if missing_skills else 'None! All skills seem to match.'}`")
                st.markdown(f"**Hash**: `{payload.get('hash', '')}`")

            st.markdown("---") # Separator for the next job
    else:
        st.error("Could not extract text from resume. Try a different file.")

# ====================================================================
# 2. MAIN APPLICATION SETUP (Done only ONCE)
# ====================================================================
st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("Resume Matcher – Get Job Recommendations Instantly")

# This part is for caching the model loading, making the app faster on rerun.
# The model is loaded only once.
@st.cache_resource
def load_model():
    return SentenceTransformer("all-mpnet-base-v2")

model = load_model()
collection_name = "jds1"

# ====================================================================
# 3. UI and PROCESSING LOGIC
# ====================================================================

# --- OPTION 1: UPLOAD RESUME ---
st.subheader("Option 1: Upload Your Resume")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"], label_visibility="collapsed")

# --- OPTION 2: SELECT A SAMPLE RESUME ---
st.subheader("Option 2: Use a Sample Resume")

SAMPLE_RESUME_DIR = "sample_resumes"
try:
    sample_files = ["Choose a sample..."] + os.listdir(SAMPLE_RESUME_DIR)
except FileNotFoundError:
    sample_files = ["Choose a sample..."]
    st.warning(f"'{SAMPLE_RESUME_DIR}' folder not found. Please create it to use sample resumes.")

selected_resume = st.selectbox("Select a sample resume to test the app:", sample_files, label_visibility="collapsed")

# --- Trigger the processing ---
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        file_path = tmp.name
    
    process_resume_and_display_results(file_path, collection_name)
    os.remove(file_path)

elif selected_resume != "Choose a sample...":
    file_path = os.path.join(SAMPLE_RESUME_DIR, selected_resume)
    process_resume_and_display_results(file_path, collection_name)

else:
    st.info("Upload your resume or select a sample to get started.")