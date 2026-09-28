"""
Async streaming client for the DeepSeek chat completions API.

DeepSeek exposes an OpenAI-compatible endpoint, so the request shape
and streaming protocol match OpenAI's. We only implement what we need.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx

from config.settings import settings
from src.utils.logger import get_logger

log = get_logger(__name__)


class DeepSeekError(RuntimeError):
    """Raised when the DeepSeek API returns an error or is unreachable."""


class DeepSeekClient:
    """
    Minimal async client for DeepSeek's `/chat/completions` endpoint.

    Usage:
        client = DeepSeekClient()
        async for token in client.stream(messages):
            print(token, end="", flush=True)
    """

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
                "No DeepSeek API key configured. Set DEEPSEEK_API_KEY in .env."
            )

        if (
            self.api_key.startswith("placeholder")
            or self.api_key == "your_deepseek_api_key_here"
        ):
            log.warning(
                "DeepSeek API key is still a placeholder. "
                "Chat will fail until you set a real key in .env."
            )

    # ─── Public API ──────────────────────────────────────

    async def stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Send `messages` to DeepSeek and yield response tokens as they arrive.

        Args:
            messages: OpenAI-style chat messages
                      (e.g. [{"role": "user", "content": "Hallo"}]).
            temperature: 0.0 = deterministic, 1.0 = creative.
            max_tokens: hard cap on the reply length.

        Yields:
            Individual text chunks (usually one or two words each).

        Raises:
            DeepSeekError: on network failure or non-200 HTTP status.
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        log.info(
            "Streaming from DeepSeek: model=%s, messages=%d",
            self.model,
            len(messages),
        )

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
                            "DeepSeek HTTP %s: %s",
                            response.status_code,
                            body[:500],
                        )
                        if response.status_code in (401, 403):
                            raise DeepSeekError(
                                "Authentication failed — your DEEPSEEK_API_KEY "
                                "is missing, invalid, or expired. Check .env."
                            )
                        if response.status_code == 429:
                            raise DeepSeekError(
                                "Rate limit reached. Wait a moment and try again, "
                                "or upgrade your DeepSeek plan."
                            )
                        raise DeepSeekError(
                            f"DeepSeek API returned HTTP "
                            f"{response.status_code}: {body[:200]}"
                        )

                    async for line in response.aiter_lines():
                        token = self._parse_sse_line(line)
                        if token is not None:
                            yield token

        except httpx.RequestError as exc:
            log.exception("Network error contacting DeepSeek")
            raise DeepSeekError(f"Network error: {exc}") from exc

    # ─── Internals ───────────────────────────────────────

    @staticmethod
    def _parse_sse_line(line: str) -> str | None:
        """
        Parse a single Server-Sent Events line from the stream.

        DeepSeek (like OpenAI) sends lines like:
            data: {"choices":[{"delta":{"content":"Hallo"}}]}
            data: [DONE]

        Return the text chunk, or None if the line carries no content.
        """
        if not line or not line.startswith("data:"):
            return None

        data = line[len("data:"):].strip()
        if data == "[DONE]":
            return None

        import json  # local import keeps module import cheap

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