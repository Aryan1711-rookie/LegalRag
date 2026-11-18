
from pathlib import Path

from rag.ingestion.parser import extract_text
from rag.ingestion.chunking import chunk_pages
from rag.ingestion.normalize import normalize_text

PDF_PATH = Path(
    "rag/test/6.LANDMARK JUDGMENTS OF THE SUPREME COURT PLAIN.pdf"
)

CHUNK_SIZE = 450
OVERLAP = 60

# 1. Extract PDF
pages = extract_text(str(PDF_PATH))

# 2. Normalize extracted pages
for page in pages:
    page["text"] = normalize_text(page["text"])

# 3. Chunk pages
chunks = chunk_pages(
    pages=pages,
    chunk_size=CHUNK_SIZE,
    overlap=OVERLAP,
    source=PDF_PATH.name,
    document_title="Landmark Judgments of the Supreme Court of India",
    case_names={
        14: "Minerva Mills v. Union of India"
    }
)

# 4. Print statistics
lengths = [len(chunk["text"]) for chunk in chunks]

print("\n========== CHUNKING STATISTICS ==========")
print("Total pages:", len(pages))
print("Total chunks:", len(chunks))
print("Minimum length:", min(lengths, default=0))
print("Maximum length:", max(lengths, default=0))
print(
    "Average length:",
    round(sum(lengths) / len(lengths), 2) if lengths else 0
)

# 5. Inspect selected chunks
target_ids = {
    "chunk_00026",
    "chunk_00027",
    "chunk_00028",
    "chunk_00029",
    "chunk_00030",
    "chunk_00031",
}

for chunk in chunks:
    if chunk["chunk_id"] in target_ids:
        print("\n" + "=" * 80)
        print("CHUNK:", chunk["chunk_id"])
        print("METADATA:", chunk["metadata"])
        print("\nORIGINAL CONTENT:")
        print(chunk["text"])
        print("\nRETRIEVAL TEXT:")
        print(chunk["retrieval_text"])

# 6. Check size violations
print("\n========== VALIDATION ==========")

oversized = [
    chunk for chunk in chunks
    if len(chunk["text"]) > CHUNK_SIZE
]

missing_retrieval_text = [
    chunk for chunk in chunks
    if not chunk.get("retrieval_text")
]

print("Oversized original chunks:", len(oversized))
print("Missing retrieval text:", len(missing_retrieval_text))

for chunk in oversized:
    print(
        chunk["chunk_id"],
        "Length:",
        len(chunk["text"])
    )
