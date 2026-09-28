from pathlib import Path

from pptx import Presentation

from app.ingestion.models import Document
from app.ingestion.cleaner import clean_pptx_text

def load_pptx(
        file_path: str | Path,
        course_id: str,
) -> list[Document]:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PPTX not found: {path}"
        )

    if path.suffix.lower() != ".pptx":
        raise ValueError(
            f"Expected a PPTX file, received: {path.suffix}"
        )

    presentation = Presentation(path)

    documents: list[Document] = []

    for slide_index, slide in enumerate(
            presentation.slides,
            start=1,
    ):

        text_blocks = []

        for shape in slide.shapes:

            if not hasattr(shape, "text"):
                continue

            text = shape.text.strip()

            if text:
                text_blocks.append(text)

        raw_text = "\n".join(text_blocks)

        slide_text = clean_pptx_text(raw_text)

        if not slide_text:
            continue

        document = Document(
            document_id=f"{course_id}:{path.stem}",
            course_id=course_id,

            source_type="slides",
            source_name=path.name,
            source_path=str(path),

            text=slide_text,

            slide_number=slide_index,
        )

        documents.append(document)

    return documents