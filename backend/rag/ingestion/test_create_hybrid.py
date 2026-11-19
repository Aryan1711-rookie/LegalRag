import pymupdf

digital_path = (
    "rag/test/6.LANDMARK JUDGMENTS "
    "OF THE SUPREME COURT PLAIN.pdf"
)

output_path = "rag/test/hybrid_test.pdf"

with pymupdf.open(digital_path) as source:

    with pymupdf.open() as output:

        # Page 1: Digital PDF page
        output.insert_pdf(
            source,
            from_page=11,
            to_page=11
        )

        # Page 2: Scanned image
        page = output.new_page(
            width=448,
            height=697
        )

        page.insert_image(
            page.rect,
            filename="rag/test/4.png"
        )

        # Page 3: Another digital PDF page
        output.insert_pdf(
            source,
            from_page=13,
            to_page=13
        )

        output.save(output_path)

print(f"Hybrid PDF created: {output_path}")