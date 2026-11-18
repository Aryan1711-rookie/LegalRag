
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile
)

from api.schema.document import DocumentUploadResponse
from api.dependencies.auth import get_current_user
from database.document_repository import DocumentRepository


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
CHUNK_SIZE = 1024 * 1024          # 1 MB


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(
    request: Request,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    user=Depends(get_current_user)
):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    temp_path = None
    total_size = 0
    file_header = b""

    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_path = Path(temp_file.name)

            while content := file.file.read(CHUNK_SIZE):

                total_size += len(content)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF file exceeds the 20 MB limit."
                    )

                if len(file_header) < 5:
                    file_header += content[:5 - len(file_header)]

                temp_file.write(content)

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

        ingestion_service = request.app.state.ingestion_service

        result = ingestion_service.ingest_pdf(
            pdf_path=str(temp_path),
            title=title or Path(file.filename).stem,
            original_file_name=file.filename,
            user_id=str(user.id)
        )

        return result

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        print(f"Document Upload Error: {e}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the PDF."
        )

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

        file.file.close()




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

    if status and status not in {"processing", "completed", "failed"}:
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


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    user=Depends(get_current_user)
):
    repository = DocumentRepository()

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
