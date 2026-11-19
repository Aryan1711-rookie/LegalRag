
from time import perf_counter

from database.supabase import get_supabase
from evaluation.run_answer_quality import DOCUMENT_ID
from rag.embeddings.embedding_manager import EmbeddingManager

import httpx

QUERY = (
    "What did the Supreme Court hold in the Minerva Mills case "
    "regarding Parliament's power to amend the Constitution?"
)

# Generate the query embedding once, outside the benchmark.
embedding_manager = EmbeddingManager()
query_embedding = embedding_manager.generate_embedding(QUERY)

vector_string = "[" + ",".join(
    str(value) for value in query_embedding
) + "]"

supabase = get_supabase()

print("\n========== RPC BENCHMARK ==========")

times = []

for run in range(1, 6):
    start = perf_counter()

    response = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": vector_string,
            "match_count": 20,
            "filter_document_id": DOCUMENT_ID
        }
    ).execute()

    elapsed = perf_counter() - start
    times.append(elapsed)

    print(
        f"Run {run}: {elapsed:.4f}s | "
        f"Candidates: {len(response.data)}"
    )

print("-----------------------------------")
print(f"Average: {sum(times) / len(times):.4f}s")
print(f"Minimum: {min(times):.4f}s")
print(f"Maximum: {max(times):.4f}s")
print("===================================")


# import httpx
# from time import perf_counter

# from database.supabase import get_supabase

# client = get_supabase().postgrest.session

# print("HTTP client:", type(client).__name__)
# print("HTTP/2 enabled:", client._transport._pool._http2)

# for run in range(1, 6):
#     start = perf_counter()

#     response = client.get(
#         "/",
#     )

#     elapsed = perf_counter() - start

#     print(
#         f"HTTP Run {run}: {elapsed:.4f}s | "
#         f"Status: {response.status_code}"
#     )
