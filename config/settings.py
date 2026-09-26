"""
Global configuration for Smart German Grammar Bot.

Loads environment variables from .env and exposes a validated,
typed configuration singleton. Fails fast if required secrets
are missing.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# ─── Locate .env relative to project root ────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load .env into os.environ. override=False ensures real
# shell-exported vars take precedence over the .env file.
load_dotenv(dotenv_path=ENV_PATH, override=False)


class ConfigurationError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""

    # ─── DeepSeek API ────────────────────────────────────
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str

    # ─── Application ─────────────────────────────────────
    app_env: str
    log_level: str
    project_root: Path

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"


def _require_env(key: str) -> str:
    """Fetch a required env var or exit with a clean message."""
    value = os.getenv(key, "").strip()
    if not value:
        print(
            f"\n❌ Configuration Error: Required environment variable "
            f"'{key}' is missing or empty.\n"
            f"   → Copy '.env.example' to '.env' and fill in your value.\n"
            f"   → Expected file location: {ENV_PATH}\n",
            file=sys.stderr,
        )
        sys.exit(1)
    return value


def _optional_env(key: str, default: str) -> str:
    """Fetch an optional env var with a fallback."""
    return os.getenv(key, default).strip() or default


def _load_settings() -> Settings:
    """Build a validated Settings instance."""
    return Settings(
        deepseek_api_key=_require_env("DEEPSEEK_API_KEY"),
        deepseek_base_url=_optional_env(
            "DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"
        ),
        deepseek_model=_optional_env("DEEPSEEK_MODEL", "deepseek-chat"),
        app_env=_optional_env("APP_ENV", "development"),
        log_level=_optional_env("LOG_LEVEL", "INFO"),
        project_root=PROJECT_ROOT,
    )


# ─── Global singleton ────────────────────────────────────
settings = _load_settings()