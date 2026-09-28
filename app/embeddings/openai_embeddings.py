from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

from app.core.config import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
)


class OpenAIEmbeddingService:

    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        self.model = OPENAI_EMBEDDING_MODEL

    @retry(
        wait=wait_random_exponential(
            min=1,
            max=20,
        ),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def embed_texts(
            self,
            texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        # Explicitly preserve API ordering
        ordered = sorted(
            response.data,
            key=lambda item: item.index,
        )

        return [
            item.embedding
            for item in ordered
        ]

    def embed_query(
            self,
            query: str,
    ) -> list[float]:

        embeddings = self.embed_texts(
            [query]
        )

        return embeddings[0]