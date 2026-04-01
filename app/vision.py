from __future__ import annotations

from collections.abc import Callable
from threading import Event, Lock, Thread
from time import sleep
from typing import Any

from app.gesture import Landmark

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
        self._frame_lock = Lock()
        self._latest_frame: bytes | None = None

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

    def latest_frame(self) -> bytes | None:
        with self._frame_lock:
            return self._latest_frame

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
            message="Webcam attiva. Di' la frase magica guardando lo schermo.",
            detection_score=0.0,
        )
        hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
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
                annotated = self._annotate_frame(frame, left_hand, right_hand)
                self._store_frame(annotated)
                self.on_status(
                    available=True,
                    message="Webcam attiva. Di' la frase magica: Amo Dadu.",
                    detection_score=0.0,
                )

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

        hands_found: list[dict[str, Landmark]] = []

        for _, landmarks in zip(result.multi_handedness, result.multi_hand_landmarks):
            mapped: dict[str, Landmark] = {
                "wrist": Landmark(landmarks.landmark[0].x, landmarks.landmark[0].y),
                "thumb_ip": Landmark(landmarks.landmark[3].x, landmarks.landmark[3].y),
                "thumb_tip": Landmark(landmarks.landmark[4].x, landmarks.landmark[4].y),
                "index_pip": Landmark(landmarks.landmark[6].x, landmarks.landmark[6].y),
                "index_tip": Landmark(landmarks.landmark[8].x, landmarks.landmark[8].y),
            }
            hands_found.append(mapped)

        if not hands_found:
            return None, None

        if len(hands_found) == 1:
            return hands_found[0], None

        ordered = sorted(hands_found, key=lambda hand: hand["wrist"].x)
        return ordered[0], ordered[1]

    def _store_frame(self, frame: Any) -> None:
        if cv2 is None:
            return
        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            return
        with self._frame_lock:
            self._latest_frame = encoded.tobytes()

    def _annotate_frame(
        self,
        frame: Any,
        left_hand: dict[str, Landmark] | None,
        right_hand: dict[str, Landmark] | None,
    ) -> Any:
        if cv2 is None:
            return frame

        annotated = frame.copy()
        frame_height, frame_width = annotated.shape[:2]

        for hand, color in ((left_hand, (255, 120, 180)), (right_hand, (255, 220, 120))):
            if not hand:
                continue
            for point_name in ("wrist", "thumb_ip", "thumb_tip", "index_pip", "index_tip"):
                if point_name not in hand:
                    continue
                point = hand[point_name]
                center = (int(point.x * frame_width), int(point.y * frame_height))
                cv2.circle(annotated, center, 8, color, -1)

        cv2.putText(
            annotated,
            "Di': Amo Dadu",
            (24, 42),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            annotated,
            "I sottotitoli compaiono sotto la webcam.",
            (24, 78),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 240, 240),
            2,
        )
        return annotated
