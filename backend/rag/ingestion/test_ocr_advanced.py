
from pathlib import Path
from time import perf_counter

from PIL import Image

from rag.ingestion.loaders.image_loader import ImageLoader


IMAGE_PATH = Path(
    r"D:\LegalRag\backend\rag\test\3.jpg"
)

METHODS = [
    "baseline",
    "deskew",
    "clahe",
    "sharpen",
    "combined",
]

loader = ImageLoader(
    file_path=str(IMAGE_PATH),
    languages="hin+eng",
    config="--oem 3 --psm 6"
)

for method in METHODS:

    print("\n" + "=" * 75)
    print(f"PREPROCESSING: {method.upper()}")
    print("=" * 75)

    start = perf_counter()

    with Image.open(IMAGE_PATH) as original:

        if method == "baseline":
            processed = loader._preprocess_image(original)
        else:
            processed = loader._preprocess_advanced(
                original,
                method
            )

        text, confidence = loader._extract_ocr(processed)

    elapsed = perf_counter() - start

    print(f"Confidence: {confidence}")
    print(f"Execution time: {elapsed:.2f} seconds")
    print("\nExtracted text:\n")
    print(text)
