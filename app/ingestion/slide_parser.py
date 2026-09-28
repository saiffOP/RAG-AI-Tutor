from app.ingestion.models import Document, RetrievalUnit


def create_slide_units(
        documents: list[Document],
) -> list[RetrievalUnit]:

    units: list[RetrievalUnit] = []

    for document in documents:

        if not document.text.strip():
            continue

        unit = RetrievalUnit(
            unit_id=(
                f"{document.document_id}"
                f":slide{document.slide_number}"
            ),
            document_id=document.document_id,
            course_id=document.course_id,

            text=document.text,

            source_type=document.source_type,
            source_name=document.source_name,
            source_path=document.source_path,

            slide_number=document.slide_number,

            title=document.title,
            section=document.section,

            metadata={
                **document.metadata,
                "content_type": "slide",
            },
        )

        units.append(unit)

    return units