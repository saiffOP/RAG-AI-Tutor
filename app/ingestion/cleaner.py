import re

from app.ingestion.models import Document


def clean_text(text: str) -> str:

    # Normalize Windows/newline variants
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove our generated PDF header
    text = re.sub(
        r"^RAG AI TUTOR\s*/\s*[A-Z0-9]+\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Remove generated handout footer
    text = re.sub(
        r"^.+?\s*\|\s*Learning handout\s*$",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Remove standalone page-number lines
    text = re.sub(
        r"^Page\s+\d+\s*$",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Collapse spaces/tabs, but preserve newlines
    text = re.sub(r"[ \t]+", " ", text)

    # Maximum two consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_document(document: Document) -> Document:

    document.text = clean_text(document.text)

    return document

def clean_pptx_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Example:
    # ML101 / ML101-01_ML_Fundamentals
    text = re.sub(
        r"^[A-Z0-9]+\s*/\s*[A-Za-z0-9_-]+\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Example:
    # ML101-01_ML_Fundamentals · slide 06
    text = re.sub(
        r"^[A-Za-z0-9_-]+\s*[·•]\s*slide\s+\d+\s*$",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_web_blocks(
        blocks: list[str],
) -> list[str]:

    cleaned = []

    previous = None

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        # Skip immediately repeated blocks
        if block == previous:
            continue

        cleaned.append(block)

        previous = block

    return cleaned