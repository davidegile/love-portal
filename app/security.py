from app.content import PIN_HINTS

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
