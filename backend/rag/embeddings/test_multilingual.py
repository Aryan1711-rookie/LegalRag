"""CPU smoke benchmark for LegalMind multilingual retrieval."""
import gc
import time

from sentence_transformers import SentenceTransformer

MODELS = [
    "BAAI/bge-base-en-v1.5",
    "intfloat/multilingual-e5-small",
    "intfloat/multilingual-e5-base",
]

DOCUMENTS = [
    ("D1", "Parliament cannot destroy the basic structure of the Constitution."),
    ("D2", "अगली सुनवाई की तिथि 25.05.2025 निर्धारित की जाती है।"),
    ("D3", "The right to privacy is a fundamental right under Article 21."),
    ("D4", "अभियुक्त को अपनी प्रतिरक्षा करने के लिए उचित अवसर प्रदान किया जाना चाहिए।"),
    ("D5", "The court dismissed the appeal due to insufficient evidence."),
    ("D6", "न्यायालय ने पुलिस को अतिरिक्त अनुसंधान करने का आदेश दिया।"),
]

QUERIES = [
    ("Can Parliament destroy the basic structure?", "D1", "EN -> EN"),
    ("When is the next hearing?", "D2", "EN -> HI"),
    ("निजता का अधिकार किस अनुच्छेद में है?", "D3", "HI -> EN"),
    ("अभियुक्त को प्रतिरक्षा का क्या अधिकार है?", "D4", "HI -> HI"),
    ("Why was the appeal dismissed?", "D5", "EN -> EN"),
    ("What investigation did the court order?", "D6", "EN -> HI"),
    ("Agli hearing kab hai?", "D2", "HINGLISH -> HI"),
]


def prepare_text(text, model_name, is_query=False):
    if "multilingual-e5" in model_name:
        return ("query: " if is_query else "passage: ") + text
    if "bge-base-en" in model_name and is_query:
        return "Represent this sentence for searching relevant passages: " + text
    return text


def benchmark_model(model_name):
    print("\n" + "=" * 75)
    print("MODEL:", model_name)
    print("=" * 75)
    start = time.perf_counter()
    model = SentenceTransformer(model_name, device="cpu")
    load_time = time.perf_counter() - start

    texts = [prepare_text(text, model_name) for _, text in DOCUMENTS]
    start = time.perf_counter()
    document_embeddings = model.encode(
        texts, normalize_embeddings=True, convert_to_numpy=True
    )
    embedding_time = time.perf_counter() - start

    hits_at_1 = hits_at_3 = 0
    reciprocal_ranks = []
    query_times = []

    for query, expected, query_type in QUERIES:
        prepared = prepare_text(query, model_name, is_query=True)
        start = time.perf_counter()
        query_embedding = model.encode(
            prepared, normalize_embeddings=True, convert_to_numpy=True
        )
        query_times.append(time.perf_counter() - start)

        similarities = document_embeddings @ query_embedding
        ranked_indices = similarities.argsort()[::-1]
        ranked_ids = [DOCUMENTS[i][0] for i in ranked_indices]
        rank = ranked_ids.index(expected) + 1

        hits_at_1 += int(rank == 1)
        hits_at_3 += int(rank <= 3)
        reciprocal_ranks.append(1 / rank)

        print(f"\nQuery: {query}\nType: {query_type}")
        print(f"Expected: {expected}\nRank: {rank}")
        for index in ranked_indices[:3]:
            doc_id, text = DOCUMENTS[index]
            print(f"  {doc_id} | {similarities[index]:.4f} | {text}")

    total = len(QUERIES)
    result = {
        "model": model_name,
        "dimensions": document_embeddings.shape[1],
        "accuracy_at_1": hits_at_1 / total,
        "recall_at_3": hits_at_3 / total,
        "mrr": sum(reciprocal_ranks) / total,
        "load_time": load_time,
        "embedding_time": embedding_time,
        "avg_query_time": sum(query_times) / total,
    }
    del model
    gc.collect()
    return result


def main():
    results = [benchmark_model(name) for name in MODELS]
    print("\n" + "=" * 110)
    print("LEGALMIND MULTILINGUAL EMBEDDING BENCHMARK")
    print("=" * 110)
    print(
        f"{'Model':<38}{'Dims':>6}{'Acc@1':>10}{'R@3':>10}"
        f"{'MRR':>10}{'Embed(s)':>12}{'Query(s)':>12}"
    )
    for r in results:
        print(
            f"{r['model']:<38}{r['dimensions']:>6}"
            f"{r['accuracy_at_1']:>10.2%}{r['recall_at_3']:>10.2%}"
            f"{r['mrr']:>10.4f}{r['embedding_time']:>12.4f}"
            f"{r['avg_query_time']:>12.4f}"
        )


if __name__ == "__main__":
    main()
