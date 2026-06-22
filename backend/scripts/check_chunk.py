import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.vector_store import get_vector_store

def main():
    store = get_vector_store()
    # Try to get by metadata URL
    results = store.get(where={"url": "https://netsoltech.com/about-us/modern-slavery-act"})
    print(f"Found {len(results['ids'])} chunks for URL: https://netsoltech.com/about-us/modern-slavery-act")
    if results['ids']:
        for i, doc in enumerate(results['documents']):
            print(f"\n--- Chunk {i+1} ---")
            print(doc[:300])
    else:
        # If not found, search by metadata title
        results2 = store.get(where={"title": "Modern Slavery Act Statement | NETSOL Technologies"})
        print(f"Found by title: {len(results2['ids'])} chunks")
        if results2['ids']:
            for i, doc in enumerate(results2['documents']):
                print(f"\n--- Chunk {i+1} ---")
                print(doc[:300])

if __name__ == "__main__":
    main()