
import json
from time import perf_counter

from database.supabase import get_supabase
from rag.retrieve.mmr import mmr
import sys
import re
from rag.retrieve.rrf import reciprocal_rank_fusion
from database.document_repository import DocumentRepository
class SearchRepository:
    LEGAL_SYNONYMS = {
    "fir": [
        "first information report",
        "information in cognizable cases"
    ],
    "zero fir": [
        "irrespective of the area"
    ],
    "remand": [
        "detention of the accused",
        "police custody",
        "judicial custody"
    ],
    "default bail": [
        "expiry of detention period",
        "furnish bail"
    ],
    "undertrial": [
        "under trial prisoner",
        "maximum period of detention"
    ]
}

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
    def get_section_chunks(
    self,
    document_id: str,
    section_number: str,
    limit: int = 20
):

        if not document_id:
            raise ValueError("Document ID is required.")

        response = (
            self.supabase
            .table("document_chunks")
            .select(
                "id, document_id, chunk_id, content, metadata"
            )
            .eq("document_id", document_id)
            .eq(
                "metadata->>section_number",
                str(section_number)
            )
            .order("chunk_id")
            .limit(limit)
            .execute()
        )

        return response.data or []

    def search_lexical(
    self,
    question: str,
    document_id: str,
    user_id: str,
    match_count: int = 20
) -> list[dict]:

        if not document_id or not user_id:
            raise ValueError(
                "Document ID and user ID are required."
            )

        start = perf_counter()
        expanded_query = self.expand_lexical_query(question)

        print("Original query:", question)
        print("Expanded query:", expanded_query)
        response = self.supabase.rpc(
            "search_document_chunks_lexical",
            {
                "search_query": expanded_query  ,
                "filter_document_id": document_id,
                "filter_user_id": user_id,
                "match_count": match_count
            }
        ).execute()

        candidates = response.data or []

        elapsed = perf_counter() - start

        print("\n========== LEXICAL SEARCH ==========")
        print(f"Candidates: {len(candidates)}")
        print(f"Search time: {elapsed:.4f}s")
        print("====================================\n")

        return candidates
    
    def expand_lexical_query(self, question: str) -> str:

        normalized = question.lower().strip()

        original = " ".join(
            re.findall(r"\w+", question)
        )

        expanded_terms = []

        for keyword, synonyms in self.LEGAL_SYNONYMS.items():

            if re.search(
                rf"\b{re.escape(keyword)}\b",
                normalized
            ):
                expanded_terms.extend(synonyms)

        # Detect territorial FIR questions
        if "fir" in normalized and any(
            term in normalized
            for term in [
                "jurisdiction",
                "outside",
                "territorial",
                "another police station"
            ]
        ):
            expanded_terms.append(
                "irrespective of the area"
            )

        expanded_terms = list(dict.fromkeys(expanded_terms))

        query_parts = [original] if original else []

        query_parts.extend(
            f'"{term}"'
            for term in expanded_terms
        )

        return " OR ".join(query_parts)

    def search_hybrid_with_metrics(
    self,
    question: str,
    query_embedding: list[float],
    document_id: str,
    user_id: str,
    candidate_count: int = 20,
    top_k: int = 5,
    rrf_k: int = 60
):

        total_start = perf_counter()

        if not document_id or not user_id:
            raise ValueError("Document ID and user ID are required.")

        # Verify document ownership before either search
        document = DocumentRepository().get_document_for_user(
            document_id=document_id,
            user_id=user_id
        )

        if not document or document["status"] != "completed":
            raise PermissionError("Document is not available.")

        # 1. Dense retrieval
        dense_start = perf_counter()

        dense_results = self._retrieve_candidates(
            query_embedding=query_embedding,
            match_count=candidate_count,
            document_id=document_id
        )

        dense_seconds = perf_counter() - dense_start

        # 2. Lexical retrieval
        lexical_start = perf_counter()

        lexical_results = self.search_lexical(
            question=question,
            document_id=document_id,
            user_id=user_id,
            match_count=candidate_count
        )

        lexical_seconds = perf_counter() - lexical_start

        # 3. Reciprocal Rank Fusion
        fusion_start = perf_counter()

        fused_results = reciprocal_rank_fusion(
            dense_results=dense_results,
            lexical_results=lexical_results,
            k=rrf_k
        )

        fusion_seconds = perf_counter() - fusion_start

        # 4. Select top results
        selected_chunks = fused_results[:top_k]

        # Remove embeddings from response
        cleaned_chunks = [
            {
                key: value
                for key, value in chunk.items()
                if key != "embedding"
            }
            for chunk in selected_chunks
        ]

        performance = {
            "dense_seconds": round(dense_seconds, 4),
            "lexical_seconds": round(lexical_seconds, 4),
            "fusion_seconds": round(fusion_seconds, 4),
            "dense_candidates": len(dense_results),
            "lexical_candidates": len(lexical_results),
            "candidate_count": len(fused_results),
            "selected_count": len(cleaned_chunks),
            "database_seconds": round(
                dense_seconds + lexical_seconds, 4
            ),
            "mmr_seconds": 0.0,
            "hybrid_total_seconds": round(
                perf_counter() - total_start, 4
            )
        }

        print("\n========== HYBRID RETRIEVAL ==========")
        print("Dense candidates:", len(dense_results))
        print("Lexical candidates:", len(lexical_results))
        print("Unique candidates:", len(fused_results))
        print("Selected chunks:", len(cleaned_chunks))

        for rank, chunk in enumerate(cleaned_chunks, start=1):

            metadata = chunk.get("metadata") or {}

            print(
                f"Rank: {rank} | "
                f"Chunk: {chunk['chunk_id']} | "
                f"Section: {metadata.get('section_number')} | "
                f"RRF: {chunk['rrf_score']:.6f}"
            )

        print("======================================\n")

        return cleaned_chunks, performance