from typing import Any

from app.retrieval.bm25_retriever import (
    BM25Retriever,
)
from app.retrieval.fusion import (
    reciprocal_rank_fusion,
)
from app.retrieval.retriever import (
    SemanticRetriever,
)


class HybridRetriever:

    def __init__(
            self,
            semantic_retriever: SemanticRetriever,
            bm25_retriever: BM25Retriever,
    ):
        self.semantic_retriever = semantic_retriever
        self.bm25_retriever = bm25_retriever

    def retrieve(
            self,
            query: str,
            candidate_k: int = 20,
            top_k: int = 15,
            course_id: str | None = None,
    ) -> list[dict[str, Any]]:

        # ---------------------------------------
        # Dense / semantic retrieval
        # ---------------------------------------

        filters = None

        if course_id:
            filters = {
                "course_id": {
                    "$eq": course_id
                }
            }

        dense_results = (
            self.semantic_retriever.retrieve(
                query=query,
                top_k=candidate_k,
                filters=filters,
            )
        )

        # ---------------------------------------
        # BM25 lexical retrieval
        # ---------------------------------------

        bm25_results = (
            self.bm25_retriever.retrieve(
                query=query,
                top_k=candidate_k,
                course_id=course_id,
            )
        )

        # ---------------------------------------
        # RRF
        # ---------------------------------------

        fused_results = (
            reciprocal_rank_fusion(
                result_lists=[
                    dense_results,
                    bm25_results,
                ],
                top_k=top_k,
            )
        )

        return fused_results