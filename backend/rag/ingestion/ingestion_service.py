
from rag.ingestion.parser import extract_text
from rag.ingestion.normalize import normalize_text
from rag.ingestion.chunking import chunk_pages
from rag.embeddings.embedding_manager import EmbeddingManager


pdf_path = r"D:\LegalRag\backend\rag\test\6.LANDMARK JUDGMENTS OF THE SUPREME COURT PLAIN.pdf"


# 1. Extract PDF text
pages = extract_text(pdf_path)


# 2. Normalize extracted text
normalized_pages = []

for page in pages:
    clean_text = normalize_text(page["text"])

    normalized_pages.append({
        "page_number": page["page_number"],
        "text": clean_text
    })

    print(f"\nPAGE {page['page_number']}")
    print(clean_text)
    print("=" * 80)


# 3. Chunk the normalized pages
chunks = chunk_pages(
    normalized_pages,
    chunk_size=450,
    overlap=60,
    source="LANDMARK JUDGMENTS OF THE SUPREME COURT.pdf"
)


# 4. Check chunk statistics
oversized = [
    chunk for chunk in chunks
    if len(chunk["text"]) > 450
]

sizes = [len(chunk["text"]) for chunk in chunks]

print("\n========== CHUNK STATISTICS ==========")
print("Total pages:", len(normalized_pages))
print("Total chunks:", len(chunks))
print("Oversized chunks:", len(oversized))
print("Minimum chunk size:", min(sizes) if sizes else 0)
print("Maximum chunk size:", max(sizes) if sizes else 0)
print(
    "Average chunk size:",
    round(sum(sizes) / len(sizes), 2) if sizes else 0
)


# 5. Inspect oversized chunks
for chunk in oversized:
    print("\nOVERSIZED CHUNK:", chunk["chunk_id"])
    print("Length:", len(chunk["text"]))
    print(chunk["text"])
    print("-" * 80)


# 6. Inspect the first 10 chunks
print("\n========== FIRST 10 CHUNKS ==========")

for chunk in chunks[:10]:
    print("\nChunk ID:", chunk["chunk_id"])
    print("Page:", chunk["metadata"]["page_number"])
    print("Length:", len(chunk["text"]))
    print(chunk["text"])
    print("-" * 80)


# 7. Initialize embedding manager
manager = EmbeddingManager()


# 8. Test embedding generation with one sample
sample_text = (
    "The Supreme Court held that the basic structure "
    "of the Constitution cannot be abrogated."
)

sample_embedding = manager.generate_embedding(sample_text)

print("\n========== EMBEDDING TEST ==========")
print("Dimensions:", len(sample_embedding))
print("First 5 values:", sample_embedding[:5])


# 9. Generate embeddings for all chunks
def embed_chunks(chunks: list):
    texts = [chunk["retrieval_text"] for chunk in chunks]

    embeddings = manager.generate_embeddings(texts)

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding

    return chunks


embedded_chunks = embed_chunks(chunks)


# 10. Verify embedded chunks
print("\n========== EMBEDDING RESULTS ==========")
print("Total embedded chunks:", len(embedded_chunks))

if embedded_chunks:
    print(
        "Embedding dimensions:",
        len(embedded_chunks[0]["embedding"])
    )

    print("First chunk ID:", embedded_chunks[0]["chunk_id"])
    print(
        "First chunk embedding:",
        embedded_chunks[0]["embedding"][:5]
    )
