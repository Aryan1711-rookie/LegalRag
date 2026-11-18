
import re
import unicodedata


def normalize_text(text: str) -> str:
    """
    Normalize extracted PDF text while preserving
    paragraph boundaries and legal content.
    """

    # 1. Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # 2. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Remove null characters
    text = text.replace("\x00", "")

    # 4. Remove unwanted control characters
    text = "".join(
        char for char in text
        if char in "\n\t" or unicodedata.category(char)[0] != "C"
    )

    # 5. Join words broken by PDF line wrapping
    # Example: consti-\ntution -> constitution
    text = re.sub(
        r"(?<=[A-Za-z])-[ \t]*\n[ \t]*(?=[a-z])",
        "",
        text
    )

    # 6. Normalize horizontal whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # 7. Remove spaces around line breaks
    text = re.sub(r" *\n *", "\n", text)

    # 8. Preserve paragraph breaks, remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 9. Remove isolated trailing page number
    text = re.sub(r"\n\s*\d{1,3}\s*$", "", text)

    # 10. Preserve bullet-point boundaries
    text = re.sub(r"\n[ \t]*(?=[•–])", "\n\n", text)
    
    # 11. Convert single line breaks into spaces
    # Keep double line breaks as paragraph separators
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    return text.strip()
