import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "chat_history.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("Database initialized.")

def get_or_create_thread(thread_id: str, title: str = "New Chat"):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM threads WHERE id = ?", (thread_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute(
            "INSERT INTO threads (id, title) VALUES (?, ?)",
            (thread_id, title)
        )
        conn.commit()
        conn.close()
        return {"created": True, "id": thread_id}
    
    conn.close()
    return {"created": False, "id": thread_id}

def delete_empty_threads() -> int:
    """Delete threads with no messages."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM threads 
        WHERE id NOT IN (SELECT DISTINCT thread_id FROM messages)
    ''')
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted

def save_message(thread_id: str, role: str, content: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
        (thread_id, role, content)
    )
    cursor.execute(
        "UPDATE threads SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (thread_id,)
    )
    conn.commit()
    conn.close()

def get_messages(thread_id: str, limit: int = 100) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT role, content, created_at FROM messages WHERE thread_id = ? ORDER BY created_at ASC LIMIT ?",
        (thread_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [{"role": row["role"], "content": row["content"]} for row in rows]

def get_all_threads() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.id, t.title, t.created_at, t.updated_at, COUNT(m.id) as message_count
        FROM threads t
        LEFT JOIN messages m ON t.id = m.thread_id
        GROUP BY t.id
        ORDER BY t.updated_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "id": row["id"],
        "title": row["title"],
        "message_count": row["message_count"],
        "updated_at": row["updated_at"]
    } for row in rows]

def update_thread_title(thread_id: str, title: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE threads SET title = ? WHERE id = ?",
        (title, thread_id)
    )
    conn.commit()
    conn.close()