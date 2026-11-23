
from pydantic import BaseModel, Field
from uuid import UUID


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        title="Question",
        min_length=3,
        max_length=2000,
        description="The question to be answered by the RAG system."
    )

    document_id: UUID = Field(
        ...,
        description="ID of the document to search within."
    )

    chat_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID. Omit to create a new chat."
    )


class ChatResponse(BaseModel):
    chat_id: UUID
    question: str
    answer: str
    model: str
    sources: list[dict]
    citation_report: dict
    grounding_report: dict
    performance: dict = Field(default_factory=dict)

    
class ChatSaveRequest(BaseModel):
    is_saved: bool


class ChatSaveResponse(BaseModel):
    id: UUID
    title: str
    is_saved: bool