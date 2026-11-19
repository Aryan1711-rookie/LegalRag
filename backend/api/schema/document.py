
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    title: str
    file_name: str
    total_pages: int
    total_chunks: int
    inserted_chunks: int
    status: str




class DocumentAcceptedResponse(BaseModel):
    document_id: str
    title: str
    file_name: str
    total_pages: int
    status: str
    progress: int
    processing_stage: str