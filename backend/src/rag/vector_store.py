from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from .embeddings import embed_query, embed_documents

class SentenceTransformerEmbedding(Embeddings):
    def embed_query(self, text):
        return embed_query(text)
    
    def embed_documents(self, texts):
        return embed_documents(texts)

PROJECT_ROOT = Path(__file__).parent.parent.parent
PERSIST_DIR = PROJECT_ROOT / "data" / "chromadb"
PERSIST_DIR.mkdir(parents=True, exist_ok=True)

_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = SentenceTransformerEmbedding()
        _vector_store = Chroma(
            persist_directory=str(PERSIST_DIR),
            embedding_function=embeddings,
            collection_name="netsol_docs"
        )
    return _vector_store

def add_documents_to_store(documents):
    vector_store = get_vector_store()
    ids = vector_store.add_documents(documents)
    return ids