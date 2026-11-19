
from evaluation.dataset_loader import load_evaluation_dataset
from evaluation.retrieval_runner import RetrievalRunner
from evaluation.evaluator import Evaluator


def main():

    dataset = load_evaluation_dataset()

    retrieval_runner = RetrievalRunner()
    evaluator = Evaluator()

    for case in dataset:

        print("\n" + "=" * 60)
        print("Evaluation ID:", case["id"])
        print("Question:", case["question"])

        retrieved_chunks = retrieval_runner.get_retrieved_chunk_ids(
            question=case["question"],
            document_id="eb31e7e1-ab00-4f58-ba05-0aaa98e9344b",
            top_k=5
        )

        metrics = evaluator.evaluate_retrieval(
            retrieved_chunks=retrieved_chunks,
            relevant_chunks=case["relevant_chunks"],
            k=5
        )

        print("\nRetrieved:", retrieved_chunks)
        print("Relevant:", case["relevant_chunks"])

        print("\nRetrieval Metrics:")

        for metric, score in metrics.items():
            print(f"{metric}: {score:.4f}")


if __name__ == "__main__":
    main()
