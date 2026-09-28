from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

    course_id: str | None = None


class SourceResponse(BaseModel):
    source_id: str
    unit_id: str
    course_id: str
    source_type: str
    source_name: str

    page_number: int | None = None
    slide_number: int | None = None
    section: str | None = None
    source_url: str | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]


class HealthResponse(BaseModel):
    status: str