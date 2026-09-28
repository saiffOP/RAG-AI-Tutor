from app.embeddings.openai_embeddings import (
    OpenAIEmbeddingService,
)
from app.indexing.indexer import (
    RetrievalUnitIndexer,
)
from app.ingestion.pipeline import (
    ingest_all_courses,
)
from app.vectorstore.pinecone_store import (
    PineconeStore,
)
from app.storage.corpus_store import (
    save_retrieval_units,
)


def main():

    print("=" * 80)
    print("RAG AI TUTOR - KNOWLEDGE BASE INDEXING")
    print("=" * 80)

    # --------------------------------------------------
    # 1. Ingest all sources
    # --------------------------------------------------

    print("\n[1/4] Ingesting course content...\n")

    units = ingest_all_courses()

    if not units:
        print("No retrieval units found.")
        return

    save_retrieval_units(units)

    print(
        f"\nTotal retrieval units: {len(units)}"
    )

    # --------------------------------------------------
    # 2. Initialize embedding service
    # --------------------------------------------------

    print("\n[2/4] Initializing OpenAI embeddings...")

    embedding_service = OpenAIEmbeddingService()

    # --------------------------------------------------
    # 3. Initialize Pinecone
    # --------------------------------------------------

    print("\n[3/4] Connecting to Pinecone...")

    vector_store = PineconeStore()

    vector_store.ensure_index()

    print("Pinecone index ready.")

    # --------------------------------------------------
    # 4. Embed + index
    # --------------------------------------------------

    print("\n[4/4] Embedding and indexing units...\n")

    indexer = RetrievalUnitIndexer(
        embedding_service=embedding_service,
        vector_store=vector_store,
        batch_size=50,
        namespace="course-content",
    )

    stats = indexer.index_units(
        units
    )

    print("\n" + "=" * 80)
    print("INDEXING COMPLETE")
    print("=" * 80)

    print(
        f"Retrieval units : {stats['units']}"
    )

    print(
        f"Batches         : {stats['batches']}"
    )

    print(
        f"Vectors upserted: {stats['upserted']}"
    )

    print(
        "Namespace       : course-content"
    )


if __name__ == "__main__":
    main()