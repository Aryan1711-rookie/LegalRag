import os
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from services.rag_service import RAGService
from services.ingestion_service import IngestionService

from api.routes.chat import router as chat_router
from api.routes.documents import router as documents_router
from api.routes.auth import router as auth_router
from api.routes.web_research import router as web_research_router

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.ready = False

    try:

        logger.info("Initializing LegalMind AI services.")

        app.state.rag_service = RAGService()

        embedding_manager = (
            app.state.rag_service
            .retrieval_service
            .embedding_manager
        )

        app.state.ingestion_service = IngestionService(
            embedding_manager=embedding_manager
        )

        app.state.ready = True

        logger.info("LegalMind AI services initialized.")

        yield

    finally:

        app.state.ready = False

        app.state.ingestion_service = None
        app.state.rag_service = None

        logger.info("LegalMind AI shutting down.")


app = FastAPI(
    title="LegalMind AI",
    description="Legal Document RAG API",
    version="1.0.0",
    lifespan=lifespan
)


# Environment-based CORS configuration

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers

app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(auth_router)
app.include_router(web_research_router)


# Liveness endpoint

@app.get("/health/live", tags=["Health"])
def liveness_check():

    return {
        "status": "alive",
        "service": "LegalMind AI"
    }


# Readiness endpoint

@app.get("/health/ready", tags=["Health"])
@app.get("/health", tags=["Health"])
def readiness_check(request: Request):

    if not getattr(request.app.state, "ready", False):

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "LegalMind AI"
            }
        )

    return {
        "status": "ready",
        "service": "LegalMind AI",
        "version": "1.0.0"
    }