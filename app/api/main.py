from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
)

from app.api.schemas import (
    AskRequest,
    AskResponse,
    HealthResponse,
)
from app.embeddings.openai_embeddings import (
    OpenAIEmbeddingService,
)
from app.generation.generator import (
    RAGGenerator,
)
from app.rag.service import (
    RAGService,
)
from app.retrieval.bm25_retriever import (
    BM25Retriever,
)
from app.retrieval.hybrid_retriever import (
    HybridRetriever,
)
from app.retrieval.retriever import (
    SemanticRetriever,
)
from app.storage.corpus_store import (
    load_retrieval_units,
)
from app.vectorstore.pinecone_store import (
    PineconeStore,
)


rag_service: RAGService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    global rag_service

    print("=" * 80)
    print("STARTING RAG AI TUTOR")
    print("=" * 80)

    # --------------------------------------------------
    # Load persisted corpus
    # --------------------------------------------------

    print("Loading retrieval corpus...")

    units = load_retrieval_units()

    print(
        f"Loaded {len(units)} retrieval units."
    )

    # --------------------------------------------------
    # OpenAI embeddings
    # --------------------------------------------------

    print("Initializing embedding service...")

    embedding_service = (
        OpenAIEmbeddingService()
    )

    # --------------------------------------------------
    # Pinecone
    # --------------------------------------------------

    print("Connecting to Pinecone...")

    vector_store = PineconeStore()

    vector_store.ensure_index()

    # --------------------------------------------------
    # Dense retriever
    # --------------------------------------------------

    semantic_retriever = SemanticRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # --------------------------------------------------
    # BM25
    # --------------------------------------------------

    print("Building BM25 index...")

    bm25_retriever = BM25Retriever(
        units=units
    )

    # --------------------------------------------------
    # Hybrid retrieval
    # --------------------------------------------------

    hybrid_retriever = HybridRetriever(
        semantic_retriever=semantic_retriever,
        bm25_retriever=bm25_retriever,
    )

    # --------------------------------------------------
    # Generator
    # --------------------------------------------------

    generator = RAGGenerator()

    # --------------------------------------------------
    # Complete RAG service
    # --------------------------------------------------

    rag_service = RAGService(
        retriever=hybrid_retriever,
        generator=generator,
    )

    print("=" * 80)
    print("RAG AI TUTOR READY")
    print("=" * 80)

    yield

    rag_service = None

    print("RAG AI Tutor stopped.")


app = FastAPI(
    title="RAG AI Tutor",
    description=(
        "Hybrid retrieval-based AI tutor for "
        "machine learning course content."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health():
    return {
        "status": "healthy"
    }


@app.post(
    "/ask",
    response_model=AskResponse,
)
def ask(request: AskRequest):

    if rag_service is None:
        raise HTTPException(
            status_code=503,
            detail="RAG service is not ready.",
        )

    try:
        return rag_service.ask(
            question=request.question,
            course_id=request.course_id,
            top_k=5,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"RAG request failed: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate an answer."
            ),
        ) from exc