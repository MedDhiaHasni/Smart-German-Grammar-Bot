"""
Manual test for GrammarService — dry-run, no API call.

Verifies that the service builds the correct message payload and
manages session state as expected. When a real key is present,
calling .stream_reply() will actually stream from DeepSeek.

Run:
    python -m scripts.test_service
"""

from __future__ import annotations

from src.bot.prompts import system_prompt_for
from src.models import ChatSession, DrillMode, Role
from src.services import GrammarService


def main() -> None:
    # ─── 1. Prompt generation per mode ──────────────────
    print("=== System prompts ===")
    for mode in DrillMode:
        prompt = system_prompt_for(mode)
        first_line = prompt.strip().splitlines()[0][:60]
        print(f"  {mode.value:12s} → {first_line}...")

    # ─── 2. Session state management (no API call) ──────
    print("\n=== Session state ===")
    session = ChatSession(mode=DrillMode.GENERAL)
    session.add(Role.USER, "Hallo")
    session.add(Role.ASSISTANT, "Hallo! Wie kann ich helfen?")
    print(f"  session id:    {session.session_id[:12]}...")
    print(f"  mode:          {session.mode.value}")
    print(f"  message count: {len(session.messages)}")
    print(f"  history sent to API:")
    for msg in session.history_for_api():
        print(f"    [{msg['role']:9s}] {msg['content'][:50]}")

    # ─── 3. Mode switching via service ──────────────────
    print("\n=== Service mode switch ===")
    service = GrammarService()
    service.set_mode(session, "akkusativ")
    print(f"  mode is now:   {session.mode.value}")

    try:
        service.set_mode(session, "not_a_real_mode")
    except ValueError as exc:
        print(f"  invalid mode rejected: {exc}")

    print("\n✅ GrammarService structure OK (no API call made).")


if __name__ == "__main__":
    main()