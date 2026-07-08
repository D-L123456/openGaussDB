from pydantic import BaseModel
from typing import Any


class LearningEventCreate(BaseModel):
    event_type: str
    level: int | None = None
    part: int | None = None
    detail: dict[str, Any] | None = None
    duration_seconds: int | None = None


class LearningEventResponse(BaseModel):
    id: str
    event_type: str
    level: int | None
    part: int | None
    detail: dict[str, Any] | None
    duration_seconds: int | None
    created_at: str

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    user_id: str
    ability_scores: dict[str, Any]
    weak_points: dict[str, Any] | None
    error_patterns: dict[str, Any] | None
    learning_style: str
    total_learning_time: int
    streak_days: int
    last_active_at: str | None
    challenge_progress: dict[str, Any] | None
    badges: dict[str, Any] | None

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    id: str
    rec_type: str
    title: str
    description: str
    priority: int
    action_type: str | None
    action_target: str | None
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True


class AbilitySnapshotResponse(BaseModel):
    id: str
    ability_scores: dict[str, Any]
    trigger_event: str
    created_at: str

    class Config:
        from_attributes = True


class ErrorPatternResponse(BaseModel):
    id: str
    category: str
    description: str
    occurrence_count: int
    ability_dim: str | None
    last_seen_at: str

    class Config:
        from_attributes = True


class LearningTimelineResponse(BaseModel):
    events: list[dict[str, Any]]
    total_count: int


class LearningDashboardResponse(BaseModel):
    profile: UserProfileResponse
    recent_recommendations: list[RecommendationResponse]
    top_error_patterns: list[ErrorPatternResponse]
    ability_history: list[AbilitySnapshotResponse]
    timeline: list[dict[str, Any]]