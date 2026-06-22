import sys
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.vector_store import add_documents_to_store, PERSIST_DIR

CHUNKS_FILE = PROJECT_ROOT / "data" / "processed" / "all_chunks.json"

def main():
    print(f"📂 Project root: {PROJECT_ROOT}")
    print(f"📂 Chunks file: {CHUNKS_FILE}")
    print(f"📂 Vector store dir: {PERSIST_DIR}")

    # Delete existing store if present
    if PERSIST_DIR.exists() and any(PERSIST_DIR.iterdir()):
        print("⚠️ Vector store exists. Deleting...")
        shutil.rmtree(PERSIST_DIR)
        print("✅ Deleted.")

    if not CHUNKS_FILE.exists():
        print("❌ Chunks file not found.")
        return

    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    print(f"📄 Loaded {len(chunks)} chunks.")

    documents = []
    for item in chunks:
        doc = Document(
            page_content=item["chunk"],
            metadata={
                "url": item.get("url", ""),
                "title": item.get("title", "")
            }
        )
        documents.append(doc)

    print(f"📥 Adding {len(documents)} documents to vector store...")
    add_documents_to_store(documents)
    print("✅ Vector store created!")

if __name__ == "__main__":
    main()