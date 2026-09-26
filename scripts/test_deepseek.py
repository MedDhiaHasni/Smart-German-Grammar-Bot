"""
Manual smoke test for DeepSeekClient.

Run it with:
    python -m scripts.test_deepseek

It will stream a short reply from the model to your terminal.
Requires a valid DEEPSEEK_API_KEY in .env.
"""

from __future__ import annotations

import asyncio
import sys

from src.services import DeepSeekClient, DeepSeekError


async def main() -> int:
    client = DeepSeekClient()
    messages = [
        {
            "role": "system",
            "content": (
                "You are a concise German tutor. Reply in 2 short sentences."
            ),
        },
        {
            "role": "user",
            "content": "Was ist der Unterschied zwischen Dativ und Akkusativ?",
        },
    ]

    print("\n--- Streaming reply from DeepSeek ---\n")
    try:
        async for token in client.stream(messages, max_tokens=200):
            print(token, end="", flush=True)
    except DeepSeekError as exc:
        print(f"\n\n[ERROR] {exc}", file=sys.stderr)
        return 1

    print("\n\n--- End of stream ---\n")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))