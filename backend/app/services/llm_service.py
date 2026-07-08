import json
import logging
from typing import AsyncIterator

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self._api_key = settings.modelarts_api_key
        self._base_url = settings.modelarts_base_url
        self._model = settings.modelarts_model

    @property
    def _chat_url(self) -> str:
        if self._base_url.endswith("/chat/completions"):
            return self._base_url
        return f"{self._base_url}/chat/completions"

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and self._base_url and self._model)

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        if not self.is_configured:
            return self._mock_response(messages)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0)) as client:
                response = await client.post(
                    self._chat_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            logger.error("LLM API timeout")
            return "抱歉，大模型响应超时，请稍后重试。"
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API HTTP error: {e.response.status_code} {e.response.text[:200]}")
            return f"抱歉，大模型服务返回错误（{e.response.status_code}），请稍后重试。"
        except Exception as e:
            logger.error(f"LLM API error: {type(e).__name__}: {e}")
            return f"抱歉，大模型调用失败（{type(e).__name__}），请稍后重试。"

    async def chat_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        if not self.is_configured:
            yield self._mock_response(messages)
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0)) as client:
                async with client.stream(
                    "POST",
                    self._chat_url,
                    headers=headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"LLM stream error: {type(e).__name__}: {e}")
            yield f"\n\n[错误：大模型流式响应失败 - {type(e).__name__}]"

    def _mock_response(self, messages: list[dict]) -> str:
        last_msg = messages[-1]["content"] if messages else ""
        return (
            f"【模拟回复】这是一个OpenGauss知识智能体的模拟响应。\n"
            f"您的问题是：{last_msg[:200]}\n\n"
            f"请配置华为云ModelArts API以获得真实回复。"
        )


llm_service = LLMService()
