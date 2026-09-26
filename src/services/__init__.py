"""Service layer for the Smart German Grammar Bot."""

from src.services.deepseek_client import DeepSeekClient, DeepSeekError

__all__ = ["DeepSeekClient", "DeepSeekError"]