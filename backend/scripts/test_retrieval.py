import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.vector_store import get_vector_store

def main():
    store = get_vector_store()
    query = "who is the CEO of Netsol"
    docs = store.similarity_search(query, k=5)
    print(f"Retrieved {len(docs)} docs:")
    for i, doc in enumerate(docs):
        print(f"\n--- Doc {i+1} ---")
        print(doc.page_content[:300])
        print(f"Metadata: {doc.metadata}")

if __name__ == "__main__":
    main()