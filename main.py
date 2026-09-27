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
    print(
        f"\n🇩🇪  Smart German Grammar Bot\n"
        f"    Environment : {settings.app_env}\n"
        f"    Model       : {settings.deepseek_model}\n"
        f"    Open        : http://localhost:8000\n"
        f"    API docs    : http://localhost:8000/docs\n\n"
    )
    uvicorn.run(
        "src.api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()