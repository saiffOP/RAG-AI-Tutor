import json
from pathlib import Path

from app.ingestion.models import RetrievalUnit


DEFAULT_CORPUS_PATH = Path(
    "data/index/retrieval_units.json"
)


def save_retrieval_units(
        units: list[RetrievalUnit],
        path: Path = DEFAULT_CORPUS_PATH,
) -> None:
    """
    Persist processed retrieval units.

    This corpus is used by BM25 at runtime so that
    source documents do not need to be ingested again.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = []

    for unit in units:
        data.append(
            {
                "unit_id": unit.unit_id,
                "document_id": unit.document_id,
                "course_id": unit.course_id,
                "source_type": unit.source_type,
                "source_name": unit.source_name,
                "text": unit.text,
                "source_url": unit.source_url,
                "page_number": unit.page_number,
                "slide_number": unit.slide_number,
                "section": unit.section,
                "question": unit.question,
                "metadata": unit.metadata,
            }
        )

    with path.open(
            "w",
            encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"Saved {len(units)} retrieval units "
        f"to {path}"
    )


def load_retrieval_units(
        path: Path = DEFAULT_CORPUS_PATH,
) -> list[RetrievalUnit]:
    """
    Load the persisted retrieval corpus.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Retrieval corpus not found: {path}. "
            f"Run the indexing pipeline first."
        )

    with path.open(
            "r",
            encoding="utf-8",
    ) as file:
        data = json.load(file)

    units = [
        RetrievalUnit(**item)
        for item in data
    ]

    return units