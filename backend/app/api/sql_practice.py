from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.sql_practice import SqlQuestion, SqlSubmission
from app.schemas.sql_practice import (
    SqlQuestionCreate,
    SqlQuestionResponse,
    SqlSubmitRequest,
    SqlSubmitResponse,
)
from app.services.sql_judge import sql_judge_service
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/api/sql-practice", tags=["sql-practice"])


@router.get("/questions", response_model=list[SqlQuestionResponse])
async def list_questions(
    chapter: str | None = None,
    difficulty: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(SqlQuestion)
    if chapter:
        query = query.where(SqlQuestion.chapter.contains(chapter))
    if difficulty:
        query = query.where(SqlQuestion.difficulty == difficulty)
    query = query.order_by(SqlQuestion.chapter, SqlQuestion.created_at)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/questions/{question_id}", response_model=SqlQuestionResponse)
async def get_question(
    question_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SqlQuestion).where(SqlQuestion.id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question


@router.post("/questions", response_model=SqlQuestionResponse)
async def create_question(
    data: SqlQuestionCreate,
    db: AsyncSession = Depends(get_db),
):
    question = SqlQuestion(**data.model_dump())
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


@router.post("/submit", response_model=dict)
async def submit_sql(
    data: SqlSubmitRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await sql_judge_service.judge(
        question_id=data.question_id,
        user_sql=data.user_sql,
        db=db,
    )

    try:
        recommendations = await recommendation_service.get_sql_practice_recommendations(
            db=db,
            question_id=data.question_id,
            is_correct=result.get("is_correct", False),
            score=result.get("score", 0),
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Generate recommendations failed: {e}")
        recommendations = []

    result["recommendations"] = recommendations
    return result


@router.get("/submissions/{question_id}", response_model=list[SqlSubmitResponse])
async def get_submissions(
    question_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SqlSubmission)
        .where(SqlSubmission.question_id == question_id)
        .order_by(SqlSubmission.created_at.desc())
    )
    return result.scalars().all()


@router.post("/generate")
async def generate_questions(
    chapter: str,
    count: int = 5,
):
    questions = await sql_judge_service.generate_questions(chapter, count)
    return {"questions": questions}
