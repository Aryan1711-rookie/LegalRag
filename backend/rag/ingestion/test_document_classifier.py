import argparse
import json

from rag.ingestion.parser import extract_text

from rag.ingestion.classifiers.document_classifier import (
    DocumentClassifier
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file",
        required=True
    )

    args = parser.parse_args()

    pages = extract_text(args.file)

    classifier = DocumentClassifier()

    result = classifier.classify(pages)

    print("\n========== CLASSIFICATION RESULT ==========")

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()