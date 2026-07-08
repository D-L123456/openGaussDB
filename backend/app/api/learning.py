from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.learning import LearningEvent, UserProfile, LearningRecommendation, ErrorPattern, AbilitySnapshot
from app.services.learning_tracker import learning_tracker
from app.services.profile_engine import profile_engine
from app.schemas.learning import (
    LearningEventCreate,
    LearningEventResponse,
    UserProfileResponse,
    RecommendationResponse,
    ErrorPatternResponse,
    AbilitySnapshotResponse,
    LearningDashboardResponse,
)

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.post("/events", response_model=LearningEventResponse)
async def create_event(
    data: LearningEventCreate,
    db: AsyncSession = Depends(get_db),
):
    event = await learning_tracker.record_event(
        db=db,
        user_id="default_user",
        event_type=data.event_type,
        level=data.level,
        part=data.part,
        detail=data.detail,
        duration_seconds=data.duration_seconds,
    )
    return LearningEventResponse(
        id=event.id,
        event_type=event.event_type,
        level=event.level,
        part=event.part,
        detail=event.detail,
        duration_seconds=event.duration_seconds,
        created_at=event.created_at.isoformat() if event.created_at else "",
    )


@router.get("/events", response_model=list[LearningEventResponse])
async def list_events(
    event_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    events, total = await learning_tracker.get_events(
        db, "default_user", event_type=event_type, limit=limit, offset=offset
    )
    return [
        LearningEventResponse(
            id=e.id,
            event_type=e.event_type,
            level=e.level,
            part=e.part,
            detail=e.detail,
            duration_seconds=e.duration_seconds,
            created_at=e.created_at.isoformat() if e.created_at else "",
        )
        for e in events
    ]


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    profile = await learning_tracker.get_profile(db, "default_user")
    return UserProfileResponse(
        user_id=profile.user_id,
        ability_scores=profile.ability_scores or {},
        weak_points=profile.weak_points,
        error_patterns=profile.error_patterns,
        learning_style=profile.learning_style or "undetermined",
        total_learning_time=profile.total_learning_time or 0,
        streak_days=profile.streak_days or 0,
        last_active_at=profile.last_active_at.isoformat() if profile.last_active_at else None,
        challenge_progress=profile.challenge_progress,
        badges=profile.badges,
    )


@router.get("/recommendations", response_model=list[RecommendationResponse])
async def get_recommendations(
    refresh: bool = False,
    db: AsyncSession = Depends(get_db),
):
    if refresh:
        recs = await profile_engine.analyze_and_recommend(db, "default_user")
    else:
        recs = await profile_engine.get_active_recommendations(db, "default_user")

    return [
        RecommendationResponse(
            id=r.id,
            rec_type=r.rec_type,
            title=r.title,
            description=r.description,
            priority=r.priority,
            action_type=r.action_type,
            action_target=r.action_target,
            is_read=r.is_read,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in recs
    ]


@router.put("/recommendations/{rec_id}/read")
async def mark_recommendation_read(rec_id: str, db: AsyncSession = Depends(get_db)):
    rec = await profile_engine.mark_recommendation_read(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"status": "ok"}


@router.put("/recommendations/{rec_id}/dismiss")
async def dismiss_recommendation(rec_id: str, db: AsyncSession = Depends(get_db)):
    rec = await profile_engine.dismiss_recommendation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"status": "ok"}


@router.get("/error-patterns", response_model=list[ErrorPatternResponse])
async def get_error_patterns(db: AsyncSession = Depends(get_db)):
    patterns = await learning_tracker.get_error_patterns(db, "default_user")
    return [
        ErrorPatternResponse(
            id=p.id,
            category=p.category,
            description=p.description,
            occurrence_count=p.occurrence_count,
            ability_dim=p.ability_dim,
            last_seen_at=p.last_seen_at.isoformat() if p.last_seen_at else "",
        )
        for p in patterns
    ]


@router.get("/ability-history", response_model=list[AbilitySnapshotResponse])
async def get_ability_history(
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
):
    snapshots = await learning_tracker.get_ability_history(db, "default_user", limit=limit)
    return [
        AbilitySnapshotResponse(
            id=s.id,
            ability_scores=s.ability_scores,
            trigger_event=s.trigger_event,
            created_at=s.created_at.isoformat() if s.created_at else "",
        )
        for s in snapshots
    ]


@router.get("/timeline")
async def get_timeline(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    timeline = await learning_tracker.get_timeline(db, "default_user", days=days)
    return {"events": timeline, "total_count": len(timeline)}


@router.get("/dashboard", response_model=LearningDashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    profile = await learning_tracker.get_profile(db, "default_user")
    recommendations = await profile_engine.get_active_recommendations(db, "default_user")
    error_patterns = await learning_tracker.get_error_patterns(db, "default_user")
    ability_history = await learning_tracker.get_ability_history(db, "default_user", limit=30)
    timeline = await learning_tracker.get_timeline(db, "default_user", days=30)

    return LearningDashboardResponse(
        profile=UserProfileResponse(
            user_id=profile.user_id,
            ability_scores=profile.ability_scores or {},
            weak_points=profile.weak_points,
            error_patterns=profile.error_patterns,
            learning_style=profile.learning_style or "undetermined",
            total_learning_time=profile.total_learning_time or 0,
            streak_days=profile.streak_days or 0,
            last_active_at=profile.last_active_at.isoformat() if profile.last_active_at else None,
            challenge_progress=profile.challenge_progress,
            badges=profile.badges,
        ),
        recent_recommendations=[
            RecommendationResponse(
                id=r.id,
                rec_type=r.rec_type,
                title=r.title,
                description=r.description,
                priority=r.priority,
                action_type=r.action_type,
                action_target=r.action_target,
                is_read=r.is_read,
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
            for r in recommendations[:5]
        ],
        top_error_patterns=[
            ErrorPatternResponse(
                id=p.id,
                category=p.category,
                description=p.description,
                occurrence_count=p.occurrence_count,
                ability_dim=p.ability_dim,
                last_seen_at=p.last_seen_at.isoformat() if p.last_seen_at else "",
            )
            for p in error_patterns[:5]
        ],
        ability_history=[
            AbilitySnapshotResponse(
                id=s.id,
                ability_scores=s.ability_scores,
                trigger_event=s.trigger_event,
                created_at=s.created_at.isoformat() if s.created_at else "",
            )
            for s in ability_history
        ],
        timeline=timeline[:50],
    )