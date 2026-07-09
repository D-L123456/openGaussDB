import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm.attributes import flag_modified

from app.models.learning import LearningEvent, UserProfile, ErrorPattern, AbilitySnapshot

logger = logging.getLogger(__name__)

ABILITY_DIMS = [
    "基础环境搭建",
    "openGauss运维",
    "数据库迁移与同步",
    "数据库开发",
    "数据库设计",
    "数据库优化与调优",
    "SQL编程与优化",
    "数据库对象管理",
]

DEFAULT_ABILITY_SCORES = {dim: 10 for dim in ABILITY_DIMS}

LEVEL_BOOST = {
    1: {"数据库设计": 25, "数据库对象管理": 10},
    2: {"基础环境搭建": 20, "openGauss运维": 10, "数据库开发": 15, "数据库设计": 10, "SQL编程与优化": 15, "数据库对象管理": 20},
    3: {"数据库开发": 20, "数据库设计": 5, "SQL编程与优化": 30, "数据库对象管理": 10},
    4: {"数据库开发": 15, "SQL编程与优化": 20, "数据库对象管理": 15, "数据库优化与调优": 10},
    5: {"数据库开发": 10, "SQL编程与优化": 15, "数据库优化与调优": 20, "数据库对象管理": 10},
    6: {"数据库优化与调优": 30, "openGauss运维": 15, "数据库迁移与同步": 10, "基础环境搭建": 10, "SQL编程与优化": 10},
    7: {"openGauss运维": 20, "基础环境搭建": 5, "数据库优化与调优": 10, "数据库对象管理": 20, "数据库迁移与同步": 5},
    8: {"openGauss运维": 25, "基础环境搭建": 10, "数据库优化与调优": 10, "数据库迁移与同步": 10, "数据库对象管理": 5},
    9: {"数据库开发": 15, "数据库设计": 10, "SQL编程与优化": 20, "数据库优化与调优": 10, "openGauss运维": 10, "数据库对象管理": 10, "数据库迁移与同步": 5, "基础环境搭建": 5},
}

EVENT_TYPE_DIM_MAP = {
    "challenge_start": None,
    "challenge_submit": None,
    "challenge_error": None,
    "challenge_pass": None,
    "sql_submit": "SQL编程与优化",
    "sql_error": "SQL编程与优化",
    "sql_pass": "SQL编程与优化",
    "chat_ask": None,
    "knowledge_browse": None,
}


class LearningTracker:
    async def record_event(
        self,
        db: AsyncSession,
        user_id: str,
        event_type: str,
        level: int | None = None,
        part: int | None = None,
        detail: dict | None = None,
        duration_seconds: int | None = None,
    ) -> LearningEvent:
        event = LearningEvent(
            user_id=user_id,
            event_type=event_type,
            level=level,
            part=part,
            detail=detail or {},
            duration_seconds=duration_seconds,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        await self._update_profile_on_event(db, user_id, event)
        await self._update_error_patterns(db, user_id, event)

        return event

    async def _update_profile_on_event(
        self, db: AsyncSession, user_id: str, event: LearningEvent
    ):
        profile = await self._get_or_create_profile(db, user_id)
        profile.last_active_at = datetime.utcnow()

        if event.duration_seconds:
            profile.total_learning_time = (profile.total_learning_time or 0) + event.duration_seconds

        if event.event_type == "challenge_pass":
            await self._apply_challenge_boost(db, profile, event)
            await self._update_challenge_progress(profile, event)

        if event.event_type == "challenge_part_pass":
            await self._apply_challenge_part_boost(db, profile, event)

        if event.event_type in ("challenge_error", "sql_error"):
            await self._update_weak_points(profile, event)

        await self._update_streak(profile)
        await self._update_badges(profile, event)

        await db.commit()

    async def _apply_challenge_boost(
        self, db: AsyncSession, profile: UserProfile, event: LearningEvent
    ):
        if not event.level:
            return

        progress = profile.challenge_progress or {}
        level_key = str(event.level)
        if progress.get(level_key, {}).get("status") == "passed":
            logger.info(f"Level {event.level} already passed, skip boost")
            return

        boost = LEVEL_BOOST.get(event.level, {})
        scores = profile.ability_scores or dict(DEFAULT_ABILITY_SCORES)

        detail = event.detail or {}
        attempts = detail.get("attempts", 1)
        time_taken = detail.get("duration_seconds", 0)

        for dim, base_boost in boost.items():
            if dim in scores:
                effective_boost = base_boost
                if attempts > 3:
                    effective_boost = int(base_boost * 0.6)
                elif attempts > 1:
                    effective_boost = int(base_boost * 0.8)
                if time_taken and time_taken > 600:
                    effective_boost = int(effective_boost * 0.8)
                scores[dim] = min(100, scores.get(dim, 10) + effective_boost)

        profile.ability_scores = scores
        flag_modified(profile, "ability_scores")

        snapshot = AbilitySnapshot(
            user_id=profile.user_id,
            ability_scores=scores.copy(),
            trigger_event=f"challenge_pass_level_{event.level}",
        )
        db.add(snapshot)

    async def _update_challenge_progress(self, profile: UserProfile, event: LearningEvent):
        progress = profile.challenge_progress or {}
        level_key = str(event.level)
        detail = event.detail or {}

        if level_key not in progress:
            progress[level_key] = {"status": "in_progress", "attempts": 0, "errors": [], "passed_at": None}

        progress[level_key]["status"] = "passed"
        progress[level_key]["attempts"] = detail.get("attempts", progress[level_key].get("attempts", 0))
        progress[level_key]["passed_at"] = datetime.utcnow().isoformat()

        if detail.get("errors"):
            progress[level_key]["errors"] = detail["errors"]

        profile.challenge_progress = progress
        flag_modified(profile, "challenge_progress")

    async def _apply_challenge_part_boost(
        self, db: AsyncSession, profile: UserProfile, event: LearningEvent
    ):
        if not event.level:
            return
        boost = LEVEL_BOOST.get(event.level, {})
        if not boost:
            return
        scores = profile.ability_scores or dict(DEFAULT_ABILITY_SCORES)
        detail = event.detail or {}
        total_parts = detail.get("total_parts", 1)
        fraction = 1.0 / total_parts

        for dim, base_boost in boost.items():
            if dim in scores:
                part_boost = max(1, int(base_boost * fraction))
                scores[dim] = min(100, scores.get(dim, 10) + part_boost)

        profile.ability_scores = scores
        flag_modified(profile, "ability_scores")

    async def _update_weak_points(self, profile: UserProfile, event: LearningEvent):
        weak = profile.weak_points or {}
        detail = event.detail or {}
        error_category = detail.get("category", "unknown")

        if error_category not in weak:
            weak[error_category] = {"count": 0, "first_seen": None, "last_seen": None, "examples": []}

        weak[error_category]["count"] += 1
        weak[error_category]["last_seen"] = datetime.utcnow().isoformat()
        if not weak[error_category]["first_seen"]:
            weak[error_category]["first_seen"] = datetime.utcnow().isoformat()

        example = detail.get("user_answer", "")
        if example and len(weak[error_category].get("examples", [])) < 5:
            weak[error_category].setdefault("examples", []).append(example)

        profile.weak_points = weak
        flag_modified(profile, "weak_points")

    async def _update_error_patterns(self, db: AsyncSession, user_id: str, event: LearningEvent):
        if event.event_type not in ("challenge_error", "sql_error"):
            return

        detail = event.detail or {}
        category = detail.get("category", event.event_type)
        description = detail.get("description", detail.get("user_answer", "未知错误"))

        result = await db.execute(
            select(ErrorPattern).where(
                ErrorPattern.user_id == user_id,
                ErrorPattern.category == category,
            )
        )
        pattern = result.scalar_one_or_none()

        if pattern:
            pattern.occurrence_count += 1
            pattern.last_seen_at = datetime.utcnow()
            related = pattern.related_events or []
            related.append(event.id)
            pattern.related_events = related[-20:]
        else:
            dim = detail.get("ability_dim", EVENT_TYPE_DIM_MAP.get(event.event_type))
            pattern = ErrorPattern(
                user_id=user_id,
                category=category,
                description=description,
                ability_dim=dim,
                related_events=[event.id],
            )
            db.add(pattern)

        await db.commit()

    async def _update_streak(self, profile: UserProfile):
        now = datetime.utcnow()
        last = profile.last_active_at

        if not last:
            profile.streak_days = 1
            return

        diff = now.date() - last.date()
        if diff.days == 0:
            pass
        elif diff.days == 1:
            profile.streak_days = (profile.streak_days or 0) + 1
        else:
            profile.streak_days = 1

    async def _update_badges(self, profile: UserProfile, event: LearningEvent):
        badges = profile.badges or {}

        if event.event_type == "challenge_pass":
            badges["first_clear"] = True
            progress = profile.challenge_progress or {}
            if len(progress) >= 2:
                badges["double_clear"] = True

        if (profile.streak_days or 0) >= 3:
            badges["streak_3"] = True
        if (profile.streak_days or 0) >= 7:
            badges["streak_7"] = True

        detail = event.detail or {}
        if event.event_type == "challenge_pass" and detail.get("attempts", 1) == 1:
            badges["perfect_clear"] = True

        if (profile.total_learning_time or 0) >= 3600:
            badges["hour_scholar"] = True

        profile.badges = badges
        flag_modified(profile, "badges")

    async def _get_or_create_profile(self, db: AsyncSession, user_id: str) -> UserProfile:
        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                ability_scores=dict(DEFAULT_ABILITY_SCORES),
                weak_points={},
                error_patterns={},
                learning_style="undetermined",
                total_learning_time=0,
                streak_days=0,
                challenge_progress={},
                badges={},
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
        return profile

    async def get_profile(self, db: AsyncSession, user_id: str) -> UserProfile:
        return await self._get_or_create_profile(db, user_id)

    async def get_events(
        self,
        db: AsyncSession,
        user_id: str,
        event_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[LearningEvent], int]:
        query = select(LearningEvent).where(LearningEvent.user_id == user_id)
        count_query = select(func.count(LearningEvent.id)).where(LearningEvent.user_id == user_id)

        if event_type:
            query = query.where(LearningEvent.event_type == event_type)
            count_query = count_query.where(LearningEvent.event_type == event_type)

        total = await db.scalar(count_query)

        query = query.order_by(LearningEvent.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(query)
        events = result.scalars().all()

        return events, total or 0

    async def get_error_patterns(self, db: AsyncSession, user_id: str) -> list[ErrorPattern]:
        result = await db.execute(
            select(ErrorPattern)
            .where(ErrorPattern.user_id == user_id)
            .order_by(ErrorPattern.occurrence_count.desc())
        )
        return result.scalars().all()

    async def get_ability_history(self, db: AsyncSession, user_id: str, limit: int = 30) -> list[AbilitySnapshot]:
        result = await db.execute(
            select(AbilitySnapshot)
            .where(AbilitySnapshot.user_id == user_id)
            .order_by(AbilitySnapshot.created_at.desc())
            .limit(limit)
        )
        snapshots = result.scalars().all()
        return list(reversed(snapshots))

    async def get_timeline(
        self, db: AsyncSession, user_id: str, days: int = 30
    ) -> list[dict]:
        since = datetime.utcnow() - timedelta(days=days)
        result = await db.execute(
            select(LearningEvent)
            .where(LearningEvent.user_id == user_id, LearningEvent.created_at >= since)
            .order_by(LearningEvent.created_at.desc())
        )
        events = result.scalars().all()

        timeline = []
        for e in events:
            timeline.append({
                "id": e.id,
                "event_type": e.event_type,
                "level": e.level,
                "part": e.part,
                "detail": e.detail,
                "duration_seconds": e.duration_seconds,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            })
        return timeline

    async def determine_learning_style(self, db: AsyncSession, user_id: str) -> str:
        result = await db.execute(
            select(LearningEvent.event_type, func.count(LearningEvent.id).label("cnt"))
            .where(LearningEvent.user_id == user_id)
            .group_by(LearningEvent.event_type)
        )
        counts = {row.event_type: row.cnt for row in result.all()}

        challenge_count = counts.get("challenge_start", 0) + counts.get("challenge_pass", 0)
        chat_count = counts.get("chat_ask", 0)
        sql_count = counts.get("sql_submit", 0) + counts.get("sql_pass", 0)
        knowledge_count = counts.get("knowledge_browse", 0)

        if challenge_count > chat_count and challenge_count > sql_count:
            return "explorer"
        elif chat_count > challenge_count and chat_count > sql_count:
            return "theorist"
        elif sql_count > challenge_count and sql_count > chat_count:
            return "practitioner"
        elif knowledge_count > 0:
            return "theorist"
        else:
            return "undetermined"


learning_tracker = LearningTracker()