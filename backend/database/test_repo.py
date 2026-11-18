
from database.document_repository import DocumentRepository

# Import your existing ingestion pipeline
from rag.ingestion.parser import extract_text
from rag.ingestion.normalize import normalize_text
from rag.ingestion.chunking import chunk_pages
from rag.embeddings.embedding_manager import EmbeddingManager
import time

start_time = time.perf_counter()

PDF_PATH = (
    r"D:\LegalRag\backend\rag\test"
    r"\6.LANDMARK JUDGMENTS OF THE SUPREME COURT PLAIN.pdf"
)


# 1. Extract PDF
pages = extract_text(PDF_PATH)


# 2. Normalize
normalized_pages = []

for page in pages:
    normalized_pages.append({
        "page_number": page["page_number"],
        "text": normalize_text(page["text"])
    })


# 3. Chunk
chunks = chunk_pages(
    normalized_pages,
    chunk_size=450,
    overlap=60,
    source="6.LANDMARK JUDGMENTS OF THE SUPREME COURT PLAIN.pdf",
    document_title="Landmark Judgments of the Supreme Court of India",
    case_names={
        14: "Minerva Mills v. Union of India"
    }
)


# 4. Generate embeddings
manager = EmbeddingManager()

#texts = [chunk["text"] for chunk in chunks]
texts = [chunk["retrieval_text"] for chunk in chunks]
embeddings = manager.generate_embeddings(texts)

for chunk, embedding in zip(chunks, embeddings):
    chunk["embedding"] = embedding


# 5. Initialize repository
repository = DocumentRepository()


# 6. Insert document
document = repository.create_document(
    title="Landmark Judgments of the Supreme Court of India",
    file_name="LANDMARK JUDGMENTS OF THE SUPREME COURT.pdf",
    total_pages=len(pages),
    file_path=PDF_PATH
)

print("Document inserted:", document["id"])


# 7. Insert chunks
inserted = repository.insert_chunks(
    document_id=document["id"],
    chunks=chunks
)

end_time = time.perf_counter() 
total_time = end_time - start_time
print("Total chunks inserted:", inserted)
print(f"Total insertion time: {total_time:.2f} seconds")
if inserted:
    print(f"Average time per chunk: {total_time / inserted:.4f} seconds")
else:
    print("No chunks inserted.")

