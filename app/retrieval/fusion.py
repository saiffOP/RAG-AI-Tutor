from typing import Any


def reciprocal_rank_fusion(
        result_lists: list[list[dict[str, Any]]],
        k: int = 60,
        top_k: int = 20,
) -> list[dict[str, Any]]:
    """
    Combine multiple ranked result lists using
    Reciprocal Rank Fusion.
    """

    fused: dict[str, dict[str, Any]] = {}

    for results in result_lists:

        for rank, result in enumerate(
                results,
                start=1,
        ):
            document_id = result["id"]

            if document_id not in fused:
                fused[document_id] = {
                    **result,
                    "rrf_score": 0.0,
                }

            fused[document_id]["rrf_score"] += (
                    1.0 / (k + rank)
            )

    ranked = sorted(
        fused.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return ranked[:top_k]