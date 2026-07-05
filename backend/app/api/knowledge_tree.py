from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.knowledge import (
    KnowledgeNodeResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
)
from app.services.knowledge_tree import knowledge_tree_service
from app.services.vector_store import vector_store

router = APIRouter(prefix="/api/knowledge-tree", tags=["knowledge-tree"])


@router.get("/tree")
async def get_knowledge_tree(db: AsyncSession = Depends(get_db)):
    tree = await knowledge_tree_service.get_tree(db)
    return {"nodes": tree}


@router.post("/search", response_model=list[KnowledgeSearchResult])
async def search_knowledge(request: KnowledgeSearchRequest):
    results = await knowledge_tree_service.search_knowledge(
        query=request.query,
        top_k=request.top_k,
    )
    return results


@router.get("/chapters")
async def list_chapters():
    metadata = vector_store.get_all_metadata()
    chapters = {}
    for meta in metadata:
        chapter = meta.get("chapter", "")
        section = meta.get("section", "")
        if chapter not in chapters:
            chapters[chapter] = []
        if section and section not in chapters[chapter]:
            chapters[chapter].append(section)
    return chapters


@router.get("/stats")
async def get_stats():
    return {
        "total_documents": vector_store.count(),
        "chapters": len(vector_store.get_all_metadata()),
    }