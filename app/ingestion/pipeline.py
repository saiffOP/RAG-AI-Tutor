from pathlib import Path

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.pptx_loader import load_pptx
from app.ingestion.qa_parser import extract_qa_units
from app.ingestion.slide_parser import create_slide_units
from app.ingestion.web_section_parser import load_web_sections
from app.ingestion.web_unit_builder import create_web_units
from app.ingestion.models import RetrievalUnit


def ingest_course(
        course_dir: Path,
) -> list[RetrievalUnit]:

    course_id = course_dir.name

    units: list[RetrievalUnit] = []

    # ==================================================
    # PDFs
    # ==================================================

    pdf_dir = course_dir / "pdf"

    if pdf_dir.exists():

        for pdf_path in sorted(
                pdf_dir.glob("*.pdf")
        ):

            print(
                f"[PDF] {course_id}: "
                f"{pdf_path.name}"
            )

            documents = load_pdf(
                pdf_path,
                course_id=course_id,
            )

            pdf_units = extract_qa_units(
                documents
            )

            units.extend(pdf_units)

    # ==================================================
    # Slides
    # ==================================================

    slides_dir = course_dir / "slides"

    if slides_dir.exists():

        for pptx_path in sorted(
                slides_dir.glob("*.pptx")
        ):

            print(
                f"[PPTX] {course_id}: "
                f"{pptx_path.name}"
            )

            documents = load_pptx(
                pptx_path,
                course_id=course_id,
            )

            slide_units = create_slide_units(
                documents
            )

            units.extend(slide_units)

    # ==================================================
    # URLs
    # ==================================================

    urls_file = course_dir / "urls.txt"

    if urls_file.exists():

        urls = [
            line.strip()
            for line in urls_file.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
               and not line.strip().startswith("#")
        ]

        for url in urls:

            print(
                f"[WEB] {course_id}: {url}"
            )

            sections = load_web_sections(
                url=url,
                course_id=course_id,
            )

            web_units = create_web_units(
                sections
            )

            units.extend(web_units)

    return units

def ingest_all_courses(
        data_dir: str | Path = "data",
) -> list[RetrievalUnit]:

    data_path = Path(data_dir)

    if not data_path.exists():
        raise FileNotFoundError(
            f"Data directory not found: {data_path}"
        )

    units: list[RetrievalUnit] = []

    for course_dir in sorted(data_path.iterdir()):

        if not course_dir.is_dir():
            continue

        course_units = ingest_course(
            course_dir
        )

        print(
            f"{course_dir.name}: "
            f"{len(course_units)} retrieval units"
        )

        units.extend(course_units)

    return units