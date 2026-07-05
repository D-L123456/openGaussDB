from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("")
async def get_recommendations(db: AsyncSession = Depends(get_db)):
    recommendations = await recommendation_service.get_recommendations(db)
    return {"recommendations": recommendations}