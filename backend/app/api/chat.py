import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sse_starlette.sse import EventSourceResponse

from app.core.database import get_db
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageResponse,
)
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    session = ChatSession(title=data.title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatSession).order_by(ChatSession.updated_at.desc())
    )
    return result.scalars().all()


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return result.scalars().all()


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    await db.execute(delete(ChatSession).where(ChatSession.id == session_id))
    await db.commit()
    return {"status": "deleted"}


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await rag_service.chat(
        message=request.message,
        session_id=request.session_id,
        db=db,
    )
    return ChatResponse(
        session_id=result["session_id"],
        answer=result["answer"],
        sources=result["sources"],
        needs_clarification=result.get("needs_clarification", False),
    )


@router.post("/ask/stream")
async def ask_question_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    async def event_generator():
        async for event in rag_service.chat_stream(
            message=request.message,
            session_id=request.session_id,
        ):
            yield {
                "event": event["type"],
                "data": event["data"],
            }

    return EventSourceResponse(event_generator())
