from typing import Any

from app.retrieval.hybrid_retriever import (
    HybridRetriever,
)
from app.retrieval.reranker import (
    CrossEncoderReranker,
)


class RetrievalPipeline:

    def __init__(
            self,
            hybrid_retriever: HybridRetriever,
            reranker: CrossEncoderReranker,
    ):
        self.hybrid_retriever = (
            hybrid_retriever
        )

        self.reranker = reranker

    def retrieve(
            self,
            query: str,
            candidate_k: int = 20,
            fusion_k: int = 15,
            final_k: int = 5,
            course_id: str | None = None,
    ) -> list[dict[str, Any]]:

        # Stage 1:
        # Dense + BM25 + RRF
        candidates = (
            self.hybrid_retriever.retrieve(
                query=query,
                candidate_k=candidate_k,
                top_k=fusion_k,
                course_id=course_id,
            )
        )

        # Stage 2:
        # Cross-encoder reranking
        results = self.reranker.rerank(
            query=query,
            candidates=candidates,
            top_k=final_k,
        )

        return results