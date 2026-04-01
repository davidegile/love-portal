from __future__ import annotations

from collections.abc import Callable
from threading import Event, Thread
from time import monotonic, sleep
from typing import Any

from app.gesture import Landmark, evaluate_heart_gesture

try:
    import cv2  # type: ignore
except ImportError:  # pragma: no cover
    cv2 = None

try:
    import mediapipe as mp  # type: ignore
except ImportError:  # pragma: no cover
    mp = None


class VisionService:
    def __init__(
        self,
        on_detected: Callable[[], None],
        on_status: Callable[[bool, str, float | None], None],
        *,
        detection_threshold: float = 0.78,
        detection_hold_seconds: float = 1.0,
    ) -> None:
        self.on_detected = on_detected
        self.on_status = on_status
        self.detection_threshold = detection_threshold
        self.detection_hold_seconds = detection_hold_seconds
        self._thread: Thread | None = None
        self._stop_event = Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._run, name="vision-service", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def _run(self) -> None:  # pragma: no cover
        if cv2 is None or mp is None:
            self.on_status(
                available=False,
                message="Installa OpenCV e MediaPipe per attivare la webcam.",
                detection_score=0.0,
            )
            return

        capture = cv2.VideoCapture(0)
        if not capture.isOpened():
            self.on_status(
                available=False,
                message="Webcam non disponibile.",
                detection_score=0.0,
            )
            return

        self.on_status(
            available=True,
            message="Webcam attiva. Cerca di formare un cuore con le mani.",
            detection_score=0.0,
        )
        hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        streak_start: float | None = None

        try:
            while not self._stop_event.is_set():
                ok, frame = capture.read()
                if not ok:
                    self.on_status(
                        available=False,
                        message="Impossibile leggere dalla webcam.",
                        detection_score=0.0,
                    )
                    sleep(0.3)
                    continue

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hands.process(rgb_frame)
                left_hand, right_hand = self._extract_hands(result)
                gesture = evaluate_heart_gesture(left_hand, right_hand)
                self.on_status(
                    available=True,
                    message=gesture.reason,
                    detection_score=gesture.score,
                )

                if gesture.score >= self.detection_threshold:
                    now = monotonic()
                    if streak_start is None:
                        streak_start = now
                    elif now - streak_start >= self.detection_hold_seconds:
                        self.on_detected()
                        return
                else:
                    streak_start = None

                sleep(0.05)
        finally:
            capture.release()
            hands.close()

    def _extract_hands(
        self,
        result: Any,
    ) -> tuple[dict[str, Landmark] | None, dict[str, Landmark] | None]:
        if not result.multi_hand_landmarks or not result.multi_handedness:
            return None, None

        left_hand: dict[str, Landmark] | None = None
        right_hand: dict[str, Landmark] | None = None

        for handedness, landmarks in zip(result.multi_handedness, result.multi_hand_landmarks):
            label = handedness.classification[0].label.lower()
            mapped = {
                "wrist": Landmark(landmarks.landmark[0].x, landmarks.landmark[0].y),
                "thumb_tip": Landmark(landmarks.landmark[4].x, landmarks.landmark[4].y),
                "index_tip": Landmark(landmarks.landmark[8].x, landmarks.landmark[8].y),
            }
            if label == "left":
                left_hand = mapped
            elif label == "right":
                right_hand = mapped

        return left_hand, right_hand
