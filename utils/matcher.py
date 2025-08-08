"""
This module contains functions to match resumes to job descriptions using embeddings.
It uses cosine similarity to find the best matches based on the embeddings generated from the resume and job descriptions.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
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

def match_resume_to_jd_optimized(resume_embedding, jd_embeddings):
    """
    Efficiently matches a resume to jobs using a single matrix operation.
    """
    # 1. Extract all job embeddings into a single list.
    # This prepares the data for a bulk calculation.
    jd_embedding_matrix = [jd["embedding"] for jd in jd_embeddings]

    # 2. Calculate all similarity scores in one go.
    # This is much faster than looping. The result is a 2D array like [[s1, s2, s3, ...]].
    all_scores = cosine_similarity([resume_embedding], jd_embedding_matrix)

    # 3. Pair the original job data with the calculated scores.
    # all_scores[0] gets the actual list of scores.
    matches = list(zip(jd_embeddings, all_scores[0]))
    
    # 4. Sort the matches by score in descending order.
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches

