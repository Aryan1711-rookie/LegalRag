import logging

from rag.ingestion.chunking import chunk_pages

from rag.ingestion.parsers.statute_layout import (
    detect_statute_layout
)

from rag.ingestion.parsers.statute_index import (
    extract_section_titles
)

from rag.ingestion.parsers.statute_parser import (
    parse_statute_pages
)

from rag.ingestion.chunkers.statute_chunker import (
    chunk_statute
)


logger = logging.getLogger(__name__)


def route_chunking(
    pages: list,
    normalized_pages: list,
    document_type: str,
    source: str,
    document_title: str,
    chunk_size: int = 450,
    overlap: int = 60
):

    def general_chunking():

        return chunk_pages(
            pages=normalized_pages,
            chunk_size=chunk_size,
            overlap=overlap,
            source=source,
            document_title=document_title
        )

    # Non-statutory documents
    if document_type not in {"act", "bill"}:

        logger.info("Using general chunking.")

        return general_chunking()

    # Use native text because this is the extraction
    # format validated by our statute parser tests.
    statute_pages = [
        {
            "page_number": page["page_number"],
            "text": page["text"]
        }
        for page in pages
    ]

    layout = detect_statute_layout(statute_pages)

    if not layout:

        logger.warning(
            "Unsupported statute layout. "
            "Using general chunking."
        )

        return general_chunking()

    logger.info("Detected statute layout: %s", layout)

    section_titles = extract_section_titles(
        pages=statute_pages,
        start_page=layout["index_start"],
        end_page=layout["index_end"]
    )

    sections = parse_statute_pages(
        pages=statute_pages,
        start_page=layout["body_start"],
        end_page=layout["body_end"],
        section_titles=section_titles
    )

    parsed_numbers = [
        section["section_number"]
        for section in sections
    ]

    # Validate section coverage against the index
    if (
        not section_titles
        or not sections
        or parsed_numbers != list(section_titles)
    ):

        logger.warning(
            "Statute validation failed. "
            "Using general chunking."
        )

        return general_chunking()

    statute_chunks = chunk_statute(
        sections=sections,
        source=source,
        document_title=document_title,
        chunk_size=chunk_size,
        overlap=overlap,
        document_type=document_type
    )

    if not statute_chunks:
        return general_chunking()

    # Preserve indexes, comparison tables, schedules
    # and introductory material.
    remaining_pages = [
        page
        for page in normalized_pages
        if not (
            layout["body_start"]
            < page["page_number"]
            <= layout["body_end"]
        )
    ]

    additional_chunks = chunk_pages(
        pages=remaining_pages,
        chunk_size=chunk_size,
        overlap=overlap,
        source=source,
        document_title=document_title
    )

    chunks = statute_chunks + additional_chunks

    # Ensure globally unique chunk IDs
    for index, chunk in enumerate(chunks, start=1):

        chunk["chunk_id"] = f"chunk_{index:05d}"

    logger.info(
        "Statute sections: %s | Statute chunks: %s "
        "| Additional chunks: %s",
        len(sections),
        len(statute_chunks),
        len(additional_chunks)
    )

    return chunks