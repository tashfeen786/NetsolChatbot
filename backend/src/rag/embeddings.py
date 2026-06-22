from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def get_embeddings():
    global _model
    if _model is None:
        print("🔄 Loading embedding model (SentenceTransformer)...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded!")
    return _model

def embed_query(text):
    model = get_embeddings()
    return model.encode(text).tolist()

def embed_documents(texts):
    model = get_embeddings()
    return model.encode(texts).tolist()