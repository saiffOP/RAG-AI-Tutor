import re
from typing import Any

from rank_bm25 import BM25Okapi

from app.ingestion.models import RetrievalUnit


def tokenize(text: str) -> list[str]:
    """
    Simple tokenizer for BM25 lexical retrieval.
    Keeps technical terms reasonably intact.
    """
    return re.findall(
        r"[a-zA-Z0-9_]+",
        text.lower(),
    )


class BM25Retriever:

    def __init__(
            self,
            units: list[RetrievalUnit],
    ):
        self.units = units

        self.tokenized_corpus = [
            tokenize(unit.text)
            for unit in units
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_corpus
        )

    def retrieve(
            self,
            query: str,
            top_k: int = 20,
            course_id: str | None = None,
    ) -> list[dict[str, Any]]:

        query_tokens = tokenize(query)

        scores = self.bm25.get_scores(
            query_tokens
        )

        candidates = []

        for unit, score in zip(
                self.units,
                scores,
        ):
            if (
                    course_id is not None
                    and unit.course_id != course_id
            ):
                continue

            candidates.append(
                {
                    "id": unit.unit_id,
                    "score": float(score),
                    "text": unit.text,
                    "course_id": unit.course_id,
                    "source_type": unit.source_type,
                    "source_name": unit.source_name,
                    "source_url": unit.source_url,
                    "page_number": unit.page_number,
                    "slide_number": unit.slide_number,
                    "section": unit.section,
                    "question": unit.question,
                    "metadata": unit.metadata,
                }
            )

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return candidates[:top_k]