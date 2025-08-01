"""
This module contains functions to match resumes to job descriptions using embeddings.
It uses cosine similarity to find the best matches based on the embeddings generated from the resume and job descriptions.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def match_resume_to_jd(resume_embedding, jd_embeddings):
    """
    Match resume embedding to job description embeddings using cosine similarity.
    
    """
    matches = []
    for jd in jd_embeddings:
        score = cosine_similarity([resume_embedding], [jd["embedding"]])[0][0]
        matches.append((jd, score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


# def match_resume_to_jd(resume_embedding, jd_embeddings):
#     matches = []

#     if not jd_embeddings:
#         print(" No job embeddings available.")
#         return []

    
#     # Ensure resume embedding is a 2D array: (1, 768)
#     resume_embedding = np.array(resume_embedding).reshape(1, -1)

#     print("Type of resume_embedding:", type(resume_embedding))
#     print("Resume embedding shape:", np.array(resume_embedding).shape)  

#     for jd in jd_embeddings:
#         jd_vec = np.array(jd["embedding"]).reshape(1, -1)
#         print("Type of jd['embedding']:", type(jd["embedding"]))
#         print("JD embedding shape:", np.array(jd["embedding"]).shape)
#         print("Type of jdvec:", type(jd_vec))
#         print("JDvec shape:", np.array(jd_vec).shape)
#         score = cosine_similarity(resume_embedding, jd_vec)[0][0]
#         matches.append((jd, score))
    
#     matches.sort(key=lambda x: x[1], reverse=True)
#     return matches