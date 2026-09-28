from collections import Counter
from pathlib import Path

import pymupdf

from app.ingestion.cleaner import clean_text
from app.ingestion.models import Document


def load_pdf(
        file_path: str | Path,
        course_id: str,
) -> list[Document]:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file, received: {path.suffix}"
        )

    pdf = pymupdf.open(path)

    try:
        page_texts = []

        for page in pdf:
            raw_text = page.get_text("text")
            text = clean_text(raw_text)

            page_texts.append(text)

        # --------------------------------
        # Detect repeated first-line header
        # --------------------------------

        first_lines = []

        for text in page_texts:

            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]

            if lines:
                first_lines.append(lines[0])

        counts = Counter(first_lines)

        repeated_headers = {
            line
            for line, count in counts.items()
            if count >= 2
        }

        # --------------------------------
        # Create Documents
        # --------------------------------

        documents = []

        for page_index, text in enumerate(
                page_texts,
                start=1,
        ):

            lines = text.splitlines()

            if (
                    lines
                    and lines[0].strip()
                    in repeated_headers
            ):
                lines = lines[1:]

            text = "\n".join(lines).strip()

            if not text:
                continue

            documents.append(
                Document(
                    document_id=(
                        f"{course_id}:{path.stem}"
                    ),
                    course_id=course_id,

                    source_type="pdf",
                    source_name=path.name,
                    source_path=str(path),

                    text=text,

                    page_number=page_index,
                )
            )

        return documents

    finally:
        pdf.close()