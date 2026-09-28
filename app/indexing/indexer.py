from typing import Any

from app.embeddings.openai_embeddings import OpenAIEmbeddingService
from app.ingestion.models import RetrievalUnit
from app.vectorstore.pinecone_store import PineconeStore


class RetrievalUnitIndexer:

    def __init__(
            self,
            embedding_service: OpenAIEmbeddingService,
            vector_store: PineconeStore,
            batch_size: int = 100,
            namespace: str = "course-content",
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.batch_size = batch_size
        self.namespace = namespace

    @staticmethod
    def _clean_metadata(
            metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Remove None values and keep metadata Pinecone-safe.
        """

        cleaned = {}

        for key, value in metadata.items():

            if value is None:
                continue

            if isinstance(
                    value,
                    (str, int, float, bool),
            ):
                cleaned[key] = value

            elif isinstance(value, list):
                cleaned[key] = [
                    item
                    for item in value
                    if isinstance(
                        item,
                        (str, int, float, bool),
                    )
                ]

            else:
                # Avoid accidentally sending complex
                # Python objects to Pinecone.
                cleaned[key] = str(value)

        return cleaned

    def _build_metadata(
            self,
            unit: RetrievalUnit,
    ) -> dict[str, Any]:

        metadata = {
            "document_id": unit.document_id,
            "course_id": unit.course_id,

            "source_type": unit.source_type,
            "source_name": unit.source_name,
            "source_path": unit.source_path,
            "source_url": unit.source_url,

            "page_number": unit.page_number,
            "slide_number": unit.slide_number,

            "title": unit.title,
            "section": unit.section,

            "question_number": unit.question_number,
            "question": unit.question,

            # Needed later to construct LLM context
            # directly from retrieved records.
            "text": unit.text,

            **unit.metadata,
        }

        return self._clean_metadata(metadata)

    def index_units(
            self,
            units: list[RetrievalUnit],
    ) -> dict[str, int]:

        if not units:
            return {
                "units": 0,
                "batches": 0,
                "upserted": 0,
            }

        self.vector_store.ensure_index()

        total_upserted = 0
        total_batches = 0

        for start in range(
                0,
                len(units),
                self.batch_size,
        ):

            batch = units[
                start:start + self.batch_size
            ]

            texts = [
                unit.text
                for unit in batch
            ]

            embeddings = (
                self.embedding_service.embed_texts(
                    texts
                )
            )

            if len(embeddings) != len(batch):
                raise RuntimeError(
                    "Embedding count does not match "
                    "RetrievalUnit count."
                )

            vectors = []

            for unit, embedding in zip(
                    batch,
                    embeddings,
            ):
                vectors.append(
                    {
                        "id": unit.unit_id,
                        "values": embedding,
                        "metadata":
                            self._build_metadata(unit),
                    }
                )

            self.vector_store.upsert(
                vectors=vectors,
                namespace=self.namespace,
            )

            total_batches += 1
            total_upserted += len(vectors)

            print(
                f"Indexed "
                f"{total_upserted}/{len(units)} units"
            )

        return {
            "units": len(units),
            "batches": total_batches,
            "upserted": total_upserted,
        }