import logging
import time

from pathlib import Path
from tempfile import TemporaryDirectory
from functools import lru_cache

from workers.celery_app import celery_app

import sys


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_ingestion_service():

    from rag.embeddings.embedding_manager import EmbeddingManager
    from services.ingestion_service import IngestionService

    embedding_manager = EmbeddingManager()

    return IngestionService(
        embedding_manager=embedding_manager
    )


@celery_app.task(name="legalmind.test_worker")
def test_worker():

    time.sleep(5)

    return {
        "status": "success",
        "message": "LegalMind worker is working!"
    }


@celery_app.task(name="legalmind.ingest_document")
def ingest_document(document_id: str):

    from database.document_repository import DocumentRepository
    from database.storage_repository import StorageRepository

    repository = DocumentRepository()

    document = repository.claim_document(document_id)

    if not document:

        logger.info(
            "Document %s is not available for processing.",
            document_id
        )

        return {
            "document_id": document_id,
            "status": "skipped"
        }

    logger.info(
        "Document %s claimed successfully.",
        document_id
    )
    try:
        storage = StorageRepository()

        user_id = document["user_id"]
        file_name = document["file_name"]
        title = document["title"]

        extension = Path(file_name).suffix.lower()

        with TemporaryDirectory() as temp_dir:

            destination = (
                Path(temp_dir) / f"original{extension}"
            )

            storage.download_document(
                user_id=user_id,
                document_id=document_id,
                extension=extension,
                destination=str(destination)
            )

            ingestion_service = get_ingestion_service()

            result = ingestion_service.ingest_pdf(
                pdf_path=str(destination),
                user_id=user_id,
                title=title,
                original_file_name=file_name,
                existing_document_id=document_id
            )

        return {
            "document_id": document_id,
            "status": "completed",
            "total_chunks": result["total_chunks"]
        }

    except Exception:

        logger.exception(
            "Ingestion failed for document %s",
            document_id
        )

        try:
            repository.update_document_status(
                document_id=document_id,
                status="failed"
            )

        except Exception:
            logger.exception(
                "Unable to update status for document %s",
                document_id
            )

        raise