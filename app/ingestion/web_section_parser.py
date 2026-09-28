import httpx
from bs4 import BeautifulSoup, Tag

from app.ingestion.models import WebSection


USER_AGENT = "Mozilla/5.0 (compatible; RAGAITutor/1.0)"


def load_web_sections(
        url: str,
        course_id: str,
) -> list[WebSection]:

    response = httpx.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
        follow_redirects=True,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # ---------------------------
    # Page title
    # ---------------------------

    page_title = (
        soup.title.get_text(" ", strip=True)
        if soup.title
        else url
    )

    # ---------------------------
    # Remove obvious noise
    # ---------------------------

    for tag in soup.find_all(
            [
                "script",
                "style",
                "noscript",
                "svg",
                "nav",
                "footer",
            ]
    ):
        tag.decompose()

    # ---------------------------
    # Locate main content
    # ---------------------------

    main = (
            soup.find("main")
            or soup.find("article")
            or soup.body
    )

    if main is None:
        return []

    sections: list[WebSection] = []

    current_heading = page_title
    current_level = 1
    current_blocks: list[str] = []

    def save_section():
        nonlocal current_blocks

        text = "\n\n".join(current_blocks).strip()

        if not text:
            return

        sections.append(
            WebSection(
                heading=current_heading,
                text=text,
                heading_level=current_level,
                course_id=course_id,
                source_name=page_title,
                source_url=url,
                section_index=len(sections),
            )
        )

        current_blocks = []

    # ---------------------------
    # Walk content in HTML order
    # ---------------------------

    for element in main.find_all(
            [
                "h1",
                "h2",
                "h3",
                "h4",
                "p",
                "li",
                "pre",
            ]
    ):

        if not isinstance(element, Tag):
            continue

        text = element.get_text(
            " ",
            strip=True,
        )

        if not text:
            continue

        if element.name in {
            "h1",
            "h2",
            "h3",
            "h4",
        }:

            # Save previous section
            save_section()

            current_heading = text.rstrip("#").strip()

            current_level = int(
                element.name[1]
            )

        else:
            # Prevent immediate duplicates
            if (
                    current_blocks
                    and current_blocks[-1] == text
            ):
                continue

            current_blocks.append(text)

    save_section()

    return sections