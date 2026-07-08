import json
import logging
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.chat import ChatSession, ChatMessage
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.services.learning_tracker import learning_tracker, ABILITY_DIMS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是OpenGauss数据库知识智能体，专门回答关于openGauss数据库的问题。

你的知识来源于openGauss官方教程文档，涵盖以下内容：
- 第1章：数据库安装配置与SQL基础
- 第2章：查询优化与业务封装（视图、索引、游标、事务、存储过程、触发器）
- 第3章：数据库设计（需求分析、E-R图、规范化）
- 第4章：数据库开发（JDBC、Psycopg、ODBC、设计规范）
- 第5章：数据库迁移（全量迁移、增量迁移、反向迁移、数据校验）
- 第6章：性能调优（执行计划、WDR报告、参数调优、SQL改写）
- 第7章：高级特性（全密态数据库、MOT、AI4DB、DB4AI）
- 第8章：成为openGauss开发者

回答要求：
1. 基于检索到的知识内容进行回答，确保准确性
2. 如果涉及SQL语句，请给出openGauss兼容的语法
3. 如果知识库中没有相关内容，请如实说明
4. 回答要结构化，使用markdown格式
5. 对于操作类问题，给出具体步骤和命令"""

PROFILE_SYSTEM_PROMPT_TEMPLATE = """【学员画像 — 请据此个性化回答】

8维能力评分：
{ability_scores_text}

薄弱环节：
{weak_points_text}

常见错误模式：
{error_patterns_text}

闯关进度：
{challenge_progress_text}

学习风格：{learning_style}

个性化回答要求：
1. 如果用户问的问题涉及其薄弱环节，主动补充相关知识点和注意事项
2. 如果用户曾经犯过类似错误，温和提醒"你之前在XXX上出过错，注意..."
3. 根据学习风格调整回答方式：
   - explorer（探索型）：先给结论，再给详细解释，鼓励动手尝试
   - theorist（理论型）：先讲原理，再给示例，提供深入理解
   - practitioner（实践型）：先给代码/步骤，再简要解释原理
4. 适时推荐下一步学习内容（如"建议你试试第二关"或"可以复习一下XX章节"）
5. 不要在每次回答中都提及画像信息，只在相关时自然融入"""

INTENT_CHECK_PROMPT = """你是一个意图分析助手。你的任务是判断用户的问题是否足够清晰、是否包含了足够的信息来给出准确的回答。

判断标准：
- 如果用户的问题意图明确、条件充分，可以给出准确回答，则判断为"clear"
- 如果用户的问题模糊、缺少关键信息（如具体场景、版本、操作环境、使用目的等），需要追问才能准确回答，则判断为"unclear"

注意：
- 对于简单的常识性问题（如"openGauss是什么"），应判断为clear
- 只有当缺少信息会导致回答方向错误或不准确时，才判断为unclear
- 追问要具体、有针对性，帮助用户补充关键信息
- 最多追问1-2个关键问题，不要连续追问
- 如果用户是在回答之前的追问，补充了信息，应判断为clear

你必须严格按以下JSON格式回复，不要输出任何其他内容：
{"status": "clear"}
或
{"status": "unclear", "clarification": "你的追问内容"}"""


class RAGService:
    def __init__(self):
        self.vector_store = vector_store
        self.llm_service = llm_service

    async def chat(
        self,
        message: str,
        session_id: str | None = None,
        db: AsyncSession | None = None,
        user_id: str = "default_user",
    ) -> dict:
        history = []
        if db and session_id:
            history = await self._get_history(session_id, db)

        needs_clarification, clarification = await self._check_intent(
            message, history
        )

        if needs_clarification:
            if db:
                session_id, _ = await self._save_conversation(
                    session_id, message, clarification, [], db
                )
                await self._record_chat_event(db, user_id, message)
            return {
                "session_id": str(session_id or uuid4()),
                "answer": clarification,
                "sources": [],
                "needs_clarification": True,
            }

        search_results = self.vector_store.search(message, top_k=5)

        context_parts = []
        sources = []
        for result in search_results:
            meta = result["metadata"]
            context_parts.append(
                f"【{meta.get('chapter', '')} - {meta.get('section', '')}】\n{result['content']}"
            )
            source = f"{meta.get('chapter', '')} > {meta.get('section', '')} > {meta.get('title', '')}"
            if source not in sources:
                sources.append(source)

        context = "\n\n---\n\n".join(context_parts) if context_parts else "未检索到相关知识"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        if db:
            profile_prompt = await self._build_profile_prompt(db, user_id)
            if profile_prompt:
                messages.append({"role": "system", "content": profile_prompt})

        messages.append({"role": "system", "content": f"参考知识：\n{context}"})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        answer = await self.llm_service.chat(messages)

        if db:
            session_id, _ = await self._save_conversation(
                session_id, message, answer, sources, db
            )
            await self._record_chat_event(db, user_id, message)

        return {
            "session_id": str(session_id or uuid4()),
            "answer": answer,
            "sources": sources,
            "needs_clarification": False,
        }

    async def _check_intent(
        self, message: str, history: list[dict]
    ) -> tuple[bool, str]:
        messages = [
            {"role": "system", "content": INTENT_CHECK_PROMPT},
        ]
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        try:
            result = await self.llm_service.chat(
                messages, temperature=0.3, max_tokens=256
            )
            result = result.strip()
            if result.startswith("```"):
                lines = result.split("\n")
                lines = [l for l in lines if l.strip() and not l.strip().startswith("```")]
                result = "\n".join(lines)

            data = json.loads(result)
            status = data.get("status", "clear")

            if status == "unclear":
                clarification = data.get("clarification", "")
                if clarification:
                    return True, clarification

            return False, ""
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Intent check parse failed: {e}")
            return False, ""
        except Exception as e:
            logger.warning(f"Intent check error: {type(e).__name__}: {e}")
            return False, ""

    async def chat_stream(self, message: str, session_id: str | None = None):
        search_results = self.vector_store.search(message, top_k=5)

        context_parts = []
        sources = []
        for result in search_results:
            meta = result["metadata"]
            context_parts.append(
                f"【{meta.get('chapter', '')} - {meta.get('section', '')}】\n{result['content']}"
            )
            source = f"{meta.get('chapter', '')} > {meta.get('section', '')} > {meta.get('title', '')}"
            if source not in sources:
                sources.append(source)

        context = "\n\n---\n\n".join(context_parts) if context_parts else "未检索到相关知识"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"参考知识：\n{context}"},
            {"role": "user", "content": message},
        ]

        full_answer = ""
        async for chunk in self.llm_service.chat_stream(messages):
            full_answer += chunk
            yield {"type": "content", "data": chunk}

        yield {"type": "sources", "data": json.dumps(sources, ensure_ascii=False)}

    async def _get_history(self, session_id: str, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .limit(10)
        )
        messages = result.scalars().all()
        history = []
        for msg in messages:
            history.append({"role": msg.role, "content": msg.content})
        return history

    async def _save_conversation(
        self,
        session_id: str | None,
        message: str,
        answer: str,
        sources: list[str],
        db: AsyncSession,
    ) -> tuple[str, str]:
        if not session_id:
            session = ChatSession(title=message[:50])
            db.add(session)
            await db.commit()
            await db.refresh(session)
            session_id = session.id

        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=message,
        )
        assistant_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=answer,
            sources=json.dumps(sources, ensure_ascii=False),
        )
        db.add(user_msg)
        db.add(assistant_msg)
        await db.commit()

        return session_id, assistant_msg.id


    async def _build_profile_prompt(self, db: AsyncSession, user_id: str) -> str | None:
        try:
            profile = await learning_tracker.get_profile(db, user_id)
            if not profile:
                return None

            scores = profile.ability_scores or {}
            weak = profile.weak_points or {}
            progress = profile.challenge_progress or {}

            has_data = any(scores.get(dim, 10) != 10 for dim in ABILITY_DIMS) or weak or progress
            if not has_data:
                return None

            ability_scores_text = "\n".join(
                f"  - {dim}: {scores.get(dim, 10)}分" for dim in ABILITY_DIMS
            )

            weak_items = sorted(
                weak.items(), key=lambda x: x[1].get("count", 0), reverse=True
            )[:5]
            weak_points_text = ""
            for cat, info in weak_items:
                weak_points_text += f"  - {cat}: 出现{info.get('count', 0)}次\n"
            if not weak_points_text:
                weak_points_text = "  暂无明显薄弱环节"

            error_patterns = profile.error_patterns or {}
            error_patterns_text = ""
            for pattern, count in (error_patterns.items() if isinstance(error_patterns, dict) else []):
                error_patterns_text += f"  - {pattern}: {count}次\n"
            if not error_patterns_text:
                error_patterns_text = "  暂无明确错误模式"

            progress_text = ""
            for lvl, info in progress.items():
                status = info.get("status", "unknown")
                attempts = info.get("attempts", 0)
                progress_text += f"  - 第{lvl}关: {status}, 尝试{attempts}次\n"
            if not progress_text:
                progress_text = "  尚未开始闯关"

            return PROFILE_SYSTEM_PROMPT_TEMPLATE.format(
                ability_scores_text=ability_scores_text,
                weak_points_text=weak_points_text,
                error_patterns_text=error_patterns_text,
                challenge_progress_text=progress_text,
                learning_style=profile.learning_style or "undetermined",
            )
        except Exception as e:
            logger.warning(f"Build profile prompt failed: {e}")
            return None

    async def _record_chat_event(self, db: AsyncSession, user_id: str, message: str):
        try:
            await learning_tracker.record_event(
                db, user_id, "chat_ask",
                detail={"message_preview": message[:100]},
            )
        except Exception as e:
            logger.warning(f"Record chat event failed: {e}")


rag_service = RAGService()
