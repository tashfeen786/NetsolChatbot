# NetsolChatbot

> An intelligent, multi‑tool AI assistant built with LangGraph, Gemini, and React.  
> Supports RAG (PDF/DOCX/TXT), live Google Search, Google Calendar, and business data queries with interactive charts.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash_Lite-purple.svg)](https://deepmind.google/technologies/gemini/)

---

## 🚀 Features

- 🧠 **LangGraph Agent** – tool‑calling with memory and streaming.
- 📄 **RAG (Retrieval‑Augmented Generation)** – upload PDF, DOCX, or TXT files, ask questions based on their content.
- 📊 **Business Database** – query SQLite with natural language and visualise results using **bar, pie, and line charts** (recharts).
- 🌐 **Google Search** – get up‑to‑date information from the web.
- 📅 **Google Calendar** – check meetings and events directly.
- 🔄 **Streaming Responses** – real‑time token‑by‑token output.
- 💬 **Chat History** – persistent threads with sidebar navigation.
- 🛡️ **Secure** – API keys and credentials never exposed (`.gitignore` applied).

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.10+, FastAPI, LangGraph, LangChain, Sentence‑Transformers, Google‑GenerativeAI |
| **Frontend** | React 18, Vite, Tailwind CSS, recharts, Lucide‑React |
| **Database** | SQLite (local) + Chroma vector store |
| **APIs** | Google Gemini 2.5 Flash‑Lite, Google Calendar, Google Search (Custom Search JSON API) |
| **Deployment** | Ready for Docker / Vercel (frontend) & Railway / Render (backend) |

---

## 📁 Project Structure
NetsolChatbot/
├── chatbot-langgraph/ # Backend (FastAPI + LangGraph)
│ ├── app/ # Core logic (agents, tools, routers)
│ ├── uploads/ # Temporary file storage (ignored)
│ ├── .env # Environment variables (ignored)
│ └── run.py # Entry point
├── frontend/ # React + Vite frontend
│ ├── src/
│ ├── public/
│ ├── .env.local # Frontend env (ignored)
│ └── package.json
├── data/ # SQLite DB & vector store (ignored)
├── .gitignore 
└── README.md 
---
## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 16+
- Git
- (Optional) Docker

###  Clone the Repository
```bash
git clone https://github.com/tashfeen786/NetsolChatbot.git
cd NetsolChatbot

## Backend Setup
cd chatbot-langgraph
python -m venv venv
source venv/bin/activate      # Linux/Mac
# or .\venv\Scripts\activate  # Windows
pip install -r requirements.txt
