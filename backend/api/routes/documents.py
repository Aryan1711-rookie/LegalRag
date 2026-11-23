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
from database.storage_repository import StorageRepository
from workers.tasks import ingest_document

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

# def process_document(
#     ingestion_service,
#     document_id: str,
#     temp_path: str,
#     title: str,
#     file_name: str,
#     user_id: str
# ):
#     try:
#         ingestion_service.ingest_pdf(
#             pdf_path=temp_path,
#             user_id=user_id,
#             title=title,
#             original_file_name=file_name,
#             existing_document_id=document_id
#         )

#     except Exception:
#         logger.exception(
#             "Ingestion failed for document %s",
#             document_id
#         )

#         try:
#             repository = DocumentRepository()

#             document = repository.get_document_for_user(
#                 document_id=document_id,
#                 user_id=user_id
#             )

#             if document and document["status"] == "processing":

#                 repository.update_document_progress(
#                     document_id=document_id,
#                     progress=document.get("progress") or 0,
#                     processing_stage="failed",
#                     status="failed",
#                     error_message="Document processing failed."
#                 )

#         except Exception:
#             logger.exception(
#                 "Failed to update document status."
#             )

#     finally:
#         try:
#             Path(temp_path).unlink(missing_ok=True)

#         except OSError:
#             logger.exception(
#                 "Failed to delete temporary PDF."
#             )


# ==================================================
# Upload document
# ==================================================

@router.post(
    "/upload",
    response_model=DocumentAcceptedResponse,
    status_code=202
)
def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    user=Depends(get_current_user)
):

    temp_path = None
    total_size = 0
    file_header = b""

    document_id = None
    repository = None

    publish_attempted = False

    file_hasher = hashlib.sha256()

    try:

        # 1. Validate file extension

        allowed_extensions = {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg"
        }

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required."
            )

        extension = Path(file.filename).suffix.lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, PNG and JPEG files are supported."
            )

        user_id = str(user.id)

        # 2. Save temporary file and calculate hash

        with NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_path = Path(temp_file.name)

            while content := file.file.read(CHUNK_SIZE):

                total_size += len(content)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 20 MB limit."
                    )

                file_hasher.update(content)

                if len(file_header) < 8:
                    file_header += content[
                        :8 - len(file_header)
                    ]

                temp_file.write(content)

        # 3. Validate file content

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        if extension == ".pdf":
            valid_file = file_header.startswith(b"%PDF-")

        elif extension == ".png":
            valid_file = file_header.startswith(
                b"\x89PNG\r\n\x1a\n"
            )

        elif extension in {".jpg", ".jpeg"}:
            valid_file = file_header.startswith(
                b"\xff\xd8\xff"
            )

        else:
            valid_file = False

        if not valid_file:
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted file."
            )

        # 4. Check duplicate document

        file_hash = file_hasher.hexdigest()

        repository = DocumentRepository()

        existing_document = repository.get_document_by_hash(
            user_id=user_id,
            file_hash=file_hash
        )

        if existing_document:
            raise HTTPException(
                status_code=409,
                detail="This document has already been uploaded."
            )

        # 5. Determine page count

        if extension == ".pdf":

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

        else:
            total_pages = 1

        if total_pages == 0:
            raise HTTPException(
                status_code=400,
                detail="Document contains no pages."
            )

        # 6. Create document record

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
                status="queued",
                file_hash=file_hash
            )

        except APIError as error:

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

        # 7. Upload original file to Supabase Storage

        storage_repository = StorageRepository()

        object_path = storage_repository.upload_document(
            file_path=str(temp_path),
            user_id=user_id,
            document_id=document_id
        )

        # 8. Store object path in database

        updated_document = (
            repository.update_document_file_path(
                document_id=document_id,
                user_id=user_id,
                file_path=object_path
            )
        )

        if not updated_document:
            raise RuntimeError(
                "Unable to save document storage path."
            )

        # 9. Initialize processing progress

        updated_document = (
            repository.update_document_progress(
                document_id=document_id,
                progress=5,
                processing_stage="uploaded",
                status="queued"
            )
        )

        if not updated_document:
            raise RuntimeError(
                "Unable to initialize document progress."
            )

        # 10. Submit ingestion task to Celery

        publish_attempted = True

        task = ingest_document.delay(document_id)

        logger.info(
            "Ingestion task %s submitted for document %s",
            task.id,
            document_id
        )

        # 11. Return immediately

        return {
            "document_id": document_id,
            "title": document_title,
            "file_name": file.filename,
            "total_pages": total_pages,
            "status": "queued",
            "progress": 5,
            "processing_stage": "uploaded"
        }

    except HTTPException:
        raise

    except Exception:

        logger.exception("Document upload failed.")

        # Only mark failed if task publication has not
        # been attempted. A broker error can be ambiguous.

        if document_id and repository and not publish_attempted:

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

        if publish_attempted:
            raise HTTPException(
                status_code=503,
                detail="Unable to confirm task submission."
            )

        raise HTTPException(
            status_code=500,
            detail="Unable to schedule document processing."
        )

    finally:

        # Celery downloads from Storage.
        # The API no longer needs its temporary file.

        if temp_path:

            try:
                temp_path.unlink(missing_ok=True)

            except OSError:
                logger.exception(
                    "Failed to delete temporary file."
                )

        file.file.close()

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
        "queued",
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

    user_id = str(user.id)

    document = repository.get_document_for_user(
        document_id=document_id,
        user_id=user_id
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    if document["status"] in {"queued", "processing"}:

        raise HTTPException(
            status_code=409,
            detail="Cannot delete a queued or processing document."
        )

    # Delete the stored original, if present.

    if document.get("file_path"):

        storage = StorageRepository()

        extension = Path(
            document["file_name"]
        ).suffix.lower()

        expected_path = storage.build_object_path(
            user_id=user_id,
            document_id=document_id,
            extension=extension
        )

        if document["file_path"] != expected_path:
            raise HTTPException(
                status_code=409,
                detail="Unexpected document storage path."
            )

        try:

            storage.delete_document(
                user_id=user_id,
                document_id=document_id,
                extension=extension
            )

        except Exception:
            logger.exception(
                "Document storage deletion failed."
            )

            raise HTTPException(
                status_code=500,
                detail="Unable to delete stored document."
            )

    deleted_document = (
        repository.delete_document_for_user(
            document_id=document_id,
            user_id=user_id
        )
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