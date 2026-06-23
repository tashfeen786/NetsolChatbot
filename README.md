# 🤖 NetsolChatbot

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
├── .gitignore # Excludes secrets, builds, etc.
└── README.md # You are here

text

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 16+
- Git

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/tashfeen786/NetsolChatbot.git
cd NetsolChatbot
2️⃣ Backend Setup
bash
cd chatbot-langgraph
python -m venv venv
source venv/bin/activate      # Linux/Mac
# or .\venv\Scripts\activate  # Windows
pip install -r requirements.txt
Create .env file in chatbot-langgraph/:

env
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CSE_ID=your_google_search_engine_id
GOOGLE_CALENDAR_CREDENTIALS=path/to/calendar-credentials.json
DATABASE_URL=sqlite:///../data/chat.db
Run the backend:

bash
python run.py
# Server runs on http://localhost:8000
3️⃣ Frontend Setup
bash
cd ../frontend
npm install
Create .env.local in frontend/:

env
VITE_API_URL=http://localhost:8000
Start the frontend:

bash
npm run dev
# App runs on http://localhost:5173
🌐 API Endpoints
Method	Endpoint	Description
GET	/api/threads	List all chat threads
POST	/api/threads	Create a new thread
GET	/api/threads/{id}/messages	Get messages for a thread
POST	/api/chat	Send a message (streaming SSE)
POST	/api/upload	Upload a file (PDF/DOCX/TXT)
🧪 Usage Examples
💬 Normal Chat
text
User: How many customers do we have?
Assistant: We have 127 customers in our database.
📄 RAG (Uploaded File)
Click the 📎 button and upload a PDF.

Ask: Summarise the main points from the uploaded file.

📊 Chart Query
text
User: Show total revenue by city as a bar chart.
Assistant: [Bar chart rendered with revenue per city]
📅 Calendar
text
User: What meetings do I have today?
Assistant: You have a team sync at 10:00 AM and a client call at 2:30 PM.
🌐 Web Search
text
User: Search for latest news about AI in Pakistan.
Assistant: [Summarised news with sources]
🧠 How It Works (High‑Level)
User message → Frontend sends to /api/chat.

LangGraph agent analyses intent and decides which tool(s) to call:

query_business_database → SQLite → returns data → may generate chart JSON.

search_google → Google Custom Search → returns summaries.

calendar_tool → Google Calendar API → returns events.

Retrieval tool → vector search → returns context.

Final response (with optional <chart_data> tag) is streamed back.

Frontend parses chart tags and renders interactive charts using recharts.

🔐 Security Notes
All sensitive credentials are stored in .env files and excluded from version control.

Google Service Account JSON keys are also ignored (*.json).

User‑uploaded files are stored in uploads/ (ignored) and purged after processing.

🛠️ Troubleshooting
503 Service Unavailable → Gemini API rate limit; retry after a few seconds.

Repository not found during push → Ensure GitHub repo is created before pushing.

Frontend blank screen → Check console for errors; ensure recharts is installed.

🚀 Deployment (Suggested)
Backend: Use Railway or Render – set environment variables via their dashboard.

Frontend: Deploy on Vercel or Netlify – set VITE_API_URL to your deployed backend URL.

🤝 Contributing
Fork the repo.

Create a feature branch: git checkout -b feature/amazing

Commit changes: git commit -m 'Add amazing feature'

Push: git push origin feature/amazing

Open a Pull Request.

📄 License
This project is open‑source and available under the MIT License.

🙏 Acknowledgements
LangChain / LangGraph

Google Gemini API

Recharts

Tailwind CSS

📬 Contact
Author: Tashfeen
GitHub: tashfeen786
Project Link: https://github.com/tashfeen786/NetsolChatbot
