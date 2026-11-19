from pathlib import Path
from time import perf_counter

from rag.ingestion.loaders.image_loader import ImageLoader


IMAGE_PATH = Path(
    r"D:\LegalRag\backend\rag\test\3.jpg"
)

METHODS = [
    "baseline",
    "otsu",
    "adaptive",
    "denoise_otsu",
]

for method in METHODS:

    print("\n" + "=" * 75)
    print(f"PREPROCESSING: {method.upper()}")
    print("=" * 75)

    loader = ImageLoader(
        file_path=str(IMAGE_PATH),
        languages="hin+eng",
        config="--oem 3 --psm 6"
    )

    start = perf_counter()

    with __import__("PIL").Image.open(IMAGE_PATH) as original:
        if method == "baseline":
            processed = loader._preprocess_image(original)
        else:
            processed = loader._preprocess_opencv(
                original,
                method
            )

        text, confidence = loader._extract_ocr(processed)

    elapsed = perf_counter() - start

    print(f"Confidence: {confidence}")
    print(f"Execution time: {elapsed:.2f} seconds")
    print("\nExtracted text:\n")
    print(text)