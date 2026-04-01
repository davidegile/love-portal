from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from time import time

from app.content import LETTER_HTML, LETTER_TITLE, TRIGGER_PHRASE
from app.security import hint_for_attempt, verify_pin, verify_trigger_phrase


@dataclass
class ExperienceSnapshot:
    phase: str
    pin_attempts: int
    hint: str
    status_message: str
    letter_title: str
    letter_html: str
    vision_available: bool
    vision_message: str
    last_detection_score: float
    fullscreen_required: bool
    live_transcript: str
    heard_phrase: str
    trigger_phrase: str
    speech_supported: bool


@dataclass
class ExperienceState:
    phase: str = "waiting_for_phrase"
    pin_attempts: int = 0
    hint: str = ""
    status_message: str = "Guarda la webcam e di' la frase magica."
    vision_available: bool = False
    vision_message: str = "In attesa della webcam..."
    last_detection_score: float = 0.0
    fullscreen_required: bool = True
    opened_at: float | None = None
    live_transcript: str = ""
    heard_phrase: str = ""
    speech_supported: bool = True
    _lock: Lock = field(default_factory=Lock, repr=False)

    def snapshot(self) -> ExperienceSnapshot:
        with self._lock:
            return ExperienceSnapshot(
                phase=self.phase,
                pin_attempts=self.pin_attempts,
                hint=self.hint,
                status_message=self.status_message,
                letter_title=LETTER_TITLE,
                letter_html=LETTER_HTML,
                vision_available=self.vision_available,
                vision_message=self.vision_message,
                last_detection_score=round(self.last_detection_score, 3),
                fullscreen_required=self.fullscreen_required,
                live_transcript=self.live_transcript,
                heard_phrase=self.heard_phrase,
                trigger_phrase=TRIGGER_PHRASE,
                speech_supported=self.speech_supported,
            )

    def update_vision_status(
        self,
        *,
        available: bool,
        message: str,
        detection_score: float | None = None,
    ) -> None:
        with self._lock:
            self.vision_available = available
            self.vision_message = message
            if detection_score is not None:
                self.last_detection_score = detection_score

    def update_transcript(self, transcript: str, *, supported: bool = True) -> None:
        with self._lock:
            self.speech_supported = supported
            self.live_transcript = transcript.strip()

    def open_portal(self) -> bool:
        with self._lock:
            if self.phase != "waiting_for_phrase":
                return False
            self.phase = "portal_open"
            self.status_message = "Il portale si e' aperto. Inserisci il codice."
            self.hint = ""
            self.opened_at = time()
            return True

    def hear_phrase(self, transcript: str) -> bool:
        with self._lock:
            self.live_transcript = transcript.strip()
            self.heard_phrase = transcript.strip()
            if self.phase != "waiting_for_phrase":
                return False
            if not verify_trigger_phrase(transcript):
                self.status_message = "Non ancora. Pronuncia chiaramente la frase magica."
                return False
            self.phase = "portal_open"
            self.status_message = "Il portale si e' aperto. Inserisci il codice."
            self.hint = ""
            self.opened_at = time()
            return True

    def submit_pin(self, pin: str) -> tuple[bool, str]:
        with self._lock:
            if self.phase != "portal_open":
                return False, "Il portale non e' ancora pronto."

            if verify_pin(pin):
                self.phase = "letter_unlocked"
                self.status_message = "Benvenuta nella lettera."
                self.hint = ""
                return True, "Codice corretto."

            self.pin_attempts += 1
            self.hint = hint_for_attempt(self.pin_attempts)
            self.status_message = "Non ancora. Respira e riprova."
            return False, self.hint

    def reset(self) -> None:
        with self._lock:
            self.phase = "waiting_for_phrase"
            self.pin_attempts = 0
            self.hint = ""
            self.status_message = "Guarda la webcam e di' la frase magica."
            self.last_detection_score = 0.0
            self.opened_at = None
            self.live_transcript = ""
            self.heard_phrase = ""
