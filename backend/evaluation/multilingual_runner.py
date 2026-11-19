import numpy as np

from sentence_transformers import SentenceTransformer
from rag.retrieve.mmr import mmr


class MultilingualRunner:

    def __init__(self, model_name: str):

        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name,
            device="cpu"
        )

        self.chunks = []
        self.embeddings = None

    def _prepare_text(
        self,
        text: str,
        is_query: bool = False
    ):

        if "multilingual-e5" in self.model_name:
            prefix = "query: " if is_query else "passage: "
            return prefix + text

        return text

    def index_chunks(self, chunks: list[dict]):

        if not chunks:
            raise ValueError("No chunks available for indexing.")

        self.chunks = chunks

        texts = [
            self._prepare_text(
                chunk.get("retrieval_text") or chunk["content"]
            )
            for chunk in chunks
        ]

        self.embeddings = self.model.encode(
            texts,
            batch_size=12,
            normalize_embeddings=True,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        print(
            "Indexed chunks:",
            len(self.chunks)
        )

        print(
            "Embedding dimensions:",
            self.embeddings.shape[1]
        )

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        candidate_count: int = 20
    ):

        if self.embeddings is None:
            raise RuntimeError("Index chunks before retrieval.")

        query = self._prepare_text(
            question,
            is_query=True
        )

        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        similarities = (
            self.embeddings @ query_embedding
        )

        ranked_indices = np.argsort(
            similarities
        )[::-1][:candidate_count]

        candidates = []

        for index in ranked_indices:

            candidates.append({
                **self.chunks[index],
                "embedding": self.embeddings[index],
                "similarity": float(similarities[index])
            })

        selected = mmr(
            query_embedding=query_embedding,
            candidate_chunks=candidates,
            top_k=top_k,
            lambda_param=0.7
        )

        return selected

    def get_retrieved_chunk_ids(
        self,
        question: str,
        top_k: int = 5
    ):

        chunks = self.retrieve(
            question=question,
            top_k=top_k
        )

        return [
            chunk["chunk_id"]
            for chunk in chunks
        ]