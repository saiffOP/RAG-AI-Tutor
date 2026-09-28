from typing import Any

from app.generation.generator import (
    RAGGenerator,
)
from app.retrieval.hybrid_retriever import (
    HybridRetriever,
)


class RAGService:

    def __init__(
            self,
            retriever: HybridRetriever,
            generator: RAGGenerator,
    ):
        self.retriever = retriever
        self.generator = generator

    def ask(
            self,
            question: str,
            course_id: str | None = None,
            top_k: int = 5,
    ) -> dict[str, Any]:

        question = question.strip()

        if not question:
            raise ValueError(
                "Question cannot be empty."
            )

        # ---------------------------------------
        # Retrieve evidence
        # ---------------------------------------

        results = self.retriever.retrieve(
            query=question,
            candidate_k=20,
            top_k=top_k,
            course_id=course_id,
        )

        # ---------------------------------------
        # Generate grounded answer
        # ---------------------------------------

        answer = self.generator.generate(
            query=question,
            results=results,
        )

        # ---------------------------------------
        # Build source response
        # ---------------------------------------

        sources = []

        for index, result in enumerate(
                results,
                start=1,
        ):
            sources.append(
                {
                    "source_id": f"S{index}",
                    "unit_id": result["id"],
                    "course_id": result["course_id"],
                    "source_type": result["source_type"],
                    "source_name": result["source_name"],
                    "page_number": result.get(
                        "page_number"
                    ),
                    "slide_number": result.get(
                        "slide_number"
                    ),
                    "section": result.get(
                        "section"
                    ),
                    "source_url": result.get(
                        "source_url"
                    ),
                }
            )

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }