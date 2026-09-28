from typing import Any


def build_context(
        results: list[dict[str, Any]],
) -> str:

    context_blocks = []

    for index, result in enumerate(
            results,
            start=1,
    ):
        source_label = f"S{index}"

        source_info = [
            f"Source ID: {source_label}",
            f"Course: {result.get('course_id')}",
            f"Source Type: {result.get('source_type')}",
            f"Source: {result.get('source_name')}",
        ]

        if result.get("page_number") is not None:
            source_info.append(
                f"Page: {result['page_number']}"
            )

        if result.get("slide_number") is not None:
            source_info.append(
                f"Slide: {result['slide_number']}"
            )

        if result.get("section"):
            source_info.append(
                f"Section: {result['section']}"
            )

        if result.get("source_url"):
            source_info.append(
                f"URL: {result['source_url']}"
            )

        header = "\n".join(source_info)

        block = (
            f"[{source_label}]\n"
            f"{header}\n\n"
            f"{result['text']}"
        )

        context_blocks.append(block)

    return "\n\n" + ("\n\n" + "-" * 80 + "\n\n").join(
        context_blocks
    )