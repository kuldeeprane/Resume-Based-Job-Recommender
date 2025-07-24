import pickle
import os

path = os.path.join("NoteBooks", "demo_embeddings.pkl")
    
with open(path, "rb") as f:
    jd_embeddings = pickle.load(f)

# print(embeddings[0])
print("Type of jd['embedding']:", type(jd_embeddings[1]["embedding"]))
print("JD embedding shape:", jd_embeddings[1]["embedding"].shape)
