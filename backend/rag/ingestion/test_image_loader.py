from pathlib import Path

from rag.ingestion.loaders.image_loader import ImageLoader

IMAGE_PATH = Path(
    r"D:\LegalRag\backend\rag\test\5.png"
)

configs = {
    "PSM 3 - Automatic segmentation": "--oem 3 --psm 3",
    "PSM 6 - Uniform text block": "--oem 3 --psm 6",
}

for name, config in configs.items():

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    loader = ImageLoader(
        file_path=str(IMAGE_PATH),
        languages="hin+eng",
        config=config
    )

    pages = loader.load_pages()

    for page in pages:
        print("Confidence:", page["metadata"]["ocr_confidence"])
        print("\nExtracted text:\n")
        print(page["text"])