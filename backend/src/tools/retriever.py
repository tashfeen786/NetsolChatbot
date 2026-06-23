# src/tools/retriever.py
from langchain_core.tools import tool
from ..rag.vector_store import get_vector_store

@tool
def retrieve(query: str) -> str:
    """
    Retrieve relevant information from ALL uploaded documents (PDF, DOCX, TXT).
    Use this tool when the user asks about the content of any uploaded file.
    The system automatically finds the most relevant chunks across all files.
    """
    try:
        print(f"🔍 Retrieve tool called with query: '{query}'")  # Debug
        vector_store = get_vector_store()
        
        # 🔥 Sab files mein search karo, koi filter nahi
        docs = vector_store.similarity_search(query, k=8)
        print(f"🔍 Retrieved {len(docs)} chunks")
        
        if not docs:
            return "No relevant information found in the uploaded documents. Please upload a file or try a different question."
        
        # Results ko combine karo
        return "\n\n---\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        return f"Error retrieving documents: {str(e)}"