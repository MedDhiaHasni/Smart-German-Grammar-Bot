"""
Domain models for German grammar concepts.

These are intentionally small, immutable value objects — they describe
*what* a German noun / case / gender is, not how to teach them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ─── Enums ───────────────────────────────────────────────

class Gender(str, Enum):
    """Grammatical gender of a German noun."""

    MASCULINE = "der"
    FEMININE = "die"
    NEUTER = "das"


class Case(str, Enum):
    """The four German grammatical cases."""

    NOMINATIV = "Nominativ"
    AKKUSATIV = "Akkusativ"
    DATIV = "Dativ"
    GENITIV = "Genitiv"


class DrillMode(str, Enum):
    """Which mode the bot is currently in."""

    GENERAL = "general"
    DER_DIE_DAS = "der_die_das"
    AKKUSATIV = "akkusativ"
    DATIV = "dativ"
    GENITIV = "genitiv"
    VOCAB = "vocab"


# ─── Value Objects ───────────────────────────────────────

@dataclass(frozen=True)
class GermanNoun:
    """
    A single German noun with its grammatical metadata.

    Example:
        GermanNoun(
            word="Tisch",
            gender=Gender.MASCULINE,
            plural="Tische",
            english="table",
            example="Der Tisch ist groß.",
        )
    """

    word: str
    gender: Gender
    plural: str
    english: str
    example: str = ""

    @property
    def article(self) -> str:
        """Return 'der' / 'die' / 'das' for this noun."""
        return self.gender.value

    @property
    def full_form(self) -> str:
        """Return the noun with its definite article, e.g. 'der Tisch'."""
        return f"{self.article} {self.word}"


@dataclass(frozen=True)
class DrillPrompt:
    """
    A single drill question sent to the learner, e.g.
    'What is the article for Tisch?'.

    Kept separate from GermanNoun so we can later generate drills that
    aren't tied to a specific noun (e.g. sentence transformations).
    """

    mode: DrillMode
    question: str
    expected_answer: str
    hint: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)