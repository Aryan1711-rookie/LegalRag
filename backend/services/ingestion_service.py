
from pathlib import Path

from rag.ingestion.parser import extract_text
from rag.ingestion.normalize import normalize_text
from rag.ingestion.chunking import chunk_pages
from database.document_repository import DocumentRepository


class IngestionService:

    def __init__(self, embedding_manager):
        self.embedding_manager = embedding_manager
        self.document_repository = DocumentRepository()

    
    def ingest_pdf(
        self,
        pdf_path: str,
        user_id: str,
        title: str | None = None,
        original_file_name: str | None = None,
        chunk_size: int = 450,
        overlap: int = 60
    ):

        pdf_path = Path(pdf_path)
        file_name = original_file_name or pdf_path.name
        document_title = title or Path(file_name).stem

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")

        # 1. Extract text
        pages = extract_text(str(pdf_path))

        if not pages:
            raise ValueError("No pages found in the PDF.")

        # 2. Normalize text
        normalized_pages = []

        for page in pages:
            clean_text = normalize_text(page["text"])

            normalized_pages.append({
                "page_number": page["page_number"],
                "text": clean_text
            })

        # 3. Validate content
        if not any(page["text"].strip() for page in normalized_pages):
            raise ValueError("No readable text found in the PDF.")

        # 4. Generate chunks
        chunks = chunk_pages(
            normalized_pages,
            chunk_size=chunk_size,
            overlap=overlap,
            source=file_name,
            document_title=document_title
        )

        if not chunks:
            raise ValueError("Chunking produced no chunks.")

        # 5. Generate embeddings
        texts = [chunk["retrieval_text"] for chunk in chunks]
        embeddings = self.embedding_manager.generate_embeddings(texts)

        if len(embeddings) != len(chunks):
            raise ValueError("Embedding count does not match chunk count.")

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        # 6. Create document with processing status
        document = self.document_repository.create_document(
            title=document_title,
            file_name=file_name,
            total_pages=len(pages),
            user_id=user_id,
            file_path=None,
            status="processing"
        )

        document_id = document["id"]

        # 7. Insert chunks and update lifecycle status
        try:
            inserted_count = self.document_repository.insert_chunks(
                document_id=document_id,
                chunks=chunks
            )

            if inserted_count != len(chunks):
                raise RuntimeError(
                    f"Expected {len(chunks)} chunks, "
                    f"inserted {inserted_count}."
                )

            self.document_repository.update_document_status(
                document_id=document_id,
                status="completed"
            )

        except Exception:
            try:
                self.document_repository.update_document_status(
                    document_id=document_id,
                    status="failed"
                )
            except Exception as status_error:
                print(
                    f"WARNING: Could not mark document "
                    f"{document_id} as failed: {status_error}"
                )

            try:
                self.document_repository.delete_document(document_id)
            except Exception as cleanup_error:
                print(
                    f"WARNING: Document rollback failed for "
                    f"{document_id}: {cleanup_error}"
                )

            raise

        # 8. Return ingestion summary
        return {
            "document_id": document_id,
            "title": document["title"],
            "file_name": document["file_name"],
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "inserted_chunks": inserted_count,
            "status": "completed"
        }
