from sentence_transformers import SentenceTransformer, util
from keybert import KeyBERT
model = SentenceTransformer("all-mpnet-base-v2")
import re

def embed_skills(skills):
    return model.encode(skills, convert_to_tensor=True)

kw_model = KeyBERT()

def extract_skills(text, top_n=10):
    """
    Extracts keywords from the given text using KeyBERT.
    Args:
        text (str): The text from which to extract keywords.
        top_n (int): The number of top keywords to extract. Default is 10.
    Returns:
        list: A list of extracted keywords.
    """
    if not text:
        return []
    # Ensure the text is a string
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")
    # If the text is empty, return an empty list
    if not text.strip():
        return []
    # Extract keywords using KeyBERT
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n)
    return list(set([kw[0] for kw in keywords]))

KNOWN_SKILLS = [
    'python', 'java', 'sql', 'tableau', 'power bi', 'aws', 'azure', 'gcp', 
    'docker', 'kubernetes', 'scrum', 'agile', 'jira', 'react', 'angular', 
    'vue', 'node.js', 'javascript', 'html', 'css', 'c#', '.net', 'spring', 
    'django', 'flask', 'git', 'jenkins', 'ci/cd', 'devops', 'machine learning',
    'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
    'data analysis', 'data visualization', 'product management', 'crm',
    # Programming Languages
    'python',
    'java',
    'javascript',
    'typescript',
    'sql',
    'c#',
    'c++',
    'go',
    'php',
    'ruby',
    'swift',
    'kotlin',
    'r',
    'scala',
    'rust',

    # Web Development & Frameworks
    'html',
    'css',

    'react',
    'angular',
    'vue.js',
    'node.js',
    'express.js',
    'django',
    'flask',
    'spring',
    'spring boot',
    '.net',
    'asp.net',
    'jquery',
    'rest api',
    'graphql',

    # Cloud & DevOps
    'aws',
    'azure',
    'gcp',
    'docker',
    'kubernetes',
    'terraform',
    'ansible',
    'jenkins',
    'git',
    'github',
    'gitlab',
    'ci/cd',
    'linux',
    'bash',
    'shell scripting',

    # Databases
    'mysql',
    'postgresql',
    'mongodb',
    'microsoft sql server',
    'oracle',
    'redis',
    'elasticsearch',
    'cassandra',

    # Data Science, ML & AI
    'machine learning',
    'deep learning',
    'generative ai',
    'llm',
    'natural language processing',
    'nlp',
    'pandas',
    'numpy',
    'scikit-learn',
    'tensorflow',
    'pytorch',
    'spark',
    'hadoop',
    'kafka',

    # BI & Data Visualization
    'tableau',
    'power bi',
    'qlik sense',
    'google data studio',
    'd3.js',

    # Project Management & Methodology
    'agile',
    'scrum',
    'kanban',
    'jira',
    'confluence',
    'project management',
    'product management',

    # Essential Soft Skills
    'communication',
    'leadership',
    'problem solving',
    'teamwork',

    'collaboration',
    'adaptability',
    'time management',
    'critical thinking',
    'stakeholder management'
]

def extract_skills_from_resume(resume_text: str) -> list:
    """
    Extracts known skills from resume text using direct matching.
    """
    if not isinstance(resume_text, str):
        return []

    # Normalize the resume text to lowercase for case-insensitive matching
    resume_text_lower = resume_text.lower()
    
    found_skills = set() # Use a set to automatically handle duplicates

    # Iterate through our list of known skills
    for skill in KNOWN_SKILLS:
        # Use regex with word boundaries (\b) to match whole words only
        # This prevents matching "java" in "javascript", for example.
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, resume_text_lower):
            found_skills.add(skill)
            
    return sorted(list(found_skills))


from sentence_transformers import util

# Assuming you have an 'embed_skills' function that calls model.encode()
# from your_embedding_module import embed_skills

def find_missing_skills_semantically(jd_skills, resume_skills, threshold=0.75):
    """
    Compares skills using a single, optimized matrix calculation.
    """
    if not resume_skills:
        return jd_skills # If resume has no skills, all JD skills are missing
    if not jd_skills:
        return [] # If JD has no skills, there's nothing to be missing

    # --- OPTIMIZATION 1: Get all embeddings at once ---
    jd_embeddings = embed_skills(jd_skills)
    resume_embeddings = embed_skills(resume_skills)

    # --- OPTIMIZATION 2: Compute the entire similarity matrix in one go ---
    # This creates a matrix where matrix[i][j] is the similarity
    # between jd_skills[i] and resume_skills[j].
    similarity_matrix = util.cos_sim(jd_embeddings, resume_embeddings)

    missing_skills = []
    # Now, loop through the pre-computed matrix
    for i in range(len(jd_skills)):
        # For the i-th JD skill, find its highest similarity score against all resume skills
        highest_similarity_score = similarity_matrix[i].max()
        
        # If even the best match is below the threshold, the skill is missing
        if highest_similarity_score < threshold:
            missing_skills.append(jd_skills[i])
            
    return missing_skills
