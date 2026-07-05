import json
import logging
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.chat import ChatSession, ChatMessage
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service

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
            {"role": "system", "content": f"参考知识：\n{context}"},
        ]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        answer = await self.llm_service.chat(messages)

        if db:
            session_id, _ = await self._save_conversation(
                session_id, message, answer, sources, db
            )

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


rag_service = RAGService()
