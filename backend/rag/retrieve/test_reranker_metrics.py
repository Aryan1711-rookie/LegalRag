
from sentence_transformers import CrossEncoder # pyright: ignore[reportMissingImports]

from rag.embeddings.embedding_manager import EmbeddingManager
from rag.retrieve.search_repository import SearchRepository
from rag.retrieve.reranker import CrossEncoderReranker


# ============================================================
# CONFIGURATION
# ============================================================

CANDIDATE_COUNT = 30
RERANK_TOP_K = 10
METRIC_K = 10
NDCG_K = 5

QUESTIONS = [
    "What is the Basic Structure Doctrine of the Indian Constitution?",
    "What was the Supreme Court's decision in Minerva Mills v. Union of India?",
    "What did the Supreme Court decide about cryptocurrency taxation in India in 2024?"
]


# ============================================================
# MANUALLY JUDGED RELEVANCE LABELS
# 0 = Not relevant
# 1 = Broadly relevant
# 2 = Directly relevant
# ============================================================

RELEVANCE_LABELS = {
    QUESTIONS[0]: {
        "chunk_00025": 1,
        "chunk_00032": 1,
        "chunk_00026": 0,
        "chunk_00033": 1,
        "chunk_00034": 1,
        "chunk_00024": 2,
        "chunk_00023": 1,
        "chunk_00029": 1,
        "chunk_00031": 1,
        "chunk_00022": 1
    },

    QUESTIONS[1]: {
        "chunk_00029": 2,
        "chunk_00031": 2,
        "chunk_00040": 0,
        "chunk_00030": 2,
        "chunk_00060": 0,
        "chunk_00041": 0,
        "chunk_00013": 0,
        "chunk_00012": 0,
        "chunk_00061": 0,
        "chunk_00038": 0
    },

    QUESTIONS[2]: {
        "chunk_00043": 0,
        "chunk_00041": 0,
        "chunk_00012": 0,
        "chunk_00054": 0,
        "chunk_00038": 0,
        "chunk_00088": 0,
        "chunk_00016": 0,
        "chunk_00064": 0,
        "chunk_00035": 0,
        "chunk_00001": 0
    }
}


# ============================================================
# METRIC FUNCTIONS
# ============================================================

def calculate_mrr(
    ranking,
    relevance,
    k=10,
    relevance_threshold=1
):
    """
    Mean Reciprocal Rank.

    relevance_threshold=1:
        Broad MRR. Grade 1 and 2 count as relevant.

    relevance_threshold=2:
        Strict MRR. Only directly relevant chunks count.
    """

    for rank, chunk_id in enumerate(ranking[:k], start=1):
        grade = relevance.get(chunk_id, 0)

        if grade >= relevance_threshold:
            return 1.0 / rank

    # None means no relevant item exists in the judged set.
    if not any(
        grade >= relevance_threshold
        for grade in relevance.values()
    ):
        return None

    return 0.0


def calculate_dcg(ranking, relevance, k=5):
    """
    Discounted Cumulative Gain.

    Uses graded relevance:
        0 = 0 gain
        1 = 1 gain
        2 = 3 gain
    """

    dcg = 0.0

    for rank, chunk_id in enumerate(ranking[:k], start=1):
        grade = relevance.get(chunk_id, 0)

        gain = (2 ** grade) - 1
        discount = __import__("math").log2(rank + 1)

        dcg += gain / discount

    return dcg


def calculate_ndcg(ranking, relevance, k=5):
    """
    Normalized Discounted Cumulative Gain.
    """

    dcg = calculate_dcg(
        ranking,
        relevance,
        k
    )

    ideal_ranking = sorted(
        relevance,
        key=lambda chunk_id: relevance[chunk_id],
        reverse=True
    )

    ideal_dcg = calculate_dcg(
        ideal_ranking,
        relevance,
        k
    )

    if ideal_dcg == 0:
        return None

    return dcg / ideal_dcg


def calculate_average(values):
    """
    Average only defined metric values.
    """

    valid_values = [
        value for value in values
        if value is not None
    ]

    if not valid_values:
        return None

    return sum(valid_values) / len(valid_values)


def format_metric(value):
    if value is None:
        return "N/A"

    return f"{value:.4f}"


# ============================================================
# INITIALIZE MODELS AND REPOSITORIES
# ============================================================

print("Loading embedding model...")

embedding_manager = EmbeddingManager()

print("Initializing database repository...")

search_repository = SearchRepository()

print("Loading cross-encoder reranker...")

reranker = CrossEncoderReranker()

print("\nAll components initialized successfully.")


# ============================================================
# METRIC COLLECTION
# ============================================================

bge_broad_mrr_scores = []
reranker_broad_mrr_scores = []

bge_strict_mrr_scores = []
reranker_strict_mrr_scores = []

bge_ndcg_scores = []
reranker_ndcg_scores = []


# ============================================================
# EVALUATION
# ============================================================

for question_number, question in enumerate(QUESTIONS, start=1):

    print("\n" + "=" * 70)
    print(f"QUESTION {question_number}")
    print("=" * 70)

    print("\nQuery:", question)

    relevance = RELEVANCE_LABELS[question]

    # --------------------------------------------------------
    # STEP 1: Generate query embedding
    # --------------------------------------------------------

    query_embedding = embedding_manager.generate_embedding(
        question
    )

    # --------------------------------------------------------
    # STEP 2: Retrieve candidates using BGE
    # --------------------------------------------------------

    candidates = search_repository.search(
        query_embedding=query_embedding,
        match_count=CANDIDATE_COUNT
    )

    bge_ranking = [
        document["chunk_id"]
        for document in candidates
    ]

    # --------------------------------------------------------
    # STEP 3: Cross-encoder reranking
    # --------------------------------------------------------

    reranked_documents = reranker.rerank(
        query=question,
        documents=candidates,
        top_k=RERANK_TOP_K
    )

    reranker_ranking = [
        document["chunk_id"]
        for document in reranked_documents
    ]

    # --------------------------------------------------------
    # STEP 4: Print BGE ranking
    # --------------------------------------------------------

    print("\n---------- BGE RANKING ----------")

    for rank, document in enumerate(candidates, start=1):

        chunk_id = document["chunk_id"]
        grade = relevance.get(chunk_id, 0)

        print(
            f"Rank {rank:02d} | "
            f"{chunk_id} | "
            f"Relevance: {grade} | "
            f"Similarity: {document.get('similarity', 0):.4f}"
        )

    # --------------------------------------------------------
    # STEP 5: Print reranker ranking
    # --------------------------------------------------------

    print("\n---------- CROSS-ENCODER RANKING ----------")

    for rank, document in enumerate(
        reranked_documents,
        start=1
    ):

        chunk_id = document["chunk_id"]
        grade = relevance.get(chunk_id, 0)

        print(
            f"Rank {rank:02d} | "
            f"{chunk_id} | "
            f"Relevance: {grade} | "
            f"Rerank Score: {document['rerank_score']:.4f}"
        )

    # --------------------------------------------------------
    # STEP 6: Calculate broad MRR
    # --------------------------------------------------------

    bge_broad_mrr = calculate_mrr(
        bge_ranking,
        relevance,
        k=METRIC_K,
        relevance_threshold=1
    )

    reranker_broad_mrr = calculate_mrr(
        reranker_ranking,
        relevance,
        k=METRIC_K,
        relevance_threshold=1
    )

    # --------------------------------------------------------
    # STEP 7: Calculate strict MRR
    # --------------------------------------------------------

    bge_strict_mrr = calculate_mrr(
        bge_ranking,
        relevance,
        k=METRIC_K,
        relevance_threshold=2
    )

    reranker_strict_mrr = calculate_mrr(
        reranker_ranking,
        relevance,
        k=METRIC_K,
        relevance_threshold=2
    )

    # --------------------------------------------------------
    # STEP 8: Calculate NDCG
    # --------------------------------------------------------

    bge_ndcg = calculate_ndcg(
        bge_ranking,
        relevance,
        k=NDCG_K
    )

    reranker_ndcg = calculate_ndcg(
        reranker_ranking,
        relevance,
        k=NDCG_K
    )

    # --------------------------------------------------------
    # STEP 9: Store metrics
    # --------------------------------------------------------

    bge_broad_mrr_scores.append(bge_broad_mrr)
    reranker_broad_mrr_scores.append(reranker_broad_mrr)

    bge_strict_mrr_scores.append(bge_strict_mrr)
    reranker_strict_mrr_scores.append(reranker_strict_mrr)

    bge_ndcg_scores.append(bge_ndcg)
    reranker_ndcg_scores.append(reranker_ndcg)

    # --------------------------------------------------------
    # STEP 10: Print individual metrics
    # --------------------------------------------------------

    print("\n---------- METRICS ----------")

    print("\nBroad MRR@10")
    print("BGE:", format_metric(bge_broad_mrr))
    print("Reranker:", format_metric(reranker_broad_mrr))

    print("\nStrict MRR@10")
    print("BGE:", format_metric(bge_strict_mrr))
    print("Reranker:", format_metric(reranker_strict_mrr))

    print("\nNDCG@5")
    print("BGE:", format_metric(bge_ndcg))
    print("Reranker:", format_metric(reranker_ndcg))


# ============================================================
# FINAL AVERAGE METRICS
# ============================================================

print("\n\n" + "=" * 70)
print("FINAL AVERAGE METRICS")
print("=" * 70)

print("\n---------- BROAD MRR@10 ----------")

print(
    "BGE:",
    format_metric(calculate_average(bge_broad_mrr_scores))
)

print(
    "Reranker:",
    format_metric(calculate_average(reranker_broad_mrr_scores))
)


print("\n---------- STRICT MRR@10 ----------")

print(
    "BGE:",
    format_metric(calculate_average(bge_strict_mrr_scores))
)

print(
    "Reranker:",
    format_metric(calculate_average(reranker_strict_mrr_scores))
)


print("\n---------- NDCG@5 ----------")

print(
    "BGE:",
    format_metric(calculate_average(bge_ndcg_scores))
)

print(
    "Reranker:",
    format_metric(calculate_average(reranker_ndcg_scores))
)


print("\n---------- RECALL ----------")

print(
    "Recall@10: NOT EVALUATED"
)

print(
    "Reason: Relevance labels do not cover the entire document corpus."
)


print("\nEvaluation completed.")
