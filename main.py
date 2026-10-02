"""
Entry point for the Smart German Grammar Bot.

Run with:
    python main.py

Then open http://localhost:8000 in your browser.
"""

from __future__ import annotations

import os

import uvicorn

from config.settings import settings


def main() -> None:
    key = settings.deepseek_api_key
    key_ok = not (
        key.startswith("placeholder")
        or key == "your_deepseek_api_key_here"
    )
    key_status = "✅ configured" if key_ok else "⚠️  placeholder (chat will fail)"

    # Bind to 0.0.0.0 so the app is reachable from outside the container
    # (Render requires this). Locally, 0.0.0.0 still means "localhost works".
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    # Enable hot-reload only when running locally (Render sets RENDER=true).
    reload = settings.is_development and not os.getenv("RENDER")

    print(
        f"\n🇩🇪  Smart German Grammar Bot\n"
        f"    Environment : {settings.app_env}\n"
        f"    Model       : {settings.deepseek_model}\n"
        f"    API key     : {key_status}\n"
        f"    Bind        : {host}:{port}\n"
        f"    API docs    : /docs\n"
    )

    if not key_ok:
        print(
            "    ⚠️  Your API key is a placeholder. The UI will load but\n"
            "        replies will fail until you set a real key.\n"
        )

    uvicorn.run(
        "src.api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()