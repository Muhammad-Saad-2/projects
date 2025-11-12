from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as rag_router
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="AI Research Assistant API",
    version="1.0.0",
    description="Backend API for research query and summarization using RAG architecture."
)

# CORS setup — useful for later Streamlit / frontend use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(rag_router, prefix="/api", tags=["RAG Service"])

@app.get("/")
async def root():
    return {"message": "AI Research Assistant API is running 🚀"}

