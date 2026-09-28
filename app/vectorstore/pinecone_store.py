import time
from typing import Any

from pinecone import Pinecone, ServerlessSpec

from app.core.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD,
    PINECONE_REGION,
    EMBEDDING_DIMENSION,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from pinecone.exceptions import PineconeException


class PineconeStore:

    def __init__(self):

        self.client = Pinecone(
            api_key=PINECONE_API_KEY
        )

        self.index_name = PINECONE_INDEX_NAME
        self.index = None

    def ensure_index(self) -> None:
        """
        Create the Pinecone index if it does not exist.
        """

        existing_indexes = {
            index.name
            for index in self.client.list_indexes()
        }

        if self.index_name not in existing_indexes:

            print(
                f"Creating Pinecone index: "
                f"{self.index_name}"
            )

            self.client.create_index(
                name=self.index_name,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_REGION,
                ),
            )

        self._wait_until_ready()

        description = self.client.describe_index(
            self.index_name
        )

        # Important safety check.
        if description.dimension != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Pinecone index dimension "
                f"is {description.dimension}, "
                f"but embedding dimension is "
                f"{EMBEDDING_DIMENSION}."
            )

        self.index = self.client.Index(
            host=description.host
        )

    def _wait_until_ready(
            self,
            timeout: int = 120,
    ) -> None:

        started = time.time()

        while True:

            description = self.client.describe_index(
                self.index_name
            )

            if description.status.ready:
                return

            if time.time() - started > timeout:
                raise TimeoutError(
                    "Timed out waiting for "
                    "Pinecone index."
                )

            time.sleep(2)

    @retry(
        retry=retry_if_exception_type(PineconeException),
        wait=wait_random_exponential(
            min=1,
            max=20,
        ),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def upsert(
            self,
            vectors: list[dict[str, Any]],
            namespace: str,
    ) -> None:

        if not vectors:
            return

        if self.index is None:
            raise RuntimeError(
                "Pinecone index has not been initialized."
            )

        self.index.upsert(
            vectors=vectors,
            namespace=namespace,
            timeout=60,
        )

        def query(
                self,
                vector: list[float],
                namespace: str,
                top_k: int = 5,
                filters: dict | None = None,
        ):

            if self.index is None:
                raise RuntimeError(
                    "Pinecone index has not been initialized."
                )

            return self.index.query(
                vector=vector,
                namespace=namespace,
                top_k=top_k,
                include_metadata=True,
                filter=filters,
            )
    def query(
            self,
            vector: list[float],
            namespace: str,
            top_k: int = 5,
            filters: dict | None = None,
    ):
        """
        Query Pinecone for the most similar vectors.
        """

        if self.index is None:
            raise RuntimeError(
                "Pinecone index has not been initialized."
            )

        return self.index.query(
            vector=vector,
            namespace=namespace,
            top_k=top_k,
            include_metadata=True,
            filter=filters,
        )