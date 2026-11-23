import argparse
import time

from rag.ingestion.parser import extract_image_text


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--image",
        required=True
    )

    args = parser.parse_args()

    start = time.perf_counter()

    pages = extract_image_text(args.image)

    print("\n========== IMAGE EXTRACTION ==========")

    for page in pages:

        print("Page:", page["page_number"])
        print("Type:", page["page_type"])
        print("Engine:", page["extraction_method"])
        print("Characters:", len(page["text"]))

        print("\nExtracted text:\n")
        print(page["text"])

        print("\nMetadata:")
        print(page["metadata"])

        print("=" * 80)

    print("Total pages:", len(pages))

    print(
        "Execution time:",
        round(time.perf_counter() - start, 2),
        "seconds"
    )


if __name__ == "__main__":
    main()