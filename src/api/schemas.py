"""
Pydantic schemas for the HTTP API.

These define the *shape* of requests and responses. FastAPI uses them
to validate incoming JSON automatically and to generate OpenAPI docs.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.models.grammar import DrillMode


class ChatRequest(BaseModel):
    """Incoming POST /chat/stream payload."""

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Client-generated session identifier.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The user's message text.",
    )
    mode: DrillMode | None = Field(
        default=None,
        description=(
            "Optional drill mode. If provided, the server switches the "
            "session into this mode before responding."
        ),
    )


class NewSessionResponse(BaseModel):
    """Response for POST /session/new."""

    session_id: str
    mode: DrillMode


class HealthResponse(BaseModel):
    """Response for GET /health."""

    status: str = "ok"
    model: str
    environment: str