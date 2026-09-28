import os

from openai import OpenAI

from app.generation.context_builder import (
    build_context,
)


SYSTEM_PROMPT = """
You are an AI tutor.

Answer the user's question using only the provided course context.

Rules:
1. Do not use outside knowledge.
2. If the context does not contain enough information to answer the
   question, clearly say that the available course material does not
   provide enough information.
3. Do not invent facts, examples, citations, page numbers, or sources.
4. Explain the answer clearly and directly.
5. Cite supporting sources using their source IDs, for example [S1]
   or [S2].
6. Place citations immediately after the claims they support.
7. Use only source IDs that appear in the provided context.
"""


class RAGGenerator:

    def __init__(
            self,
            model: str = "gpt-5.4",
    ):
        self.client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"]
        )

        self.model = model

    def generate(
            self,
            query: str,
            results: list[dict],
    ) -> str:

        if not results:
            return (
                "I couldn't find relevant course "
                "material for this question."
            )

        context = build_context(results)

        user_prompt = f"""
USER QUESTION:

{query}


COURSE CONTEXT:

{context}


Answer the user's question using only the course context above.
"""

        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_PROMPT,
            input=user_prompt,
        )

        return response.output_text