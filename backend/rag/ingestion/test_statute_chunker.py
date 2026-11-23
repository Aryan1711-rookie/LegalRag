import json

import pymupdf
from transformers import AutoTokenizer

from rag.ingestion.parsers.statute_parser import (
    parse_statute_pages
)

from rag.ingestion.chunkers.statute_chunker import (
    chunk_statute
)


def main():

    pdf_path = "rag/test/BNSS2023.pdf"

    pages = []

    with pymupdf.open(pdf_path) as pdf:

        for index in range(45, 262):

            pages.append({
                "page_number": index + 1,
                "text": pdf[index].get_text(
                    "text",
                    sort=True
                )
            })

    # Parse statute sections

    sections = parse_statute_pages(
        pages=pages,
        start_page=46,
        end_page=262,
        section_titles={
            "35": "When police may arrest without warrant",
            "36": "Procedure of arrest and duties of officer making arrest"
        }
    )

    # Generate chunks

    chunks = chunk_statute(
        sections=sections,
        source="BNSS2023.pdf",
        document_title="BNSS 2023",
        chunk_size=450,
        overlap=60
    )

    section_35_chunks = [
        chunk
        for chunk in chunks
        if chunk["metadata"]["section_number"] == "35"
    ]

    print("\n========== STATUTE CHUNKING ==========")

    print("Total sections:", len(sections))
    print("Total chunks:", len(chunks))
    print("Section 35 chunks:", len(section_35_chunks))

    print("\n========== SECTION 35 CHUNKS ==========")

    for chunk in section_35_chunks:

        print(
            json.dumps(
                chunk,
                indent=4,
                ensure_ascii=False
            )
        )

    # ==========================================
    # STRUCTURAL VALIDATION
    # ==========================================

    print("\n========== STRUCTURAL VALIDATION ==========")

    assert len(sections) == 531, (
        f"Expected 531 sections, got {len(sections)}."
    )

    assert chunks, "No chunks generated."

    assert section_35_chunks, (
        "No chunks found for Section 35."
    )

    assert all(
        "Section: 35" in chunk["retrieval_text"]
        for chunk in section_35_chunks
    ), "Section 35 retrieval prefix is missing."

    assert all(
        chunk["metadata"]["section_title"]
        == "When police may arrest without warrant"
        for chunk in section_35_chunks
    ), "Incorrect Section 35 title."

    assert all(
        len(chunk["text"]) <= 1800
        for chunk in chunks
    ), "Chunk exceeds maximum subsection size."

    assert all(
        chunk["metadata"]["page_number"] in {61, 62, 63}
        for chunk in section_35_chunks
    ), "Incorrect Section 35 page number."

    assert all(
        "Procedure of arrest and duties of officer making arrest"
        not in chunk["text"]
        for chunk in section_35_chunks
    ), "Section 36 content leaked into Section 35."

    assert len({
        chunk["chunk_id"]
        for chunk in chunks
    }) == len(chunks), "Duplicate chunk IDs detected."

    print("Structural validation passed.")

    # ==========================================
    # TOKEN LENGTH VALIDATION
    # ==========================================

    print("\n========== TOKEN LENGTH VALIDATION ==========")

    tokenizer = AutoTokenizer.from_pretrained(
        "BAAI/bge-base-en-v1.5"
    )

    max_tokens = 512

    token_lengths = []
    oversized_chunks = []

    for chunk in chunks:

        tokens = tokenizer.encode(
            chunk["retrieval_text"],
            add_special_tokens=True,
            truncation=False
        )

        token_count = len(tokens)

        token_lengths.append(token_count)

        if token_count > max_tokens:

            oversized_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "section": chunk["metadata"]["section_number"],
                "subsection": chunk["metadata"].get(
                    "subsection_number"
                ),
                "tokens": token_count
            })

    # Print statistics after processing ALL chunks

    print("Total chunks:", len(chunks))
    print("Minimum tokens:", min(token_lengths))
    print("Maximum tokens:", max(token_lengths))

    print(
        "Average tokens:",
        round(sum(token_lengths) / len(token_lengths), 2)
    )

    print("Model token limit:", max_tokens)
    print("Oversized chunks:", len(oversized_chunks))

    if oversized_chunks:

        print("\nOversized chunk details:")

        for chunk in oversized_chunks:

            print(
                json.dumps(
                    chunk,
                    indent=4,
                    ensure_ascii=False
                )
            )

    assert not oversized_chunks, (
        f"{len(oversized_chunks)} chunks exceed "
        "the embedding model's token limit."
    )

    print("\nToken validation passed.")
    print("\nAll tests passed.")


if __name__ == "__main__":
    main()