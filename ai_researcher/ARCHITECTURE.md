
# High Level Systsem Architecture

 ┌─────────────────────────────┐
 │         Frontend (UI)       │
 │ Streamlit Dashboard          │
 │ ─ Search Papers              │
 │ ─ View Summaries             │
 │ ─ Ask Research Questions     │
 └──────────────┬──────────────┘
                │ REST API calls
 ┌──────────────┴──────────────┐
 │        API Gateway           │  ← (optional central router)
 └──────────────┬──────────────┘
                │
 ┌──────────────┼──────────────┐
 │              │              │
 ▼              ▼              ▼
📚 Paper Fetcher   🧠 Summarizer   🔍 RAG Q/A
FastAPI Service    FastAPI Service FastAPI Service
arXiv/Semantic     LangChain +     FAISS + Sentence
Scholar API        Local LLM       Transformers








User → LangChain Router
          ↓
     Vector DB Search
          ↓
    ┌──────────────┬──────────────┐
    │  Found       │   Not Found  │
    ↓              ↓
Gemini Answer   Arxiv API Search
    ↓              ↓
  Return     → Gemini Summarize
                ↓
            Store in Vector DB
                ↓
           Return to User



# The project structure

ai_research_assistant/
│
├── 📄 README.md
├── 📄 requirements.txt
├── 📄 .env
├── 📄 config.yaml
│
├── 📂 app/
│   ├── __init__.py
│   │
│   ├── main.py                     # Gateway / central FastAPI router
│   ├── routes.py                   # API endpoints
│   ├── schemas.py                  # Pydantic models for requests/responses
│   ├── dependencies.py             # Dependency injections (DB, services)
│   │
│   ├── 📂 services/
│   │   ├── __init__.py
│   │   ├── paper_fetcher.py        # Calls Arxiv API & formats paper data
│   │   ├── summarizer.py           # Uses LangChain + Gemini for summarization
│   │   ├── rag_service.py          # Handles embedding, retrieval, and vector store ops
│   │   └── fallback_handler.py     # Handles “no data found” logic
│   │
│   ├── 📂 core/
│   │   ├── __init__.py
│   │   ├── embeddings.py           # SentenceTransformer or OpenAI embeddings setup
│   │   ├── llm.py                  # Gemini API wrapper (via LangChain)
│   │   ├── vector_store.py         # FAISS / Chroma setup & CRUD methods
│   │   └── config_loader.py        # Load .env / YAML configs safely
│   │
│   ├── 📂 utils/
│   │   ├── __init__.py
│   │   ├── logger.py               # Unified logging utility
│   │   ├── text_cleaner.py         # Cleans abstracts before summarization
│   │   └── response_formatter.py   # Formats model output for display or storage
│   │
│   ├── 📂 tests/
│   │   ├── test_rag_service.py
│   │   ├── test_arxiv_fetch.py
│   │   └── test_gemini_summary.py
│   │
│   └── 📂 data/
│       ├── vector_store/           # Stores FAISS / Chroma index files
│       ├── paper_cache.json        # Optional local metadata cache
│       └── query_logs.json         # Log of previous user queries
│
├── 📂 frontend/
│   ├── streamlit_app.py            # Streamlit dashboard (later stage)
│   └── assets/
│       ├── styles.css
│       └── icons/
│
└── 📂 docker/
    ├── Dockerfile.api              # For FastAPI services
    ├── Dockerfile.frontend         # For Streamlit app
    └── docker-compose.yml          # Multi-service orchestration
