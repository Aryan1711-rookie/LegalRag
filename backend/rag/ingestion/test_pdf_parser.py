import argparse
import time

from rag.ingestion.parser import extract_text


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--pdf", required=True)

    args = parser.parse_args()

    start = time.perf_counter()

    pages = extract_text(args.pdf)

    print("\n========== EXTRACTION RESULTS ==========")

    for page in pages:

        print(f"\nPAGE: {page['page_number']}")

        print(f"Type: {page['page_type']}")

        print(f"Engine: {page['extraction_method']}")

        print(f"Characters: {len(page['text'])}")

        print("\nExtracted text:\n")

        print(page["text"])

        print("=" * 80)

    print(f"\nTotal pages: {len(pages)}")

    print(
        "Execution time:",
        round(time.perf_counter() - start, 2),
        "seconds"
    )


if __name__ == "__main__":
    main()