
import pymupdf


def extract_text(pdf_path: str):
    doc = pymupdf.open(pdf_path)

    extracted_pages = []

    for page_num, page in enumerate(doc):

        text = page.get_text("text", sort=True)

        extracted_pages.append({
            "page_number": page_num + 1,
            "text": text
        })

    doc.close()

    return extracted_pages

############# Testing the code ######################


# pdf_path = r"D:\LegalRag\backend\rag\test\6.LANDMARK JUDGMENTS OF THE SUPREME COURT PLAIN.pdf"

# doc = pymupdf.open(pdf_path)

# page = doc[11]  # Page 12 (index starts from 0)

# # Approach 1: Default extraction
# text_default = page.get_text("text")

# # Approach 2: Sorted extraction
# text_sorted = page.get_text("text", sort=True)

# # Approach 3: Block-based extraction
# blocks = page.get_text("blocks", sort=True)

# print("\n========== DEFAULT EXTRACTION ==========")
# print(text_default)

# print("\n========== SORTED EXTRACTION ==========")
# print(text_sorted)

# print("\n========== BLOCK EXTRACTION ==========")

# for block in blocks:
#     print(block[4])
#     print("-" * 50)

# doc.close()