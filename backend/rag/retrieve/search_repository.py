
import json
from time import perf_counter

from database.supabase import get_supabase
from rag.retrieve.mmr import mmr
import sys

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

        # 1. Measure Supabase RPC time
        rpc_start = perf_counter()

        response = self.supabase.rpc(
            "match_document_chunks",
            {
                "query_embedding": vector_string,
                "match_count": match_count,
                "filter_document_id": document_id
            }
        ).execute()

        rpc_seconds = perf_counter() - rpc_start

        candidates = response.data
        response_size = sys.getsizeof(candidates)

        print(f"Candidate count: {len(candidates)}")
        print(f"Response object shallow size: {response_size / 1024:.2f} KB")
        payload_bytes = len(json.dumps(candidates, default=str).encode("utf-8"))

        print(
            f"Actual response payload: "
            f"{payload_bytes / 1024:.2f} KB"
        )

        # 2. Measure embedding conversion time
        conversion_start = perf_counter()

        for chunk in candidates:
            embedding = chunk["embedding"]

            if isinstance(embedding, str):
                embedding = json.loads(embedding)

            chunk["embedding"] = [
                float(value) for value in embedding
            ]

        conversion_seconds = perf_counter() - conversion_start

        # 3. Print detailed timing
        print("\n========== SEARCH REPOSITORY PERFORMANCE ==========")
        print(f"RPC time:                {rpc_seconds:.4f}s")
        print(f"Embedding conversion:    {conversion_seconds:.4f}s")
        print(
            f"Total retrieval time:    "
            f"{rpc_seconds + conversion_seconds:.4f}s"
        )
        print(f"Candidates retrieved:    {len(candidates)}")
        print("====================================================\n")

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

    def search_with_mmr_and_metrics(
        self,
        query_embedding: list[float],
        candidate_count: int = 20,
        top_k: int = 5,
        document_id: str = None,
        lambda_param: float = 0.7
    ):

        # 1. Supabase candidate retrieval
        database_start = perf_counter()

        candidates = self._retrieve_candidates(
            query_embedding,
            candidate_count,
            document_id
        )

        database_seconds = perf_counter() - database_start

        # 2. MMR selection
        mmr_start = perf_counter()

        selected_chunks = mmr(
            query_embedding=query_embedding,
            candidate_chunks=candidates,
            top_k=top_k,
            lambda_param=lambda_param
        )

        mmr_seconds = perf_counter() - mmr_start

        # 3. Remove embeddings from returned results
        cleaned_chunks = [
            {
                key: value
                for key, value in chunk.items()
                if key != "embedding"
            }
            for chunk in selected_chunks
        ]

        performance = {
            "database_seconds": round(database_seconds, 4),
            "mmr_seconds": round(mmr_seconds, 4),
            "candidate_count": len(candidates),
            "selected_count": len(selected_chunks)
        }

        return cleaned_chunks, performance

    def search_with_mmr(
        self,
        query_embedding: list[float],
        candidate_count: int = 20,
        top_k: int = 5,
        document_id: str = None,
        lambda_param: float = 0.7
    ):

        selected_chunks, _ = self.search_with_mmr_and_metrics(
            query_embedding=query_embedding,
            candidate_count=candidate_count,
            top_k=top_k,
            document_id=document_id,
            lambda_param=lambda_param
        )

        return selected_chunks
