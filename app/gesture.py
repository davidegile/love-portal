from __future__ import annotations

from dataclasses import dataclass
from math import dist


@dataclass(frozen=True)
class Landmark:
    x: float
    y: float


@dataclass(frozen=True)
class HeartGestureResult:
    detected: bool
    score: float
    reason: str


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))


def evaluate_heart_gesture(
    left_hand: dict[str, Landmark] | None,
    right_hand: dict[str, Landmark] | None,
) -> HeartGestureResult:
    if not left_hand or not right_hand:
        return HeartGestureResult(False, 0.0, "Servono entrambe le mani.")

    required_keys = {"thumb_tip", "index_tip", "wrist"}
    if not required_keys.issubset(left_hand) or not required_keys.issubset(right_hand):
        return HeartGestureResult(False, 0.0, "Landmark incompleti.")

    left_thumb = left_hand["thumb_tip"]
    right_thumb = right_hand["thumb_tip"]
    left_index = left_hand["index_tip"]
    right_index = right_hand["index_tip"]
    left_wrist = left_hand["wrist"]
    right_wrist = right_hand["wrist"]

    thumb_gap = dist((left_thumb.x, left_thumb.y), (right_thumb.x, right_thumb.y))
    index_gap = dist((left_index.x, left_index.y), (right_index.x, right_index.y))
    wrist_gap = dist((left_wrist.x, left_wrist.y), (right_wrist.x, right_wrist.y))
    thumbs_below_indexes = float(
        left_thumb.y > left_index.y and right_thumb.y > right_index.y
    )

    thumb_score = 1.0 - min(thumb_gap / 0.18, 1.0)
    index_score = 1.0 - min(index_gap / 0.22, 1.0)
    width_score = min(wrist_gap / 0.35, 1.0)

    score = _clamp_score(
        (thumb_score * 0.4) + (index_score * 0.4) + (width_score * 0.1) + (thumbs_below_indexes * 0.1)
    )
    detected = score >= 0.78
    reason = "Cuore rilevato." if detected else "Gesto non ancora abbastanza chiaro."
    return HeartGestureResult(detected, score, reason)
