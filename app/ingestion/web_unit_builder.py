from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ingestion.models import (
    WebSection,
    RetrievalUnit,
)
from app.chunking.tokenizer import count_tokens
import hashlib


MAX_SECTION_TOKENS = 500


text_splitter = (
    RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=500,
        chunk_overlap=50,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )
)

def _url_hash(url: str) -> str:
    return hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()[:12]


def create_web_units(
        sections: list[WebSection],
) -> list[RetrievalUnit]:

    units: list[RetrievalUnit] = []

    for section in sections:
        url_hash = _url_hash(
            section.source_url
        )

        section_tokens = count_tokens(
            section.text
        )

        # Preserve naturally small sections
        if section_tokens <= MAX_SECTION_TOKENS:

            parts = [section.text]

        else:

            parts = text_splitter.split_text(
                section.text
            )

        for part_index, part in enumerate(parts):

            # Include heading in every resulting unit
            text = (
                f"{section.heading}\n\n"
                f"{part}"
            )

            units.append(
                RetrievalUnit(
                    unit_id=(
                        f"{section.course_id}:web:"
                        f"{url_hash}:"
                        f"s{section.section_index}:"
                        f"p{part_index}"
                    ),

                    document_id=(
                        f"{section.course_id}:web:"
                        f"{url_hash}"
                    ),

                    course_id=section.course_id,

                    text=text,

                    source_type="web",
                    source_name=section.source_name,
                    source_url=section.source_url,

                    title=section.source_name,
                    section=section.heading,

                    metadata={
                        "content_type": "web_section",
                        "heading_level":
                            section.heading_level,
                        "section_index":
                            section.section_index,
                        "part_index":
                            part_index,
                        "section_tokens":
                            section_tokens,
                    },
                )
            )

    return units