import gc
import time

from database.supabase import get_supabase
from evaluation.dataset_loader import load_evaluation_dataset
from evaluation.multilingual_runner import MultilingualRunner
from evaluation.evaluator import Evaluator


DOCUMENT_ID = "eb31e7e1-ab00-4f58-ba05-0aaa98e9344b"

MODELS = [
    "BAAI/bge-base-en-v1.5",
    "intfloat/multilingual-e5-small",
    "intfloat/multilingual-e5-base",
]

TOP_K = 5
PAGE_SIZE = 500


def load_document_chunks(document_id: str):

    supabase = get_supabase()

    chunks = []
    offset = 0

    while True:

        response = (
            supabase
            .table("document_chunks")
            .select(
                "chunk_id, content, retrieval_text, metadata"
            )
            .eq("document_id", document_id)
            .order("chunk_id")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )

        batch = response.data or []

        chunks.extend(batch)

        if len(batch) < PAGE_SIZE:
            break

        offset += PAGE_SIZE

    if not chunks:
        raise ValueError(
            f"No chunks found for document {document_id}"
        )

    return chunks


def benchmark_model(model_name, chunks, dataset):

    print("\n" + "=" * 75)
    print("MODEL:", model_name)
    print("=" * 75)

    evaluator = Evaluator()

    runner = MultilingualRunner(model_name)

    start = time.perf_counter()

    runner.index_chunks(chunks)

    indexing_time = time.perf_counter() - start

    all_metrics = []
    retrieval_times = []

    for case in dataset:

        print("\nEvaluation ID:", case["id"])
        print("Question:", case["question"])

        start = time.perf_counter()

        retrieved_chunks = runner.get_retrieved_chunk_ids(
            question=case["question"],
            top_k=TOP_K
        )

        retrieval_time = time.perf_counter() - start

        metrics = evaluator.evaluate_retrieval(
            retrieved_chunks=retrieved_chunks,
            relevant_chunks=case["relevant_chunks"],
            k=TOP_K
        )

        all_metrics.append(metrics)
        retrieval_times.append(retrieval_time)

        print("Retrieved:", retrieved_chunks)
        print("Relevant:", case["relevant_chunks"])

        for metric, score in metrics.items():
            print(f"{metric}: {score:.4f}")

        print(
            f"Retrieval time: {retrieval_time:.4f}s"
        )

    average_metrics = {
        metric: sum(
            result[metric]
            for result in all_metrics
        ) / len(all_metrics)
        for metric in all_metrics[0]
    }

    result = {
        "model": model_name,
        "dimensions": runner.embeddings.shape[1],
        "indexing_time": indexing_time,
        "average_retrieval_time": (
            sum(retrieval_times) / len(retrieval_times)
        ),
        **average_metrics
    }

    del runner
    gc.collect()

    return result


def main():

    dataset = [
        case
        for case in load_evaluation_dataset()
        if case.get("expected_answerable", True)
        and case["relevant_chunks"]
    ]

    if not dataset:
        raise ValueError("No answerable evaluation cases found.")

    chunks = load_document_chunks(DOCUMENT_ID)

    available_ids = {
        chunk["chunk_id"]
        for chunk in chunks
    }

    for case in dataset:

        missing = (
            set(case["relevant_chunks"]) - available_ids
        )

        if missing:
            raise ValueError(
                f"Missing relevant chunks for "
                f"{case['id']}: {missing}"
            )

    print("Total document chunks:", len(chunks))
    print("Total evaluation questions:", len(dataset))

    results = []

    for model_name in MODELS:

        result = benchmark_model(
            model_name=model_name,
            chunks=chunks,
            dataset=dataset
        )

        results.append(result)

    print("\n" + "=" * 120)
    print("LEGALMIND REAL-WORLD EMBEDDING BENCHMARK")
    print("=" * 120)

    print(
        f"{'Model':<38}"
        f"{'Dims':>6}"
        f"{'P@5':>10}"
        f"{'R@5':>10}"
        f"{'MRR':>10}"
        f"{'NDCG@5':>10}"
        f"{'Index(s)':>12}"
        f"{'Query(s)':>12}"
    )

    for r in results:

        print(
            f"{r['model']:<38}"
            f"{r['dimensions']:>6}"
            f"{r['precision@5']:>10.4f}"
            f"{r['recall@5']:>10.4f}"
            f"{r['mrr']:>10.4f}"
            f"{r['ndcg@5']:>10.4f}"
            f"{r['indexing_time']:>12.4f}"
            f"{r['average_retrieval_time']:>12.4f}"
        )


if __name__ == "__main__":
    main()