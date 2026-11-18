
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.rag_service import RAGService
from services.ingestion_service import IngestionService

from api.routes.chat import router as chat_router
from api.routes.documents import router as documents_router
from api.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize RAG components and load the embedding model
    app.state.rag_service = RAGService()

    # Reuse the embedding model already loaded by RAGService
    embedding_manager = (
        app.state.rag_service
        .retrieval_service
        .embedding_manager
    )

    # Initialize ingestion service
    app.state.ingestion_service = IngestionService(
        embedding_manager=embedding_manager
    )

    print("LegalMind AI services initialized.")

    yield

    # Application shutdown
    app.state.ingestion_service = None
    app.state.rag_service = None

    print("LegalMind AI shutting down.")


app = FastAPI(
    title="LegalMind AI",
    description="Legal Document RAG API",
    version="1.0.0",
    lifespan=lifespan
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LegalMind AI"
    }
    