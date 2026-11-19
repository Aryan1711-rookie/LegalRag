import hashlib
import logging

from pathlib import Path
from tempfile import NamedTemporaryFile

import pymupdf

from postgrest.exceptions import APIError

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    BackgroundTasks
)

from api.schema.document import DocumentAcceptedResponse
from api.dependencies.auth import get_current_user
from database.document_repository import DocumentRepository


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)

MAX_FILE_SIZE = 20 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024

logger = logging.getLogger(__name__)


# ==================================================
# Background document processing
# ==================================================

def process_document(
    ingestion_service,
    document_id: str,
    temp_path: str,
    title: str,
    file_name: str,
    user_id: str
):
    try:
        ingestion_service.ingest_pdf(
            pdf_path=temp_path,
            user_id=user_id,
            title=title,
            original_file_name=file_name,
            existing_document_id=document_id
        )

    except Exception:
        logger.exception(
            "Ingestion failed for document %s",
            document_id
        )

        try:
            repository = DocumentRepository()

            document = repository.get_document_for_user(
                document_id=document_id,
                user_id=user_id
            )

            if document and document["status"] == "processing":

                repository.update_document_progress(
                    document_id=document_id,
                    progress=document.get("progress") or 0,
                    processing_stage="failed",
                    status="failed",
                    error_message="Document processing failed."
                )

        except Exception:
            logger.exception(
                "Failed to update document status."
            )

    finally:
        try:
            Path(temp_path).unlink(missing_ok=True)

        except OSError:
            logger.exception(
                "Failed to delete temporary PDF."
            )


# ==================================================
# Upload document
# ==================================================

@router.post(
    "/upload",
    response_model=DocumentAcceptedResponse,
    status_code=202
)
def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    user=Depends(get_current_user)
):

    temp_path = None
    total_size = 0
    file_header = b""
    task_scheduled = False

    document_id = None
    repository = None

    # Initialize SHA-256 hasher
    file_hasher = hashlib.sha256()

    try:

        # 1. Validate file extension
        if (
            not file.filename
            or Path(file.filename).suffix.lower() != ".pdf"
        ):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported."
            )

        user_id = str(user.id)

        # 2. Save uploaded PDF and calculate hash
        with NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_path = Path(temp_file.name)

            while content := file.file.read(CHUNK_SIZE):

                total_size += len(content)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF file exceeds the 20 MB limit."
                    )

                # Calculate hash incrementally
                file_hasher.update(content)

                if len(file_header) < 5:
                    file_header += content[
                        :5 - len(file_header)
                    ]

                temp_file.write(content)

        # 3. Validate PDF
        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        if file_header != b"%PDF-":
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file."
            )

        # 4. Generate final SHA-256 hash
        file_hash = file_hasher.hexdigest()

        repository = DocumentRepository()

        # 5. Check for duplicate document
        existing_document = repository.get_document_by_hash(
            user_id=user_id,
            file_hash=file_hash
        )

        if existing_document:
            raise HTTPException(
                status_code=409,
                detail=(
                    "This document has already been uploaded."
                )
            )

        # 6. Get page count without OCR
        try:
            with pymupdf.open(str(temp_path)) as pdf:

                if pdf.needs_pass:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Password-protected PDFs "
                            "are not supported."
                        )
                    )

                total_pages = len(pdf)

        except HTTPException:
            raise

        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Unable to open PDF."
            )

        if total_pages == 0:
            raise HTTPException(
                status_code=400,
                detail="PDF contains no pages."
            )

        # 7. Create document record
        document_title = (
            title.strip()
            if title and title.strip()
            else Path(file.filename).stem
        )

        try:
            document = repository.create_document(
                title=document_title,
                file_name=file.filename,
                total_pages=total_pages,
                user_id=user_id,
                status="processing",
                file_hash=file_hash
            )

        except APIError as error:

            # Handle simultaneous duplicate uploads
            if error.code == "23505":

                duplicate = repository.get_document_by_hash(
                    user_id=user_id,
                    file_hash=file_hash
                )

                if duplicate:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "This document has already "
                            "been uploaded."
                        )
                    )

            raise

        document_id = document["id"]

        # 8. Initialize processing progress
        updated_document = (
            repository.update_document_progress(
                document_id=document_id,
                progress=5,
                processing_stage="uploaded",
                status="processing"
            )
        )

        if not updated_document:
            raise RuntimeError(
                "Unable to initialize document progress."
            )

        # 9. Schedule background ingestion
        background_tasks.add_task(
            process_document,
            ingestion_service=request.app.state.ingestion_service,
            document_id=document_id,
            temp_path=str(temp_path),
            title=document_title,
            file_name=file.filename,
            user_id=user_id
        )

        task_scheduled = True

        # 10. Return immediately
        return {
            "document_id": document_id,
            "title": document_title,
            "file_name": file.filename,
            "total_pages": total_pages,
            "status": "processing",
            "progress": 5,
            "processing_stage": "uploaded"
        }

    except HTTPException:
        raise

    except Exception:

        logger.exception("Document upload failed.")

        # Handle failures after document creation
        if document_id and repository and not task_scheduled:

            try:
                repository.update_document_progress(
                    document_id=document_id,
                    progress=0,
                    processing_stage="failed",
                    status="failed",
                    error_message=(
                        "Unable to start document processing."
                    )
                )

            except Exception:
                logger.exception(
                    "Failed to update document status."
                )

        raise HTTPException(
            status_code=500,
            detail="Unable to schedule document processing."
        )

    finally:

        # Background task owns the file once scheduled
        if temp_path and not task_scheduled:

            try:
                temp_path.unlink(missing_ok=True)

            except OSError:
                logger.exception(
                    "Failed to delete temporary PDF."
                )

        file.file.close()


# ==================================================
# List documents
# ==================================================

@router.get("/")
def list_documents(
    limit: int = 10,
    offset: int = 0,
    search: str | None = None,
    status: str | None = None,
    user=Depends(get_current_user)
):

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100."
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset cannot be negative."
        )

    if status and status not in {
        "processing",
        "completed",
        "failed"
    }:
        raise HTTPException(
            status_code=400,
            detail="Invalid document status."
        )

    repository = DocumentRepository()

    result = repository.get_documents_for_user(
        user_id=str(user.id),
        limit=limit,
        offset=offset,
        search=search,
        status=status
    )

    return {
        "total_documents": result["total_documents"],
        "limit": limit,
        "offset": offset,
        "search": search,
        "status": status,
        "documents": result["documents"]
    }


# ==================================================
# Get individual document
# ==================================================

@router.get("/{document_id}")
def get_document(
    document_id: str,
    user=Depends(get_current_user)
):

    repository = DocumentRepository()

    document = repository.get_document_for_user(
        document_id=document_id,
        user_id=str(user.id)
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return document


# ==================================================
# Delete document
# ==================================================

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    user=Depends(get_current_user)
):

    repository = DocumentRepository()

    document = repository.get_document_for_user(
        document_id=document_id,
        user_id=str(user.id)
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # Prevent deletion during active ingestion
    if document["status"] == "processing":
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete a document while "
                "it is being processed."
            )
        )

    deleted_document = repository.delete_document_for_user(
        document_id=document_id,
        user_id=str(user.id)
    )

    if not deleted_document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id
    }