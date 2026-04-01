from app.state import ExperienceState


def test_open_portal_transitions_from_waiting() -> None:
    state = ExperienceState()

    opened = state.open_portal()

    assert opened is True
    assert state.snapshot().phase == "portal_open"


def test_submit_pin_unlocks_letter_for_correct_code() -> None:
    state = ExperienceState()
    state.open_portal()

    ok, message = state.submit_pin("2805")

    assert ok is True
    assert message == "Codice corretto."
    assert state.snapshot().phase == "letter_unlocked"


def test_submit_pin_returns_progressive_hint_on_failure() -> None:
    state = ExperienceState()
    state.open_portal()

    ok, message = state.submit_pin("1111")

    assert ok is False
    assert "indizio" in message.lower()
    assert state.snapshot().pin_attempts == 1
