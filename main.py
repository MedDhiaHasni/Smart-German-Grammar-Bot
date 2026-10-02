"""
Entry point for the Smart German Grammar Bot.

Run with:
    python main.py

Then open http://localhost:8000 in your browser.
"""

from __future__ import annotations

import uvicorn

from config.settings import settings


def main() -> None:
    key = settings.deepseek_api_key
    key_ok = not (
        key.startswith("placeholder")
        or key == "your_deepseek_api_key_here"
    )
    key_status = "✅ configured" if key_ok else "⚠️  placeholder (chat will fail)"

    print(
        f"\n🇩🇪  Smart German Grammar Bot\n"
        f"    Environment : {settings.app_env}\n"
        f"    Model       : {settings.deepseek_model}\n"
        f"    API key     : {key_status}\n"
        f"    Open        : http://localhost:8000\n"
        f"    API docs    : http://localhost:8000/docs\n"
    )

    if not key_ok:
        print(
            "    ⚠️  Your API key is a placeholder. The UI will load but\n"
            "        replies will fail until you set a real key in .env.\n"
        )

        import os

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = settings.is_development and host == "127.0.0.1"

    uvicorn.run(
        "src.api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()