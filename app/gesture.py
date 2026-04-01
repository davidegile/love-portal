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
    left_thumb_joint = left_hand.get("thumb_ip", left_thumb)
    right_thumb_joint = right_hand.get("thumb_ip", right_thumb)
    left_index_joint = left_hand.get("index_pip", left_index)
    right_index_joint = right_hand.get("index_pip", right_index)

    thumb_gap = dist((left_thumb.x, left_thumb.y), (right_thumb.x, right_thumb.y))
    index_gap = dist((left_index.x, left_index.y), (right_index.x, right_index.y))
    wrist_gap = dist((left_wrist.x, left_wrist.y), (right_wrist.x, right_wrist.y))
    thumb_joint_gap = dist(
        (left_thumb_joint.x, left_thumb_joint.y),
        (right_thumb_joint.x, right_thumb_joint.y),
    )
    index_joint_gap = dist(
        (left_index_joint.x, left_index_joint.y),
        (right_index_joint.x, right_index_joint.y),
    )
    thumbs_below_indexes = float(
        left_thumb.y >= left_index.y - 0.05 and right_thumb.y >= right_index.y - 0.05
    )
    indexes_above_wrists = float(
        left_index.y < left_wrist.y and right_index.y < right_wrist.y
    )

    thumb_score = 1.0 - min(thumb_gap / 0.18, 1.0)
    index_score = 1.0 - min(index_gap / 0.24, 1.0)
    thumb_joint_score = 1.0 - min(thumb_joint_gap / 0.20, 1.0)
    index_joint_score = 1.0 - min(index_joint_gap / 0.26, 1.0)
    width_score = min(wrist_gap / 0.45, 1.0)

    score = _clamp_score(
        (thumb_score * 0.28)
        + (index_score * 0.28)
        + (thumb_joint_score * 0.14)
        + (index_joint_score * 0.14)
        + (width_score * 0.08)
        + (thumbs_below_indexes * 0.04)
        + (indexes_above_wrists * 0.04)
    )
    detected = score >= 0.64
    if detected:
        reason = "Cuore rilevato."
    elif thumb_gap > 0.28 or index_gap > 0.32:
        reason = "Avvicina di piu' pollici e indici."
    elif wrist_gap < 0.18:
        reason = "Allontana leggermente i polsi e curva le dita."
    else:
        reason = "Gesto quasi giusto, chiudi meglio la punta del cuore."
    return HeartGestureResult(detected, score, reason)
