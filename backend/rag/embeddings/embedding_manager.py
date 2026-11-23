from sentence_transformers import SentenceTransformer


class EmbeddingManager:

    MODEL_NAME = "intfloat/multilingual-e5-small"
    DIMENSIONS = 384
    BATCH_SIZE = 32

    def __init__(self):
        self.model = SentenceTransformer(
            self.MODEL_NAME,
            device="cpu"
        )

    def generate_embedding(self, text: str):

        embedding = self.model.encode(
            f"query: {text}",
            normalize_embeddings=True
        )

        return embedding.tolist()

    def generate_embeddings(self, texts: list[str]):

        passages = [
            f"passage: {text}"
            for text in texts
        ]

        embeddings = self.model.encode(
            passages,
            normalize_embeddings=True,
            batch_size=self.BATCH_SIZE,
            show_progress_bar=True
        )

        return embeddings.tolist()