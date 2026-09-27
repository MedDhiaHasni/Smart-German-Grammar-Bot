"""
FastAPI application for the Smart German Grammar Bot.

Two responsibilities:
  1. Serve the static frontend (added in Step 7).
  2. Expose streaming chat endpoints for the browser to call.

Session state is kept in an in-memory registry for now. This is fine
for a single-process dev server; swap for Redis/DB if we ever scale.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config.settings import settings
from src.api.schemas import ChatRequest, HealthResponse, NewSessionResponse
from src.models.chat import ChatSession
from src.services import DeepSeekError, GrammarService
from src.utils.logger import get_logger

log = get_logger(__name__)

app = FastAPI(
    title="Smart German Grammar Bot",
    description="A web-based German grammar tutor powered by DeepSeek.",
    version="0.1.0",
)

# ─── CORS ────────────────────────────────────────────────
# In dev we allow localhost origins so the frontend can call the API
# from a different port during development. In production, tighten this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Shared service + session registry ───────────────────

_service = GrammarService()
_sessions: dict[str, ChatSession] = {}


def _get_or_create_session(session_id: str) -> ChatSession:
    """Look up an existing session or create a fresh one."""
    session = _sessions.get(session_id)
    if session is None:
        session = ChatSession(session_id=session_id)
        _sessions[session_id] = session
        log.info("Created new session %s", session_id[:8])
    return session


# ─── Endpoints ───────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness probe — used by hosts and monitoring."""
    return HealthResponse(
        status="ok",
        model=settings.deepseek_model,
        environment=settings.app_env,
    )


@app.post("/session/new", response_model=NewSessionResponse)
async def new_session() -> NewSessionResponse:
    """Create a fresh session and return its ID."""
    session = ChatSession()
    _sessions[session.session_id] = session
    log.info("New session created: %s", session.session_id[:8])
    return NewSessionResponse(
        session_id=session.session_id,
        mode=session.mode,
    )


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    """
    Stream the assistant's reply as Server-Sent Events.

    The frontend opens this endpoint with fetch() and reads the body
    incrementally; every chunk is a `data: <token>\\n\\n` line.
    """
    session = _get_or_create_session(req.session_id)

    # Switch mode if the client asked for one (e.g. sidebar button)
    if req.mode is not None and req.mode != session.mode:
        _service.set_mode(session, req.mode.value)

    async def token_generator() -> AsyncIterator[str]:
        try:
            async for token in _service.stream_reply(session, req.message):
                # SSE wire format: "data: <payload>\n\n"
                # Newlines inside a token must be escaped as separate
                # data: lines. We do a minimal escape here.
                safe = token.replace("\r", "")
                yield f"data: {safe}\n\n"
        except DeepSeekError as exc:
            log.error("DeepSeek error: %s", exc)
            yield f"event: error\ndata: {exc}\n\n"
        finally:
            # Signal clean end of stream so the client knows
            yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable proxy buffering
        },
    )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str) -> dict[str, str]:
    """Forget a session (used when the user clicks 'New chat')."""
    _sessions.pop(session_id, None)
    return {"status": "deleted", "session_id": session_id}