
from evaluation.dataset_loader import load_evaluation_dataset
from evaluation.answer_quality_runner import AnswerQualityRunner
from rag.generation.context_builder import ContextBuilder

DOCUMENT_ID = "eb31e7e1-ab00-4f58-ba05-0aaa98e9344b"


def main():

    dataset = load_evaluation_dataset()

    runner = AnswerQualityRunner(
        document_id=DOCUMENT_ID
    )

    for case in dataset:

        print("\n" + "=" * 65)
        print("Evaluation ID:", case["id"])
        print("Question:", case["question"])

        result = runner.evaluate_case(case)

        print("\nGenerated Answer:")
        print(result["answer"])
        print("\nPerformance Metrics:")

        performance = result.get("performance", {})

        for metric, value in performance.items():
            if metric == "token_usage":
                print("Token Usage:")
                for token, count in value.items():
                    print(f"  {token}: {count}")
            else:
                print(f"{metric}: {value}")

        print("\nAnswer Quality Metrics:")

        for metric, score in result["quality_metrics"].items():
            if metric != "reasoning":
                print(f"{metric}: {score:.4f}")

        print("\nJudge Reasoning:")
        print(result["quality_metrics"]["reasoning"])

        print("\nCitation Report:")
        print(result["citation_report"])

        print("\nGrounding Report:")
        print(result["grounding_report"])


if __name__ == "__main__":
    main()
