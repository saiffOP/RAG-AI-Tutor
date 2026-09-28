from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    document_id: str
    course_id: str

    source_type: str
    source_name: str

    text: str

    source_path: str | None = None
    source_url: str | None = None

    page_number: int | None = None
    slide_number: int | None = None

    title: str | None = None
    section: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    course_id: str

    text: str

    source_type: str
    source_name: str

    source_url: str | None = None

    page_number: int | None = None
    slide_number: int | None = None

    title: str | None = None
    section: str | None = None

    chunk_index: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievalUnit:
    unit_id: str
    document_id: str
    course_id: str

    text: str

    source_type: str
    source_name: str

    source_path: str | None = None
    source_url: str | None = None

    page_number: int | None = None
    slide_number: int | None = None

    title: str | None = None
    section: str | None = None

    question_number: int | None = None
    question: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class WebSection:
    heading: str
    text: str
    heading_level: int

    course_id: str
    source_name: str
    source_url: str

    section_index: int