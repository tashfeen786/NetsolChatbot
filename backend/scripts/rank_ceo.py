import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.vector_store import get_vector_store

def main():
    print("🔍 Testing vector store retrieval...")
    try:
        store = get_vector_store()
        query = "who is the CEO of Netsol"
        docs_with_scores = store.similarity_search_with_score(query, k=20)
        
        print(f"\n✅ Retrieved {len(docs_with_scores)} docs")
        print("\n--- Top 5 results ---")
        for i, (doc, score) in enumerate(docs_with_scores[:5]):
            print(f"{i+1}. Score: {score:.4f}")
            print(f"   URL: {doc.metadata.get('url', 'N/A')}")
            print(f"   Preview: {doc.page_content[:150]}...")
            print()
        
        # Check if CEO chunk 
        found_ceo = False
        for i, (doc, score) in enumerate(docs_with_scores):
            if "Najeeb" in doc.page_content or "CEO" in doc.page_content.upper():
                print(f"✅ CEO chunk found at rank {i+1} with score {score:.4f}")
                print(f"   URL: {doc.metadata.get('url', 'N/A')}")
                print(f"   Preview: {doc.page_content[:200]}...")
                found_ceo = True
                break
        
        if not found_ceo:
            print("\n❌ CEO chunk NOT found in top 20 results.")
            print("   Try increasing k in retriever.py")
            
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
    