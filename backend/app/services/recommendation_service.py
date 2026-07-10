import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer

from app.models.sql_practice import SqlQuestion, SqlSubmission
from app.models.knowledge import KnowledgeNode
from app.models.learning import UserProfile
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

RECOMMEND_PROMPT = """你是一个智能学习推荐助手。根据用户的SQL练习表现和学习画像数据，推荐最需要复习或学习的知识内容。

分析要点：
1. 优先关注用户能力画像中得分最低的维度，推荐对应章节
2. 找出得分低的题目对应的章节和知识点
3. 找出多次提交仍未正确的题目
4. 根据错误模式推断用户薄弱的知识领域
5. 推荐具体的知识体系节点，帮助用户针对性提升
6. 不要推荐用户已经掌握（能力分数>=70）的维度对应的基础内容

能力维度与章节对应关系：
- 基础环境搭建 → 第2章
- openGauss运维 → 第2章
- 数据库迁移与同步 → 第2章
- 数据库开发 → 第4章
- 数据库设计 → 第3章
- 数据库优化与调优 → 第6章
- SQL编程与优化 → 第3章、第5章
- 数据库对象管理 → 第3章

你必须严格按以下JSON格式回复，不要输出任何其他内容：
[
  {"chapter": "章节名", "section": "小节名", "title": "知识点标题", "reason": "推荐原因（简短说明为什么推荐这个知识点）"}
]

最多推荐5个知识点，按优先级排序。如果用户没有练习记录，返回空数组 []。"""

SQL_PRACTICE_RECOMMEND_PROMPT = """你是一个openGauss数据库智能学习推荐助手。用户刚刚完成了一道SQL练习题，请根据其表现给出个性化推荐。

推荐类型包括：
1. knowledge：推荐复习某个知识点（关联知识体系节点）
2. practice：推荐继续做某道练习题（关联题目ID）

分析要点：
- 如果答错或得分低：推荐复习相关知识点，再推荐同类简单题目练习
- 如果答对但得分不高：推荐优化相关知识点，推荐同类中等难度题目
- 如果满分通过：推荐进阶知识点，推荐更高难度题目
- 推荐要具体、有针对性，不要泛泛而谈

你必须严格按以下JSON格式回复，不要输出任何其他内容：
[
  {{"type": "knowledge", "chapter": "章节名", "section": "小节名", "title": "知识点标题", "reason": "推荐原因", "node_id": null}},
  {{"type": "practice", "question_id": "题目ID", "title": "题目标题", "reason": "推荐原因"}}
]

最多推荐4条（2个知识点+2道题目），按优先级排序。"""


class RecommendationService:
    def __init__(self):
        self.llm_service = llm_service

    async def get_recommendations(self, db: AsyncSession) -> list[dict]:
        stats = await self._get_practice_stats(db)
        profile_data = await self._get_user_profile_data(db)

        if not stats["total_submissions"] and not profile_data["has_profile"]:
            return await self._get_default_recommendations(db)

        knowledge_map = await self._get_knowledge_map(db)

        prompt_data = self._build_prompt_data(stats, knowledge_map, profile_data)

        try:
            result = await self.llm_service.chat(
                [
                    {"role": "system", "content": RECOMMEND_PROMPT},
                    {"role": "user", "content": prompt_data},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            result = result.strip()
            if result.startswith("```"):
                lines = result.split("\n")
                lines = [l for l in lines if l.strip() and not l.strip().startswith("```")]
                result = "\n".join(lines)

            recommendations = json.loads(result)
            if not isinstance(recommendations, list):
                return []

            for rec in recommendations:
                node_id = await self._find_knowledge_node(
                    db, rec.get("chapter", ""), rec.get("section", ""), rec.get("title", "")
                )
                rec["node_id"] = node_id

            return recommendations[:5]
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Recommendation parse failed: {e}")
            return self._fallback_recommendations(stats, knowledge_map, profile_data)
        except Exception as e:
            logger.warning(f"Recommendation error: {type(e).__name__}: {e}")
            return self._fallback_recommendations(stats, knowledge_map, profile_data)

    async def _get_practice_stats(self, db: AsyncSession) -> dict:
        total_submissions = await db.scalar(
            select(func.count(SqlSubmission.id))
        )

        avg_score = await db.scalar(
            select(func.avg(SqlSubmission.score))
        )

        correct_count = await db.scalar(
            select(func.count(SqlSubmission.id)).where(SqlSubmission.is_correct == True)
        )

        result = await db.execute(
            select(
                SqlQuestion.chapter,
                SqlQuestion.title,
                SqlQuestion.difficulty,
                SqlQuestion.tags,
                func.count(SqlSubmission.id).label("attempt_count"),
                func.avg(SqlSubmission.score).label("avg_score"),
                func.max(SqlSubmission.is_correct.cast(Integer)).label("ever_correct"),
                func.min(SqlSubmission.created_at).label("first_attempt"),
                func.max(SqlSubmission.created_at).label("last_attempt"),
            )
            .join(SqlSubmission, SqlQuestion.id == SqlSubmission.question_id)
            .group_by(SqlQuestion.id)
        )
        question_stats = []
        for row in result.all():
            question_stats.append({
                "chapter": row.chapter,
                "title": row.title,
                "difficulty": row.difficulty,
                "tags": row.tags,
                "attempt_count": row.attempt_count,
                "avg_score": round(row.avg_score, 1) if row.avg_score else 0,
                "ever_correct": bool(row.ever_correct),
                "first_attempt": str(row.first_attempt) if row.first_attempt else None,
                "last_attempt": str(row.last_attempt) if row.last_attempt else None,
            })

        return {
            "total_submissions": total_submissions or 0,
            "avg_score": round(avg_score, 1) if avg_score else 0,
            "correct_rate": round(correct_count / total_submissions * 100, 1) if total_submissions else 0,
            "question_stats": question_stats,
        }

    async def _get_knowledge_map(self, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            select(KnowledgeNode).where(KnowledgeNode.content.isnot(None)).where(KnowledgeNode.content != "")
        )
        nodes = result.scalars().all()
        return [
            {
                "id": str(node.id),
                "chapter": node.chapter,
                "section": node.section,
                "title": node.title,
            }
            for node in nodes
            if node.content
        ]

    async def _get_user_profile_data(self, db: AsyncSession) -> dict:
        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == "default_user")
        )
        profile = result.scalar_one_or_none()
        if not profile:
            return {"has_profile": False}

        ability_scores = profile.ability_scores or {}
        weak_points = profile.weak_points or {}
        challenge_progress = profile.challenge_progress or {}

        sorted_dims = sorted(ability_scores.items(), key=lambda x: x[1])

        return {
            "has_profile": True,
            "ability_scores": ability_scores,
            "weakest_dims": [dim for dim, score in sorted_dims[:3] if score < 60],
            "strong_dims": [dim for dim, score in sorted_dims if score >= 70],
            "weak_points": weak_points,
            "challenge_progress": challenge_progress,
            "streak_days": profile.streak_days,
            "total_learning_time": profile.total_learning_time,
        }

    def _build_prompt_data(self, stats: dict, knowledge_map: list[dict], profile_data: dict) -> str:
        knowledge_summary = {}
        for k in knowledge_map:
            ch = k["chapter"]
            if ch not in knowledge_summary:
                knowledge_summary[ch] = []
            knowledge_summary[ch].append(f"{k['section']} > {k['title']}")

        knowledge_text = ""
        for ch, sections in knowledge_summary.items():
            knowledge_text += f"\n{ch}：\n"
            for s in sections:
                knowledge_text += f"  - {s}\n"

        profile_text = ""
        if profile_data.get("has_profile"):
            ability_scores = profile_data.get("ability_scores", {})
            profile_text = f"""
用户学习画像：
- 能力分数：{json.dumps(ability_scores, ensure_ascii=False)}
- 最弱维度：{', '.join(profile_data.get('weakest_dims', [])) or '无'}
- 已掌握维度：{', '.join(profile_data.get('strong_dims', [])) or '无'}
- 连续学习天数：{profile_data.get('streak_days', 0)}
- 总学习时长：{profile_data.get('total_learning_time', 0)}秒
- 闯关进度：{json.dumps(profile_data.get('challenge_progress', {}), ensure_ascii=False)}
- 薄弱点记录：{json.dumps(profile_data.get('weak_points', {}), ensure_ascii=False)}
"""

        stats_text = f"""用户练习统计：
- 总提交次数：{stats['total_submissions']}
- 平均得分：{stats['avg_score']}
- 正确率：{stats['correct_rate']}%

各题目表现：
"""
        for q in stats["question_stats"]:
            status = "✓" if q["ever_correct"] else "✗"
            stats_text += f"- [{status}] {q['chapter']} | {q['title']} | 难度:{q['difficulty']} | 提交{q['attempt_count']}次 | 平均分:{q['avg_score']}\n"

        return f"{stats_text}{profile_text}\n\n可推荐的知识体系：{knowledge_text}"

    async def _find_knowledge_node(
        self, db: AsyncSession, chapter: str, section: str, title: str
    ) -> str | None:
        query = select(KnowledgeNode)
        if title:
            query = query.where(KnowledgeNode.title.contains(title))
        elif section:
            query = query.where(KnowledgeNode.section.contains(section))
        elif chapter:
            query = query.where(KnowledgeNode.chapter.contains(chapter))

        result = await db.execute(query.limit(1))
        node = result.scalar_one_or_none()
        return str(node.id) if node else None

    async def _get_default_recommendations(self, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            select(KnowledgeNode)
            .where(KnowledgeNode.content.isnot(None))
            .where(KnowledgeNode.content != "")
            .order_by(KnowledgeNode.sort_order)
            .limit(5)
        )
        nodes = result.scalars().all()
        return [
            {
                "chapter": node.chapter,
                "section": node.section,
                "title": node.title,
                "reason": "建议从基础知识开始学习",
                "node_id": str(node.id),
            }
            for node in nodes
        ]

    async def get_sql_practice_recommendations(
        self,
        db: AsyncSession,
        question_id: str,
        is_correct: bool,
        score: float,
    ) -> list[dict]:
        question_result = await db.execute(
            select(SqlQuestion).where(SqlQuestion.id == question_id)
        )
        question = question_result.scalar_one_or_none()
        if not question:
            return []

        history = await self._get_question_history(db, question_id)

        knowledge_map = await self._get_knowledge_map(db)

        related_questions = await self._get_related_questions(db, question)

        prompt_data = self._build_sql_practice_prompt(
            question, is_correct, score, history, knowledge_map, related_questions
        )

        try:
            result = await self.llm_service.chat(
                [
                    {"role": "system", "content": SQL_PRACTICE_RECOMMEND_PROMPT},
                    {"role": "user", "content": prompt_data},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            result = result.strip()
            if result.startswith("```"):
                lines = result.split("\n")
                lines = [l for l in lines if l.strip() and not l.strip().startswith("```")]
                result = "\n".join(lines)

            recommendations = json.loads(result)
            if not isinstance(recommendations, list):
                return self._fallback_sql_recommendations(question, is_correct, score, knowledge_map, related_questions)

            for rec in recommendations:
                if rec.get("type") == "knowledge":
                    node_id = await self._find_knowledge_node(
                        db, rec.get("chapter", ""), rec.get("section", ""), rec.get("title", "")
                    )
                    rec["node_id"] = node_id

            return recommendations[:4]
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"SQL practice recommendation parse failed: {e}")
            return self._fallback_sql_recommendations(question, is_correct, score, knowledge_map, related_questions)
        except Exception as e:
            logger.warning(f"SQL practice recommendation error: {type(e).__name__}: {e}")
            return self._fallback_sql_recommendations(question, is_correct, score, knowledge_map, related_questions)

    async def _get_question_history(self, db: AsyncSession, question_id: str) -> list[dict]:
        result = await db.execute(
            select(SqlSubmission)
            .where(SqlSubmission.question_id == question_id)
            .order_by(SqlSubmission.created_at.desc())
            .limit(5)
        )
        submissions = result.scalars().all()
        return [
            {
                "is_correct": s.is_correct,
                "score": s.score,
                "created_at": s.created_at.isoformat(),
            }
            for s in submissions
        ]

    async def _get_related_questions(self, db: AsyncSession, current_question: SqlQuestion) -> list[dict]:
        query = select(SqlQuestion).where(SqlQuestion.id != current_question.id)
        if current_question.chapter:
            query = query.where(SqlQuestion.chapter == current_question.chapter)
        query = query.order_by(SqlQuestion.difficulty, SqlQuestion.created_at).limit(10)
        result = await db.execute(query)
        questions = result.scalars().all()
        return [
            {
                "id": str(q.id),
                "title": q.title,
                "chapter": q.chapter,
                "difficulty": q.difficulty,
            }
            for q in questions
        ]

    def _build_sql_practice_prompt(
        self,
        question: SqlQuestion,
        is_correct: bool,
        score: float,
        history: list[dict],
        knowledge_map: list[dict],
        related_questions: list[dict],
    ) -> str:
        knowledge_summary = {}
        for k in knowledge_map:
            ch = k["chapter"]
            if ch not in knowledge_summary:
                knowledge_summary[ch] = []
            knowledge_summary[ch].append(f"{k['section']} > {k['title']}")

        knowledge_text = ""
        for ch, sections in knowledge_summary.items():
            knowledge_text += f"\n{ch}：\n"
            for s in sections:
                knowledge_text += f"  - {s}\n"

        related_text = ""
        for q in related_questions:
            related_text += f"  - ID:{q['id']} | {q['title']} | {q['chapter']} | 难度:{q['difficulty']}\n"

        history_text = ""
        for h in history:
            status = "✓" if h["is_correct"] else "✗"
            history_text += f"  - [{status}] 得分:{h['score']} ({h['created_at'][:10]})\n"

        return f"""当前题目信息：
- 标题：{question.title}
- 章节：{question.chapter}
- 难度：{question.difficulty}
- 描述：{question.description[:200]}

本次提交结果：
- 是否正确：{'是' if is_correct else '否'}
- 得分：{score}/100

该题历史提交（最近5次）：
{history_text if history_text else '  无历史记录'}

可推荐的知识体系：
{knowledge_text}

同章节可推荐的练习题：
{related_text if related_text else '  无同章节题目'}"""

    def _fallback_sql_recommendations(
        self,
        question: SqlQuestion,
        is_correct: bool,
        score: float,
        knowledge_map: list[dict],
        related_questions: list[dict],
    ) -> list[dict]:
        recommendations = []

        same_chapter_knowledge = [k for k in knowledge_map if k["chapter"] == question.chapter]
        for k in same_chapter_knowledge[:2]:
            if not is_correct or score < 80:
                reason = f"本题得分{score}分，建议复习该知识点巩固基础"
            else:
                reason = "可以进一步深入学习相关知识"
            recommendations.append({
                "type": "knowledge",
                "chapter": k["chapter"],
                "section": k["section"],
                "title": k["title"],
                "reason": reason,
                "node_id": k.get("id"),
            })

        for q in related_questions[:2]:
            if not is_correct and q["difficulty"] == "easy":
                reason = "建议先从简单题目练手，巩固基础"
            elif is_correct and score >= 90 and q["difficulty"] in ("medium", "hard"):
                reason = "表现优秀，挑战更高难度题目"
            else:
                reason = "继续练习同类题目加深理解"
            recommendations.append({
                "type": "practice",
                "question_id": q["id"],
                "title": q["title"],
                "reason": reason,
            })

        return recommendations[:4]

    def _fallback_recommendations(self, stats: dict, knowledge_map: list[dict], profile_data: dict | None = None) -> list[dict]:
        weak_chapters = set()
        for q in stats.get("question_stats", []):
            if not q["ever_correct"] or q["avg_score"] < 60:
                weak_chapters.add(q["chapter"])

        DIM_CHAPTER_MAP = {
            "基础环境搭建": "第2章",
            "openGauss运维": "第2章",
            "数据库迁移与同步": "第2章",
            "数据库开发": "第4章",
            "数据库设计": "第3章",
            "数据库优化与调优": "第6章",
            "SQL编程与优化": "第3章",
            "数据库对象管理": "第3章",
        }

        if profile_data and profile_data.get("has_profile"):
            for dim in profile_data.get("weakest_dims", []):
                ch_prefix = DIM_CHAPTER_MAP.get(dim)
                if ch_prefix:
                    weak_chapters.add(ch_prefix)

        recommendations = []
        for k in knowledge_map:
            if any(ch in k["chapter"] for ch in weak_chapters):
                recommendations.append({
                    **k,
                    "reason": "该章节练习表现较弱，建议重点复习",
                })
                if len(recommendations) >= 5:
                    break

        if not recommendations:
            for k in knowledge_map[:3]:
                recommendations.append({**k, "reason": "建议系统学习基础知识"})

        return recommendations[:5]


recommendation_service = RecommendationService()