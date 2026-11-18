
import json
from pathlib import Path


DATASET_PATH = (
    Path(__file__).parent
    / "datasets"
    / "legal_qa.json"
)


def load_evaluation_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {DATASET_PATH}"
        )

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not isinstance(dataset, list):
        raise ValueError(
            "Evaluation dataset must be a JSON list."
        )

    required_fields = {
        "id",
        "question",
        "ground_truth",
        "relevant_pages",
        "relevant_chunks",
        "category",
    }

    for index, item in enumerate(dataset):
        if not isinstance(item, dict):
            raise ValueError(
                f"Dataset item at index {index} must be an object."
            )

        missing_fields = required_fields - item.keys()

        if missing_fields:
            raise ValueError(
                f"Dataset item {index} is missing: "
                f"{', '.join(sorted(missing_fields))}"
            )

        if not item["question"].strip():
            raise ValueError(
                f"Dataset item {index} has an empty question."
            )

        if not item["ground_truth"].strip():
            raise ValueError(
                f"Dataset item {index} has an empty ground truth."
            )

    return dataset
