
from evaluation.retrieval_runner import RetrievalRunner


def main():
    runner = RetrievalRunner()

    question = "What are the essential elements of a valid contract under Indian law?"

    chunks = runner.retrieve(question=question, document_id="eb31e7e1-ab00-4f58-ba05-0aaa98e9344b")

    print("\nRetrieved chunks:")

    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk.get("metadata", {})

        print(f"\n{'=' * 60}")
        print(f"Rank: {index}")
        print("Chunk ID:", chunk.get("chunk_id"))
        print("Page:", metadata.get("page_number"))
        print("Content:")
        print(chunk.get("content", ""))

if __name__ == "__main__":
    main()
