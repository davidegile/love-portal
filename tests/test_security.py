from app.security import hint_for_attempt, is_valid_pin_format, verify_pin, verify_trigger_phrase


def test_pin_format_accepts_only_four_digits() -> None:
    assert is_valid_pin_format("2805") is True
    assert is_valid_pin_format("28a5") is False
    assert is_valid_pin_format("280") is False


def test_verify_pin_requires_exact_secret() -> None:
    assert verify_pin("2805") is True
    assert verify_pin("0000") is False


def test_hint_progression_caps_on_last_hint() -> None:
    assert hint_for_attempt(1).startswith("Piccolo indizio")
    assert hint_for_attempt(4).startswith("Ultimo indizio")
    assert hint_for_attempt(10).startswith("Ultimo indizio")


def test_trigger_phrase_matches_even_with_accents() -> None:
    assert verify_trigger_phrase("Amo Dadu") is True
    assert verify_trigger_phrase("amo dadù") is True
    assert verify_trigger_phrase("ciao amo dadù tantissimo") is True
    assert verify_trigger_phrase("ti voglio bene") is False
