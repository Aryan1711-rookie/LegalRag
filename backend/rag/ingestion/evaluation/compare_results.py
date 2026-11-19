
import json
from pathlib import Path


RESULTS_DIR = Path("rag/ingestion/evaluation/results")


def load_results():
    if not RESULTS_DIR.exists():
        raise FileNotFoundError(
            f"Results directory not found: {RESULTS_DIR}"
        )

    results = []

    for file_path in RESULTS_DIR.glob("*.json"):
        try:
            data = json.loads(
                file_path.read_text(encoding="utf-8")
            )

            metrics = data.get("metrics", {})

            results.append({
                "file": file_path.name,
                "image": data.get("image", "Unknown"),
                "preprocessing": data.get(
                    "preprocessing", "Unknown"
                ),
                "config": data.get("config", "Unknown"),
                "cer": metrics.get("cer"),
                "wer": metrics.get("wer"),
                "character_accuracy": metrics.get(
                    "character_accuracy"
                ),
                "word_accuracy": metrics.get("word_accuracy"),
                "confidence": data.get("confidence"),
                "execution_time": data.get(
                    "execution_time_seconds"
                ),
            })

        except (json.JSONDecodeError, OSError) as error:
            print(f"Skipping {file_path.name}: {error}")

    return results


def display_results(results):
    if not results:
        print("No benchmark results found.")
        return

    results.sort(
        key=lambda item: (
            item["cer"] is None,
            item["cer"] if item["cer"] is not None else float("inf")
        )
    )

    print("\n" + "=" * 105)
    print("LEGALMIND OCR BENCHMARK COMPARISON")
    print("=" * 105)

    header = (
        f"{'Image':<14}"
        f"{'Method':<16}"
        f"{'CER':>9}"
        f"{'WER':>9}"
        f"{'Char Acc':>12}"
        f"{'Word Acc':>11}"
        f"{'Confidence':>12}"
        f"{'Time(s)':>10}"
    )

    print(header)
    print("-" * 105)

    for result in results:
        cer = result["cer"]
        wer = result["wer"]
        char_acc = result["character_accuracy"]
        word_acc = result["word_accuracy"]
        confidence = result["confidence"]
        execution_time = result["execution_time"]

        print(
            f"{result['image']:<14}"
            f"{result['preprocessing']:<16}"
            f"{cer if cer is not None else '-':>9}"
            f"{wer if wer is not None else '-':>9}"
            f"{f'{char_acc:.2%}' if char_acc is not None else '-':>12}"
            f"{f'{word_acc:.2%}' if word_acc is not None else '-':>11}"
            f"{confidence if confidence is not None else '-':>12}"
            f"{execution_time if execution_time is not None else '-':>10}"
        )

    print("-" * 105)

    best = next(
        (item for item in results if item["cer"] is not None),
        None
    )

    if best:
        print("\nLowest CER:")
        print(f"  Image: {best['image']}")
        print(f"  Method: {best['preprocessing']}")
        print(f"  CER: {best['cer']}")
        print(f"  WER: {best['wer']}")

    print("\nNote: Lower CER/WER is better.")
    print("Accuracy values are clipped complements of error rates.")
    print("=" * 105)


def main():
    results = load_results()
    display_results(results)


if __name__ == "__main__":
    main()
