import time
from pathlib import Path

import pymupdf

from rag.ingestion.parser import extract_text
from rag.ingestion.normalize import normalize_text
from rag.ingestion.chunking import chunk_pages
from database.document_repository import DocumentRepository
from services.ingestion_stages import (
    IngestionStage,
    STAGE_PROGRESS
)


class IngestionService:

    def __init__(self, embedding_manager):
        self.embedding_manager = embedding_manager
        self.document_repository = DocumentRepository()

    def _update_progress(
        self,
        document_id: str,
        stage: IngestionStage
    ):
        self.document_repository.update_document_progress(
            document_id=document_id,
            progress=STAGE_PROGRESS[stage],
            processing_stage=stage.value,
            status=(
                "completed"
                if stage == IngestionStage.COMPLETED
                else "processing"
            )
        )

    def ingest_pdf(
        self,
        pdf_path: str,
        user_id: str,
        title: str | None = None,
        original_file_name: str | None = None,
        chunk_size: int = 450,
        overlap: int = 60,
        existing_document_id: str | None = None
    ):

        total_start = time.perf_counter()
        performance = {}

        pdf_path = Path(pdf_path)
        file_name = original_file_name or pdf_path.name
        document_title = title or Path(file_name).stem

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported."
            )

        # 1. Determine page count without performing OCR
        with pymupdf.open(str(pdf_path)) as pdf:
            total_pages = len(pdf)

        if total_pages == 0:
            raise ValueError("PDF contains no pages.")

        # 2. Create document BEFORE processing
        if existing_document_id:
            document_id = existing_document_id
        else:
            document = self.document_repository.create_document(
            title=document_title,
            file_name=file_name,
            total_pages=total_pages,
            user_id=user_id,
            file_path=None,
            status="processing"
        )

            document_id = document["id"]

        current_stage = IngestionStage.UPLOADED

        try:
            self._update_progress(
                document_id,
                current_stage
            )

            # 3. PDF parsing
            current_stage = IngestionStage.PARSING

            self._update_progress(
                document_id,
                current_stage
            )

            start = time.perf_counter()

            pages = extract_text(str(pdf_path))

            performance["parsing_seconds"] = round(
                time.perf_counter() - start, 4
            )

            if not pages:
                raise ValueError(
                    "No pages found in the PDF."
                )

            # 4. Normalization
            current_stage = IngestionStage.NORMALIZING

            self._update_progress(
                document_id,
                current_stage
            )

            start = time.perf_counter()

            normalized_pages = []

            for page in pages:
                normalized_pages.append({
                    **page,
                    "text": normalize_text(page["text"])
                })

            performance["normalization_seconds"] = round(
                time.perf_counter() - start, 4
            )

            if not any(
                page["text"].strip()
                for page in normalized_pages
            ):
                raise ValueError(
                    "No readable text found in the PDF."
                )

            # 5. Chunking
            current_stage = IngestionStage.CHUNKING

            self._update_progress(
                document_id,
                current_stage
            )

            start = time.perf_counter()

            chunks = chunk_pages(
                normalized_pages,
                chunk_size=chunk_size,
                overlap=overlap,
                source=file_name,
                document_title=document_title
            )

            performance["chunking_seconds"] = round(
                time.perf_counter() - start, 4
            )

            if not chunks:
                raise ValueError(
                    "Chunking produced no chunks."
                )

            # 6. Embedding generation
            current_stage = IngestionStage.EMBEDDING

            self._update_progress(
                document_id,
                current_stage
            )

            start = time.perf_counter()

            texts = [
                chunk["retrieval_text"]
                for chunk in chunks
            ]

            embeddings = (
                self.embedding_manager.generate_embeddings(
                    texts
                )
            )

            if len(embeddings) != len(chunks):
                raise ValueError(
                    "Embedding count does not match chunk count."
                )

            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding

            performance["embedding_seconds"] = round(
                time.perf_counter() - start, 4
            )

            # 7. Database indexing
            current_stage = IngestionStage.INDEXING

            self._update_progress(
                document_id,
                current_stage
            )

            start = time.perf_counter()

            inserted_count = (
                self.document_repository.insert_chunks(
                    document_id=document_id,
                    chunks=chunks
                )
            )

            if inserted_count != len(chunks):
                raise RuntimeError(
                    f"Expected {len(chunks)} chunks, "
                    f"inserted {inserted_count}."
                )

            performance["database_seconds"] = round(
                time.perf_counter() - start, 4
            )

            # 8. Mark document as completed
            self._update_progress(
                document_id,
                IngestionStage.COMPLETED
            )

        except Exception as error:

            try:
                self.document_repository.update_document_progress(
                    document_id=document_id,
                    progress=STAGE_PROGRESS[current_stage],
                    processing_stage="failed",
                    status="failed",
                    error_message=(
                        f"Document processing failed during "
                        f"{current_stage.value}."
                    )
                )

            except Exception as status_error:
                print(
                    f"WARNING: Failed to update document "
                    f"status: {status_error}"
                )

            print(
                f"Ingestion failed for {document_id}: {error}"
            )

            raise

        performance["total_seconds"] = round(
            time.perf_counter() - total_start,
            4
        )

        # 9. Performance report
        print("\n========== INGESTION PERFORMANCE ==========")
        print("Document:", document_title)
        print("Total pages:", total_pages)
        print("Total chunks:", len(chunks))

        for stage, duration in performance.items():
            print(f"{stage}: {duration:.4f}s")

        # 10. Return ingestion summary
        return {
            "document_id": document_id,
            "title": document_title,
            "file_name": file_name,
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "inserted_chunks": inserted_count,
            "status": "completed",
            "progress": 100,
            "processing_stage": "completed",
            "performance": performance
        }