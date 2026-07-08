import json
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.learning import UserProfile, LearningRecommendation, ErrorPattern, LearningEvent
from app.services.llm_service import llm_service
from app.services.learning_tracker import learning_tracker, ABILITY_DIMS

logger = logging.getLogger(__name__)

PROFILE_ANALYSIS_PROMPT = """你是一个专业的学习分析助手。你将收到学员的完整学习画像数据，请分析并给出个性化提升建议。

分析维度：
1. 能力短板：8维能力中哪些明显偏低
2. 错误模式：用户反复犯的同类错误
3. 学习进度：闯关进度和练习完成情况
4. 学习风格：根据行为数据推断的学习偏好

请给出3-5条具体的、可操作的提升建议。每条建议包含：
- type: "knowledge"（学知识）/ "practice"（做练习）/ "challenge"（闯关）/ "review"（复习）
- title: 简短标题
- description: 详细说明（2-3句话）
- priority: 1-5（1最紧急）
- action_type: "goto_knowledge" / "goto_challenge" / "goto_sql" / "review_error"
- action_target: 具体目标（如关卡号、章节名、题目ID等）

你必须严格按以下JSON格式回复，不要输出任何其他内容：
[
  {"type": "...", "title": "...", "description": "...", "priority": 1, "action_type": "...", "action_target": "..."}
]"""


class ProfileEngine:
    async def analyze_and_recommend(
        self, db: AsyncSession, user_id: str = "default_user"
    ) -> list[LearningRecommendation]:
        profile = await learning_tracker.get_profile(db, user_id)

        await self._update_learning_style(db, profile)

        analysis_data = self._build_analysis_data(profile)

        try:
            result = await llm_service.chat(
                [
                    {"role": "system", "content": PROFILE_ANALYSIS_PROMPT},
                    {"role": "user", "content": analysis_data},
                ],
                temperature=0.4,
                max_tokens=1500,
            )
            result = result.strip()
            if result.startswith("```"):
                lines = result.split("\n")
                lines = [l for l in lines if l.strip() and not l.strip().startswith("```")]
                result = "\n".join(lines)

            recs_data = json.loads(result)
            if not isinstance(recs_data, list):
                return await self._fallback_recommendations(db, profile)

            await self._dismiss_old_recommendations(db, user_id)

            recommendations = []
            for r in recs_data[:5]:
                rec = LearningRecommendation(
                    user_id=user_id,
                    rec_type=r.get("type", "knowledge"),
                    title=r.get("title", ""),
                    description=r.get("description", ""),
                    priority=r.get("priority", 5),
                    action_type=r.get("action_type"),
                    action_target=r.get("action_target"),
                )
                db.add(rec)
                recommendations.append(rec)

            await db.commit()
            for rec in recommendations:
                await db.refresh(rec)

            return recommendations
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Profile analysis parse failed: {e}")
            return await self._fallback_recommendations(db, profile)
        except Exception as e:
            logger.warning(f"Profile analysis error: {type(e).__name__}: {e}")
            return await self._fallback_recommendations(db, profile)

    def _build_analysis_data(self, profile: UserProfile) -> str:
        scores = profile.ability_scores or {}
        weak = profile.weak_points or {}
        progress = profile.challenge_progress or {}
        badges = profile.badges or {}

        scores_text = "\n".join(
            f"  - {dim}: {scores.get(dim, 10)}" for dim in ABILITY_DIMS
        )

        weak_text = ""
        for cat, info in sorted(weak.items(), key=lambda x: x[1].get("count", 0), reverse=True)[:5]:
            weak_text += f"  - {cat}: 出现{info.get('count', 0)}次 (最近: {info.get('last_seen', '未知')})\n"

        progress_text = ""
        for lvl, info in progress.items():
            status = info.get("status", "unknown")
            attempts = info.get("attempts", 0)
            errors = info.get("errors", [])
            progress_text += f"  - 第{lvl}关: {status}, 尝试{attempts}次"
            if errors:
                progress_text += f", 错误: {errors}"
            progress_text += "\n"

        badges_text = ", ".join(badges.keys()) if badges else "无"

        return f"""学员学习画像：

【8维能力评分】
{scores_text}

【薄弱环节】
{weak_text if weak_text else "  暂无明显薄弱环节"}

【闯关进度】
{progress_text if progress_text else "  尚未开始闯关"}

【学习风格】{profile.learning_style}

【累计学习时长】{profile.total_learning_time or 0}秒

【连续学习天数】{profile.streak_days or 0}天

【获得徽章】{badges_text}

请基于以上画像，给出3-5条个性化提升建议。"""

    async def _update_learning_style(self, db: AsyncSession, profile: UserProfile):
        style = await learning_tracker.determine_learning_style(db, profile.user_id)
        profile.learning_style = style
        await db.commit()

    async def _dismiss_old_recommendations(self, db: AsyncSession, user_id: str):
        result = await db.execute(
            select(LearningRecommendation)
            .where(LearningRecommendation.user_id == user_id, LearningRecommendation.is_dismissed == False)
        )
        old = result.scalars().all()
        for rec in old:
            rec.is_dismissed = True
        await db.commit()

    async def _fallback_recommendations(
        self, db: AsyncSession, profile: UserProfile
    ) -> list[LearningRecommendation]:
        scores = profile.ability_scores or {}
        weak_dims = sorted(
            [(dim, scores.get(dim, 10)) for dim in ABILITY_DIMS],
            key=lambda x: x[1],
        )[:3]

        await self._dismiss_old_recommendations(db, profile.user_id)

        recs = []
        for dim, score in weak_dims:
            rec = LearningRecommendation(
                user_id=profile.user_id,
                rec_type="knowledge",
                title=f"加强{dim}",
                description=f"你的{dim}能力评分为{score}分，建议通过学习和练习提升这一薄弱环节。",
                priority=1 if score < 20 else 3,
                action_type="goto_knowledge",
                action_target=dim,
            )
            db.add(rec)
            recs.append(rec)

        progress = profile.challenge_progress or {}
        if "1" not in progress:
            rec = LearningRecommendation(
                user_id=profile.user_id,
                rec_type="challenge",
                title="开始第一关：ER图复位",
                description="通过拖拽ER图组件，理解实体-联系模型的基本概念。",
                priority=1,
                action_type="goto_challenge",
                action_target="1",
            )
            db.add(rec)
            recs.append(rec)

        await db.commit()
        for rec in recs:
            await db.refresh(rec)

        return recs

    async def get_active_recommendations(
        self, db: AsyncSession, user_id: str = "default_user"
    ) -> list[LearningRecommendation]:
        result = await db.execute(
            select(LearningRecommendation)
            .where(
                LearningRecommendation.user_id == user_id,
                LearningRecommendation.is_dismissed == False,
            )
            .order_by(LearningRecommendation.priority, LearningRecommendation.created_at.desc())
        )
        return result.scalars().all()

    async def mark_recommendation_read(
        self, db: AsyncSession, rec_id: str
    ) -> LearningRecommendation | None:
        result = await db.execute(
            select(LearningRecommendation).where(LearningRecommendation.id == rec_id)
        )
        rec = result.scalar_one_or_none()
        if rec:
            rec.is_read = True
            await db.commit()
            await db.refresh(rec)
        return rec

    async def dismiss_recommendation(
        self, db: AsyncSession, rec_id: str
    ) -> LearningRecommendation | None:
        result = await db.execute(
            select(LearningRecommendation).where(LearningRecommendation.id == rec_id)
        )
        rec = result.scalar_one_or_none()
        if rec:
            rec.is_dismissed = True
            await db.commit()
            await db.refresh(rec)
        return rec


profile_engine = ProfileEngine()