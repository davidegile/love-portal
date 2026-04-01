from app.gesture import Landmark, evaluate_heart_gesture


def test_heart_gesture_detects_close_fingertips() -> None:
    left_hand = {
        "wrist": Landmark(0.30, 0.72),
        "thumb_ip": Landmark(0.43, 0.56),
        "thumb_tip": Landmark(0.48, 0.60),
        "index_pip": Landmark(0.44, 0.45),
        "index_tip": Landmark(0.49, 0.38),
    }
    right_hand = {
        "wrist": Landmark(0.70, 0.72),
        "thumb_ip": Landmark(0.57, 0.56),
        "thumb_tip": Landmark(0.52, 0.60),
        "index_pip": Landmark(0.56, 0.45),
        "index_tip": Landmark(0.51, 0.38),
    }

    result = evaluate_heart_gesture(left_hand, right_hand)

    assert result.detected is True
    assert result.score >= 0.64


def test_heart_gesture_rejects_distant_hands() -> None:
    left_hand = {
        "wrist": Landmark(0.18, 0.78),
        "thumb_ip": Landmark(0.24, 0.58),
        "thumb_tip": Landmark(0.28, 0.55),
        "index_pip": Landmark(0.23, 0.41),
        "index_tip": Landmark(0.26, 0.30),
    }
    right_hand = {
        "wrist": Landmark(0.82, 0.78),
        "thumb_ip": Landmark(0.76, 0.58),
        "thumb_tip": Landmark(0.72, 0.55),
        "index_pip": Landmark(0.77, 0.41),
        "index_tip": Landmark(0.74, 0.30),
    }

    result = evaluate_heart_gesture(left_hand, right_hand)

    assert result.detected is False
    assert result.score < 0.64
