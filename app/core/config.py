import os

from dotenv import load_dotenv


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

OPENAI_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)

PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "rag-ai-tutor",
)


if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not configured."
    )

if not PINECONE_API_KEY:
    raise RuntimeError(
        "PINECONE_API_KEY is not configured."
    )
PINECONE_CLOUD = os.getenv(
    "PINECONE_CLOUD",
    "aws",
)

PINECONE_REGION = os.getenv(
    "PINECONE_REGION",
    "us-east-1",
)

EMBEDDING_DIMENSION = 1536