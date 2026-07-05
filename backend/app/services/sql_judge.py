import re
import logging


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sql_practice import SqlQuestion, SqlSubmission
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

SQL_JUDGE_PROMPT = """你是一个openGauss数据库SQL判题专家。请根据以下信息判断用户的SQL是否正确。

题目描述：
{description}

参考答案SQL：
{reference_sql}

用户提交的SQL：
{user_sql}

请从以下维度评估：
1. 语法正确性：SQL语法是否符合openGauss规范
2. 逻辑正确性：是否实现了题目要求的功能
3. 性能优化：是否考虑了查询效率

请以JSON格式返回评估结果：
{{
    "is_correct": true/false,
    "score": 0-100,
    "feedback": "详细的评价和改进建议",
    "syntax_correct": true/false,
    "logic_correct": true/false,
    "optimization_suggestion": "优化建议"
}}

只返回JSON，不要其他内容。"""


class SqlJudgeService:
    def __init__(self):
        self.llm_service = llm_service

    async def judge(
        self,
        question_id: str,
        user_sql: str,
        db: AsyncSession,
    ) -> dict:
        result = await db.execute(
            select(SqlQuestion).where(SqlQuestion.id == question_id)
        )
        question = result.scalar_one_or_none()
        if not question:
            return {"error": "题目不存在"}

        prompt = SQL_JUDGE_PROMPT.format(
            description=question.description,
            reference_sql=question.reference_sql,
            user_sql=user_sql,
        )

        messages = [
            {"role": "system", "content": "你是openGauss数据库SQL判题专家，只返回JSON格式的评估结果。"},
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.llm_service.chat(messages, temperature=0.1)
            judge_result = self._parse_judge_response(response)
        except Exception as e:
            logger.error(f"SQL判题失败: {e}")
            judge_result = {
                "is_correct": False,
                "score": 0,
                "feedback": f"判题服务异常：{str(e)}",
                "syntax_correct": False,
                "logic_correct": False,
                "optimization_suggestion": "",
            }

        submission = SqlSubmission(
            question_id=question_id,
            user_sql=user_sql,
            is_correct=judge_result.get("is_correct", False),
            score=judge_result.get("score", 0),
            feedback=judge_result.get("feedback", ""),
            execution_result="",
        )
        db.add(submission)
        await db.commit()
        await db.refresh(submission)

        return {
            "id": str(submission.id),
            "question_id": str(question_id),
            "user_sql": user_sql,
            "is_correct": submission.is_correct,
            "score": submission.score,
            "feedback": submission.feedback,
            "execution_result": submission.execution_result,
            "created_at": submission.created_at.isoformat(),
        }

    def _parse_judge_response(self, response: str) -> dict:
        import json
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {
            "is_correct": False,
            "score": 0,
            "feedback": response,
            "syntax_correct": False,
            "logic_correct": False,
            "optimization_suggestion": "",
        }

    async def generate_questions(self, chapter: str, count: int = 5) -> list[dict]:
        prompt = f"""请为openGauss数据库第{chapter}章生成{count}道SQL练习题。

要求：
1. 每道题包含：title, description, difficulty(easy/medium/hard), hint, reference_sql, setup_sql
2. SQL语句必须兼容openGauss语法
3. 难度分布均匀

请以JSON数组格式返回，只返回JSON，不要其他内容。"""

        messages = [
            {"role": "system", "content": "你是openGauss数据库教学专家，擅长设计SQL练习题。"},
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.llm_service.chat(messages, temperature=0.7)
            import json
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"生成题目失败: {e}")

        return []


sql_judge_service = SqlJudgeService()