
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from rag.ingestion.loaders.image_loader import ImageLoader
from rag.ingestion.evaluation.ocr_metrics import evaluate_ocr


ENGINES = [
    "easyocr",
    "groq",
    "tesseract",
]

METHODS = [
    "baseline",
    "otsu",
    "adaptive",
    "denoise_otsu",
    "deskew",
    "clahe",
    "sharpen",
    "combined",
]


def evaluate_image(
    image_path: Path,
    ground_truth_path: Path,
    engine: str,
    method: str,
):
    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    if not ground_truth_path.exists():
        raise FileNotFoundError(
            f"Ground truth not found: {ground_truth_path}"
        )

    reference = ground_truth_path.read_text(
        encoding="utf-8"
    )

    # Initialize the requested OCR engine explicitly.
    loader = ImageLoader(
        str(image_path),
        engine=engine,
    )

    # Run only the selected engine.
    # Tesseract additionally supports preprocessing methods.
    if engine == "tesseract":
        ocr_method = method
        preprocessing = method
    else:
        ocr_method = engine
        preprocessing = "default"

    start_time = time.perf_counter()

    hypothesis, confidence = loader.run_ocr(
        ocr_method
    )

    execution_time = time.perf_counter() - start_time

    metrics = evaluate_ocr(
        reference,
        hypothesis,
    )

    result = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "image": image_path.name,
        "image_path": str(image_path),
        "ground_truth": ground_truth_path.name,

        "engine": engine,
        "language": loader.languages,
        "preprocessing": preprocessing,

        "config": loader.config,
        "confidence": confidence,

        "execution_time_seconds": round(
            execution_time,
            4,
        ),

        "metrics": metrics,
        "ocr_output": hypothesis,
    }

    # Save results.
    results_dir = Path(
        "rag/ingestion/evaluation/results"
    )

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Keep engine and preprocessing in the filename
    # to prevent different experiments from overwriting each other.
    if engine == "tesseract":
        result_filename = (
            f"{image_path.stem}_tesseract_{method}.json"
        )
    else:
        result_filename = (
            f"{image_path.stem}_{engine}.json"
        )

    result_path = results_dir / result_filename

    result_path.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=4,
        ),
        encoding="utf-8",
    )

    # Display evaluation report.
    print("\n" + "=" * 70)
    print("LEGALMIND OCR EVALUATION")
    print("=" * 70)

    print(f"Image:              {image_path.name}")
    print(f"Ground truth:       {ground_truth_path.name}")
    print(f"OCR engine:         {engine.upper()}")
    print(f"OCR language:       {loader.languages}")
    print(f"Preprocessing:      {preprocessing}")
    print(f"OCR configuration:  {loader.config}")

    print("\n" + "-" * 70)
    print("PERFORMANCE")
    print("-" * 70)

    if confidence is not None:
        print(f"OCR confidence:     {confidence:.2f}")
    else:
        print("OCR confidence:     Not available")

    print(
        f"Execution time:     {execution_time:.2f} seconds"
    )

    print("\n" + "-" * 70)
    print("ACCURACY METRICS")
    print("-" * 70)

    print(f"CER:                {metrics['cer']:.4f}")
    print(f"WER:                {metrics['wer']:.4f}")

    print(
        f"Character accuracy: "
        f"{metrics['character_accuracy']:.2%}"
    )

    print(
        f"Word accuracy:      "
        f"{metrics['word_accuracy']:.2%}"
    )

    print("\n" + "-" * 70)
    print("OCR OUTPUT")
    print("-" * 70)

    print(hypothesis)

    print("\n" + "=" * 70)
    print(f"Benchmark saved: {result_path}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate EasyOCR, Groq Vision and Tesseract."
    )

    parser.add_argument(
        "--image",
        required=True,
        help="Path to source image.",
    )

    parser.add_argument(
        "--ground-truth",
        default=(
            "rag/ingestion/evaluation/"
            "ground_truth/page_32.txt"
        ),
        help="Path to ground-truth transcription.",
    )

    parser.add_argument(
        "--engine",
        choices=ENGINES,
        default="easyocr",
        help="OCR engine to evaluate.",
    )

    parser.add_argument(
        "--method",
        choices=METHODS,
        default="baseline",
        help=(
            "Tesseract preprocessing method. "
            "Only applicable when --engine tesseract."
        ),
    )

    args = parser.parse_args()

    evaluate_image(
        image_path=Path(args.image),
        ground_truth_path=Path(args.ground_truth),
        engine=args.engine,
        method=args.method,
    )


if __name__ == "__main__":
    main()
