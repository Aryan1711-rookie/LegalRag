
import json

from database.supabase import get_supabase
from rag.retrieve.mmr import mmr


class SearchRepository:

    def __init__(self):
        self.supabase = get_supabase()

    def _retrieve_candidates(
        self,
        query_embedding: list[float],
        match_count: int = 20,
        document_id: str = None
    ):

        vector_string = "[" + ",".join(
            str(value) for value in query_embedding
        ) + "]"

        response = self.supabase.rpc(
            "match_document_chunks",
            {
                "query_embedding": vector_string,
                "match_count": match_count,
                "filter_document_id": document_id
            }
        ).execute()

        candidates = response.data

        # Convert pgvector string representation to Python lists
        for chunk in candidates:
            embedding = chunk["embedding"]

            if isinstance(embedding, str):
                embedding = json.loads(embedding)

            chunk["embedding"] = [
                float(value) for value in embedding
            ]

        return candidates

    def search(
        self,
        query_embedding: list[float],
        match_count: int = 5,
        document_id: str = None
    ):

        return self._retrieve_candidates(
            query_embedding,
            match_count,
            document_id
        )

    def search_with_mmr(
        self,
        query_embedding: list[float],
        candidate_count: int = 20,
        top_k: int = 5,
        document_id: str = None,
        lambda_param: float = 0.7
    ):

        candidates = self._retrieve_candidates(
            query_embedding,
            candidate_count,
            document_id
        )

        selected_chunks = mmr(
            query_embedding=query_embedding,
            candidate_chunks=candidates,
            top_k=top_k,
            lambda_param=lambda_param
        )

        # Remove embeddings from returned results.
        # We only need them internally for MMR.
        return [
            {
                key: value
                for key, value in chunk.items()
                if key != "embedding"
            }
            for chunk in selected_chunks
        
        ]
        # return selected_chunks
