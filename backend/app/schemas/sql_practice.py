from datetime import datetime

from pydantic import BaseModel


class SqlQuestionCreate(BaseModel):
    chapter: str
    title: str
    description: str
    difficulty: str = "medium"
    hint: str | None = None
    reference_sql: str
    setup_sql: str | None = None

    tags: dict | None = None


class SqlQuestionResponse(BaseModel):
    id: str
    chapter: str
    title: str
    description: str
    difficulty: str
    hint: str | None = None
    reference_sql: str | None = None
    setup_sql: str | None = None
    tags: dict | None = None

    model_config = {"from_attributes": True}


class SqlSubmitRequest(BaseModel):
    question_id: str
    user_sql: str


class SqlSubmitResponse(BaseModel):
    id: str
    question_id: str
    user_sql: str
    is_correct: bool
    score: float
    feedback: str | None = None
    execution_result: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
