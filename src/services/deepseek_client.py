"""
Async streaming client for an OpenAI-compatible chat completions API
(DeepSeek, OpenRouter, ...).

If the configured model fails (404 retired, 429 rate limit, 5xx), the client
automatically falls back to other free OpenRouter models.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from config.settings import settings
from src.utils.logger import get_logger

log = get_logger(__name__)

# Tried in order after the configured model. Free models come and go,
# so keep several here.
FALLBACK_MODELS = [
    "openrouter/free",
    "openai/gpt-oss-120b:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
]

# Status codes where trying a different model makes sense.
RETRY_NEXT_MODEL = {400, 404, 408, 429, 500, 502, 503, 504}


class DeepSeekError(RuntimeError):
    """Raised when the API returns an error or is unreachable."""


class DeepSeekClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or settings.deepseek_api_key
        self.base_url = (base_url or settings.deepseek_base_url).rstrip("/")
        self.model = model or settings.deepseek_model
        self.timeout = timeout

        if not self.api_key:
            raise DeepSeekError(
                "No API key configured. Set DEEPSEEK_API_KEY in .env."
            )

        if (
            self.api_key.startswith("placeholder")
            or self.api_key == "your_deepseek_api_key_here"
        ):
            log.warning(
                "API key is still a placeholder. "
                "Chat will fail until you set a real key in .env."
            )

    def _models_to_try(self) -> list[str]:
        models = [self.model]
        for m in FALLBACK_MODELS:
            if m not in models:
                models.append(m)
        return models

    # ─── Public API ──────────────────────────────────────

    async def stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Yield response tokens, falling back to other models on failure."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        errors: list[str] = []

        for model in self._models_to_try():
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }
            log.info("Streaming: model=%s, messages=%d", model, len(messages))

            yielded = False
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream(
                        "POST", url, headers=headers, json=payload
                    ) as response:
                        if response.status_code != 200:
                            body = (await response.aread()).decode(
                                "utf-8", errors="replace"
                            )
                            log.error(
                                "HTTP %s from %s: %s",
                                response.status_code,
                                model,
                                body[:300],
                            )
                            if response.status_code in (401, 403):
                                raise DeepSeekError(
                                    "Authentication failed: your DEEPSEEK_API_KEY "
                                    "is missing, invalid, or expired."
                                )
                            if response.status_code in RETRY_NEXT_MODEL:
                                errors.append(
                                    f"{model}: HTTP {response.status_code}"
                                )
                                continue
                            raise DeepSeekError(
                                f"API returned HTTP {response.status_code}: "
                                f"{body[:200]}"
                            )

                        async for line in response.aiter_lines():
                            token = self._parse_sse_line(line)
                            if token is not None:
                                yielded = True
                                yield token

                if yielded:
                    return
                errors.append(f"{model}: empty reply")

            except httpx.RequestError as exc:
                if yielded:
                    # Already sent part of the answer; can't switch models now.
                    raise DeepSeekError(f"Connection lost: {exc}") from exc
                log.warning("Network error with %s: %s", model, exc)
                errors.append(f"{model}: network error")
                continue

        raise DeepSeekError(
            "All models failed. Tried: " + "; ".join(errors)
        )

    # ─── Internals ───────────────────────────────────────

    @staticmethod
    def _parse_sse_line(line: str) -> str | None:
        if not line or not line.startswith("data:"):
            return None

        data = line[len("data:"):].strip()
        if data == "[DONE]":
            return None

        try:
            obj = json.loads(data)
        except json.JSONDecodeError:
            log.warning("Malformed SSE chunk: %r", data[:200])
            return None

        choices = obj.get("choices") or []
        if not choices:
            return None

        delta = choices[0].get("delta") or {}
        content = delta.get("content")
        return content if content else None