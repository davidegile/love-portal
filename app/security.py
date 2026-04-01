import unicodedata

from app.content import PIN_HINTS, TRIGGER_PHRASE

SECRET_PIN = "2805"


def is_valid_pin_format(pin: str) -> bool:
    return pin.isdigit() and len(pin) == 4


def verify_pin(pin: str) -> bool:
    return is_valid_pin_format(pin) and pin == SECRET_PIN


def hint_for_attempt(attempt_count: int) -> str:
    if attempt_count <= 0:
        return ""
    hint_index = min(attempt_count - 1, len(PIN_HINTS) - 1)
    return PIN_HINTS[hint_index]


def normalize_phrase(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return " ".join(normalized.lower().strip().split())


def verify_trigger_phrase(text: str) -> bool:
    candidate = normalize_phrase(text)
    trigger = normalize_phrase(TRIGGER_PHRASE)
    return trigger in candidate
