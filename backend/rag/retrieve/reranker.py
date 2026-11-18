
from sentence_transformers import CrossEncoder # pyright: ignore[reportMissingImports]


class CrossEncoderReranker:

    def __init__(
        self,
        #model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
        model_name = "BAAI/bge-reranker-base    "
    ):
        self.model = CrossEncoder(
            model_name,
            device="cpu"
        )

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 5
    ) -> list[dict]:

        if not documents:
            return []

        # Create query-document pairs
        pairs = [
            (query, document["content"])
            for document in documents
        ]

        # Generate relevance scores
        scores = self.model.predict(
            pairs,
            show_progress_bar=False
        )

        # Attach scores without modifying original documents
        reranked_documents = []

        for document, score in zip(documents, scores):
            result = document.copy()
            result["rerank_score"] = float(score)

            reranked_documents.append(result)

        # Sort by cross-encoder relevance score
        reranked_documents.sort(
            key=lambda document: document["rerank_score"],
            reverse=True
        )

        return reranked_documents[:top_k]
