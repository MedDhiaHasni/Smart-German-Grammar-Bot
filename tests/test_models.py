"""
Smoke tests for the domain models.

We run these with plain Python for now (no pytest yet); later we'll
switch to pytest once the project grows.
"""

from src.models import (
    Case,
    ChatMessage,
    ChatSession,
    DrillMode,
    Gender,
    GermanNoun,
    Role,
)


def test_german_noun_article_and_full_form() -> None:
    tisch = GermanNoun(
        word="Tisch",
        gender=Gender.MASCULINE,
        plural="Tische",
        english="table",
        example="Der Tisch ist groß.",
    )
    assert tisch.article == "der"
    assert tisch.full_form == "der Tisch"

    katze = GermanNoun(
        word="Katze",
        gender=Gender.FEMININE,
        plural="Katzen",
        english="cat",
    )
    assert katze.article == "die"
    assert katze.full_form == "die Katze"

    kind = GermanNoun(
        word="Kind",
        gender=Gender.NEUTER,
        plural="Kinder",
        english="child",
    )
    assert kind.article == "das"
    assert kind.full_form == "das Kind"


def test_gender_enum_values_match_german_articles() -> None:
    assert Gender.MASCULINE.value == "der"
    assert Gender.FEMININE.value == "die"
    assert Gender.NEUTER.value == "das"


def test_case_enum_members() -> None:
    assert {c.value for c in Case} == {
        "Nominativ",
        "Akkusativ",
        "Dativ",
        "Genitiv",
    }


def test_chat_message_serialization() -> None:
    msg = ChatMessage(role=Role.USER, content="Hallo")
    assert msg.to_api_dict() == {"role": "user", "content": "Hallo"}


def test_chat_session_flow() -> None:
    session = ChatSession(mode=DrillMode.AKKUSATIV)
    session.add(Role.USER, "What is the Akkusativ of 'der Mann'?")
    session.add(Role.ASSISTANT, "den Mann")

    assert len(session.messages) == 2
    assert session.messages[0].role == Role.USER
    assert session.messages[1].content == "den Mann"

    api_history = session.history_for_api()
    assert api_history == [
        {"role": "user", "content": "What is the Akkusativ of 'der Mann'?"},
        {"role": "assistant", "content": "den Mann"},
    ]

    session.clear()
    assert session.messages == []
    assert session.mode == DrillMode.AKKUSATIV  # mode survives clear


def test_session_id_is_unique() -> None:
    a = ChatSession()
    b = ChatSession()
    assert a.session_id != b.session_id


if __name__ == "__main__":
    # Allow running this file directly: `python tests/test_models.py`
    test_german_noun_article_and_full_form()
    test_gender_enum_values_match_german_articles()
    test_case_enum_members()
    test_chat_message_serialization()
    test_chat_session_flow()
    test_session_id_is_unique()
    print("OK all model tests passed.")