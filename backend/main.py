import logging
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🔄 Pre-loading embedding model in main thread (before LLM client)...")
from src.rag.embeddings import embed_query
embed_query("warmup")
logger.info("✅ Embedding model pre-loaded and ready")

from src.graph import build_graph
from src.database import (
    init_db, get_or_create_thread, save_message,
    get_messages, get_all_threads, update_thread_title,
    delete_empty_threads
)
from src.utils.helpers import generate_title
from src.rag.document_loader import process_uploaded_file
from src.rag.vector_store import add_documents_to_store
from langchain_core.messages import BaseMessage

app = FastAPI(title="Netsol Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_FILE_SIZE_MB = 10

@app.on_event("startup")
async def startup_event():
    init_db()
    deleted = delete_empty_threads()
    if deleted > 0:
        logger.info(f"Cleaned up {deleted} empty threads on startup")

class ChatRequest(BaseModel):
    message: str
    thread_id: str

class NewThreadRequest(BaseModel):
    title: str = "New Chat"

def _extract_text_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text")
                if text:
                    parts.append(text)
        return "".join(parts)
    return ""

@app.get("/api/threads")
async def threads():
    return get_all_threads()

@app.get("/api/threads/{thread_id}/messages")
async def thread_messages(thread_id: str):
    msgs = get_messages(thread_id)
    return {"messages": msgs}

@app.post("/api/threads")
async def create_thread(request: NewThreadRequest):
    thread_id = str(uuid.uuid4())
    get_or_create_thread(thread_id, request.title)
    return {"id": thread_id, "title": request.title}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return {"error": f"Unsupported file type: .{ext}. Allowed: pdf, docx, txt"}

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        return {"error": f"File too large. Max size is {MAX_FILE_SIZE_MB}MB."}

    try:
        documents = process_uploaded_file(file.filename, file_bytes)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        return {"error": "Failed to process file."}

    ids = add_documents_to_store(documents)
    logger.info(f"Uploaded '{file.filename}' — {len(documents)} chunks added to vector store")
    return {
        "filename": file.filename,
        "chunks_added": len(documents),
        "message": f"'{file.filename}' has been added to the knowledge base."
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    thread_id = request.thread_id
    user_message = request.message
    config = {"configurable": {"thread_id": thread_id}}
    input_state = {"messages": [{"role": "user", "content": user_message}]}

    get_or_create_thread(thread_id)
    save_message(thread_id, "user", user_message)

    msgs = get_messages(thread_id)
    if len(msgs) == 1:
        title = generate_title(user_message)
        update_thread_title(thread_id, title)

    logger.info(f"Message: {user_message}, Thread: {thread_id}")

    async def event_generator():
        full_response = ""
        try:
            async for update in graph.astream(input_state, config, stream_mode="updates"):
                for node_name, node_output in update.items():
                    if node_name == "llm":
                        messages = node_output.get("messages", [])
                        if messages:
                            last_msg = messages[-1]
                            if hasattr(last_msg, 'type') and last_msg.type == 'ai':
                                chunk = _extract_text_content(last_msg.content)
                            elif isinstance(last_msg, dict) and last_msg.get('role') == 'assistant':
                                chunk = _extract_text_content(last_msg.get('content', ''))
                            else:
                                continue
                            if chunk:
                                full_response += chunk
                                yield chunk
            if full_response:
                save_message(thread_id, "assistant", full_response)
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            yield f"Error: {str(e)}"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/")
async def root():
    return {"message": "Netsol Chat API is running"}