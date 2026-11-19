import json
import re
from html import unescape
from pathlib import Path

from rag.ingestion.evaluation.ocr_metrics import evaluate_ocr


RESULTS_DIR = Path("rag/ingestion/evaluation/results")

GROUND_TRUTH = Path(
    "rag/ingestion/evaluation/ground_truth/page_5.txt"
)


def html_to_text(html: str) -> str:
    html = re.sub(
        r"<br\s*/?>",
        "\n",
        html,
        flags=re.I,
    )

    html = re.sub(
        r"</(?:td|th)>",
        " ",
        html,
        flags=re.I,
    )

    html = re.sub(
        r"</(?:p|tr|div|li)>",
        "\n",
        html,
        flags=re.I,
    )

    text = re.sub(r"<[^>]+>", "", html)

    return unescape(text).strip()


def extract_surya_text(result_path: Path) -> str:
    data = json.loads(
        result_path.read_text(encoding="utf-8")
    )

    paragraphs = []

    for pages in data.values():
        for page in pages:
            blocks = sorted(
                page["blocks"],
                key=lambda block: block["reading_order"]
            )

            for block in blocks:
                if block.get("skipped") or block.get("error"):
                    continue

                text = html_to_text(
                    block.get("html", "")
                )

                if text:
                    paragraphs.append(text)

    return "\n\n".join(paragraphs)


def main():
    result_path = next(
        (RESULTS_DIR / "surya_page32").rglob(
            "results.json"
        ),
        None
    )

    if result_path is None:
        raise FileNotFoundError(
            "Surya results.json not found."
        )

    reference = GROUND_TRUTH.read_text(
        encoding="utf-8"
    )

    hypothesis = extract_surya_text(result_path)

    metrics = evaluate_ocr(reference, hypothesis)

    print("=" * 65)
    print("LEGALMIND SURYA OCR EVALUATION")
    print("=" * 65)

    print(f"CER:                {metrics['cer']:.4f}")
    print(f"WER:                {metrics['wer']:.4f}")
    print(f"Character accuracy: {metrics['character_accuracy']:.2%}")
    print(f"Word accuracy:      {metrics['word_accuracy']:.2%}")

    print("\nOCR OUTPUT:\n")
    print(hypothesis)

    result = {
        "image": "3.jpg",
        "ground_truth": GROUND_TRUTH.name,
        "engine": "surya",
        "preprocessing": "default",
        "confidence": None,
        "execution_time_seconds": None,
        "metrics": metrics,
        "ocr_output": hypothesis,
    }

    output_path = RESULTS_DIR / "3_surya.json"

    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )

    print(f"\nBenchmark saved: {output_path}")


if __name__ == "__main__":
    main()