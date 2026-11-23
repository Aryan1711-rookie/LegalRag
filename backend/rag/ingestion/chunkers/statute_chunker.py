from rag.ingestion.chunking import (
    join_lines,
    split_large_paragraph
)

from rag.ingestion.parsers.subsection_parser import (
    parse_subsections
)


def chunk_statute(
    sections: list,
    source: str,
    document_title: str,
    chunk_size: int = 450,
    overlap: int = 60,
    document_type: str = "act",
    max_subsection_characters: int = 1800
):

    if chunk_size <= 0:
        raise ValueError("Invalid chunk size.")

    if not 0 <= overlap < chunk_size:
        raise ValueError("Invalid overlap.")

    if max_subsection_characters <= overlap:
        raise ValueError("Invalid subsection character limit.")

    all_chunks = []
    counter = 1

    provision_label = (
        "Clause" if document_type == "bill"
        else "Section"
    )

    for section in sections:

        section_number = section["section_number"]
        section_title = section.get("section_title")
        chapter = section.get("chapter")

        subsections = parse_subsections(section)

        section_chunk_index = 1

        for subsection in subsections:

            subsection_number = subsection[
                "subsection_number"
            ]

            page_start = subsection["page_start"]
            page_end = subsection["page_end"]

            # 1. Preserve the complete subsection.
            text = join_lines([
                line.strip()
                for line in subsection["text"].splitlines()
                if line.strip()
            ])

            if not text:
                continue

            # 2. Build statutory context.
            context = [
                f"Document: {document_title}",
                f"{provision_label}: {section_number}"
            ]

            if subsection_number is not None:
                context.append(
                    f"Subsection: {subsection_number}"
                )

            if section_title:
                context.append(
                    f"Title: {section_title}"
                )

            if chapter:
                context.append(f"Chapter: {chapter}")

            header = "\n".join(context)

            # 3. Split only oversized subsections.
            if len(text) <= max_subsection_characters:

                pieces = [text]

            else:

                pieces = split_large_paragraph(
                    paragraph=text,
                    chunk_size=max_subsection_characters,
                    overlap=overlap
                )

            # 4. Build individual chunks.
            for piece_index, piece in enumerate(
                pieces,
                start=1
            ):

                retrieval_text = f"{header}\n\n{piece}"

                subsection_key = (
                    subsection_number
                    if subsection_number is not None
                    else "0"
                )

                all_chunks.append({
                    "chunk_id": f"chunk_{counter:05d}",

                    "text": piece,

                    "retrieval_text": retrieval_text,

                    "metadata": {
                        "source": source,
                        "document_title": document_title,
                        "document_type": document_type,

                        "chapter": chapter,

                        "section_number": section_number,
                        "section_title": section_title,

                        "subsection_number": subsection_number,

                        "page_number": page_start,

                        "page_start": page_start,
                        "page_end": page_end,

                        "section_page_start": section["page_start"],
                        "section_page_end": section["page_end"],

                        "subsection_part": piece_index,
                        "subsection_total_parts": len(pieces),

                        "case_name": None,

                        "context_line": header,

                        "chunk_key": (
                            f"s{section_number}"
                            f"_ss{subsection_key}"
                            f"_c{section_chunk_index:03d}"
                        )
                    }
                })

                counter += 1
                section_chunk_index += 1

    return all_chunks