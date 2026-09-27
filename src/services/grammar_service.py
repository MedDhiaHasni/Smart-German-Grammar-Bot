"""
Grammar service — the brain that ties sessions, prompts, and the
DeepSeek client together.

The public API is `GrammarService.stream_reply(...)`, an async generator
that yields response tokens. Nothing above this layer needs to know
about prompt engineering or HTTP.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from src.bot.prompts import system_prompt_for
from src.models.chat import ChatSession, Role
from src.services.deepseek_client import DeepSeekClient
from src.utils.logger import get_logger

log = get_logger(__name__)


class GrammarService:
    """
    Orchestrates a German tutoring conversation.

    Typical usage from the API layer:

        service = GrammarService()
        async for token in service.stream_reply(session, user_text):
            yield token
    """

    def __init__(self, client: DeepSeekClient | None = None) -> None:
        self.client = client or DeepSeekClient()

    # ─── Public API ──────────────────────────────────────

    async def stream_reply(
        self,
        session: ChatSession,
        user_text: str,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Append `user_text` to `session`, stream the assistant's reply
        token-by-token, and record the full reply in the session once
        the stream completes.

        Yields:
            Individual text tokens as they arrive.
        """
        # 1. Record the user's message
        session.add(Role.USER, user_text)

        # 2. Assemble the payload sent to the model:
        #    system prompt first, then the full message history.
        messages: list[dict[str, str]] = [
            {
                "role": Role.SYSTEM.value,
                "content": system_prompt_for(session.mode),
            },
            *session.history_for_api(),
        ]

        log.info(
            "Streaming reply: session=%s mode=%s history=%d",
            session.session_id[:8],
            session.mode.value,
            len(session.messages),
        )

        # 3. Stream tokens from DeepSeek, accumulating them for the record
        collected: list[str] = []
        try:
            async for token in self.client.stream(
                messages, temperature=temperature
            ):
                collected.append(token)
                yield token
        except Exception:
            log.exception(
                "Error while streaming reply for session %s",
                session.session_id[:8],
            )
            # Re-raise after logging — API layer decides how to surface it.
            raise

        # 4. Persist the assistant's full reply into the session
        full_reply = "".join(collected).strip()
        if full_reply:
            session.add(Role.ASSISTANT, full_reply)
            log.info(
                "Reply complete: session=%s chars=%d",
                session.session_id[:8],
                len(full_reply),
            )

    def set_mode(self, session: ChatSession, mode_str: str) -> None:
        """
        Change the drill mode of an existing session.

        Called when the user clicks a sidebar button. Accepts the
        string value of a DrillMode (e.g. "akkusativ").
        """
        from src.models.grammar import DrillMode

        try:
            mode = DrillMode(mode_str)
        except ValueError as exc:
            raise ValueError(
                f"Unknown drill mode: {mode_str!r}. "
                f"Valid modes: {[m.value for m in DrillMode]}"
            ) from exc

        session.mode = mode
        log.info(
            "Mode changed: session=%s mode=%s",
            session.session_id[:8],
            mode.value,
        )