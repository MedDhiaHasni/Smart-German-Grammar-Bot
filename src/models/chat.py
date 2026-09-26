"""
Domain models for a chat session with the bot.

Kept independent of any web framework so they can be used from
CLI, tests, or the FastAPI layer without modification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from src.models.grammar import DrillMode


class Role(str, Enum):
    """Who produced a given chat message."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class ChatMessage:
    """A single message in a conversation."""

    role: Role
    content: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_api_dict(self) -> dict[str, str]:
        """
        Convert to the minimal shape the DeepSeek/OpenAI-style API expects:
        only `role` and `content`, no metadata.
        """
        return {"role": self.role.value, "content": self.content}


@dataclass
class ChatSession:
    """
    A single conversation thread.

    Mutable by design: messages get appended as the conversation
    progresses. `session_id` is auto-generated but can be overridden
    (useful in tests).
    """

    session_id: str = field(default_factory=lambda: uuid4().hex)
    mode: DrillMode = DrillMode.GENERAL
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def add(self, role: Role, content: str) -> ChatMessage:
        """Append a message and return it."""
        msg = ChatMessage(role=role, content=content)
        self.messages.append(msg)
        return msg

    def history_for_api(self) -> list[dict[str, str]]:
        """Return all messages in the shape the DeepSeek API expects."""
        return [m.to_api_dict() for m in self.messages]

    def clear(self) -> None:
        """Wipe conversation history (keep session_id and mode)."""
        self.messages.clear()