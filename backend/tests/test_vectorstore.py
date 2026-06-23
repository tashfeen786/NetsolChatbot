# test_vectorstore.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.rag.vector_store import get_vector_store

vs = get_vector_store()
# Check how many documents
try:
    # Chroma doesn't have a direct count easily, but we can try to get all
    # Or just check if the collection exists
    print("✅ Vector store loaded successfully")
    print(f"📁 Persist directory: {vs._persist_directory}")
    # Try a test query
    result = vs.similarity_search("test", k=1)
    print(f"📄 Found {len(result)} documents for 'test'")
    if result:
        print(f"📄 Sample: {result[0].page_content[:100]}...")
except Exception as e:
    print(f"❌ Error: {e}")