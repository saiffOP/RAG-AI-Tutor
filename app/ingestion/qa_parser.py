import re

from app.ingestion.models import Document, RetrievalUnit


QUESTION_PATTERN = re.compile(
    r"(?m)^(\d{1,3})\.\s+(.+?)\s*$"
)


def extract_qa_units(
        documents: list[Document],
) -> list[RetrievalUnit]:

    if not documents:
        return []

    combined_parts = []
    page_ranges = []

    current_position = 0

    for document in documents:

        text = document.text.strip()

        if not text:
            continue

        start = current_position
        end = start + len(text)

        combined_parts.append(text)

        page_ranges.append(
            {
                "start": start,
                "end": end,
                "page_number": document.page_number,
            }
        )

        # +2 because we join pages with "\n\n"
        current_position = end + 2

    combined_text = "\n\n".join(combined_parts)

    matches = list(
        QUESTION_PATTERN.finditer(combined_text)
    )

    units = []

    base_document = documents[0]

    for index, match in enumerate(matches):

        question_number = int(match.group(1))
        question = match.group(2).strip()

        answer_start = match.end()

        if index + 1 < len(matches):
            unit_end = matches[index + 1].start()
        else:
            unit_end = len(combined_text)

        answer = combined_text[
            answer_start:unit_end
        ].strip()

        if not answer:
            continue

        start_position = match.start()

        pages = [
            page["page_number"]
            for page in page_ranges
            if (
                    page["end"] > start_position
                    and page["start"] < unit_end
            )
        ]

        pages = [
            page
            for page in pages
            if page is not None
        ]

        start_page = min(pages) if pages else None
        end_page = max(pages) if pages else None

        text = (
            f"Question: {question}\n\n"
            f"Answer: {answer}"
        )

        unit = RetrievalUnit(
            unit_id=(
                f"{base_document.document_id}"
                f":q{question_number}"
            ),

            document_id=base_document.document_id,
            course_id=base_document.course_id,

            text=text,

            source_type="pdf",
            source_name=base_document.source_name,
            source_path=base_document.source_path,

            page_number=start_page,

            question_number=question_number,
            question=question,

            metadata={
                **base_document.metadata,
                "content_type": "qa",
                "start_page": start_page,
                "end_page": end_page,
            },
        )

        units.append(unit)

    return units