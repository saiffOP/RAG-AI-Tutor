from typing import Any

from app.embeddings.openai_embeddings import (
    OpenAIEmbeddingService,
)
from app.vectorstore.pinecone_store import (
    PineconeStore,
)


class SemanticRetriever:

    def __init__(
            self,
            embedding_service: OpenAIEmbeddingService,
            vector_store: PineconeStore,
            namespace: str = "course-content",
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.namespace = namespace

    def retrieve(
            self,
            query: str,
            top_k: int = 5,
            filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:

        query = query.strip()

        if not query:
            return []

        # Convert user question into the same vector space
        # as our indexed course content.
        query_vector = (
            self.embedding_service.embed_query(query)
        )

        response = self.vector_store.query(
            vector=query_vector,
            namespace=self.namespace,
            top_k=top_k,
            filters=filters,
        )

        results = []

        for match in response.matches:

            metadata = match.metadata or {}

            results.append(
                {
                    "id": match.id,
                    "score": float(match.score),
                    "text": metadata.get(
                        "text",
                        "",
                    ),
                    "course_id": metadata.get(
                        "course_id"
                    ),
                    "source_type": metadata.get(
                        "source_type"
                    ),
                    "source_name": metadata.get(
                        "source_name"
                    ),
                    "source_url": metadata.get(
                        "source_url"
                    ),
                    "page_number": metadata.get(
                        "page_number"
                    ),
                    "slide_number": metadata.get(
                        "slide_number"
                    ),
                    "section": metadata.get(
                        "section"
                    ),
                    "question": metadata.get(
                        "question"
                    ),
                    "metadata": metadata,
                }
            )

        return results