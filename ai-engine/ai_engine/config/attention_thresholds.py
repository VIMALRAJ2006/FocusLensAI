"""Configurable thresholds for Task 05 attention scoring."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AttentionThresholds:
    """Weights and temporal thresholds used by the attention scorer."""

    face_weight: float = 0.15
    eyes_weight: float = 0.25
    gaze_weight: float = 0.25
    posture_weight: float = 0.15
    alertness_weight: float = 0.20

    # Score classification.
    focused_min_score: float = 70.0
    inactive_score: float = 0.0
    drowsy_score_cap: float = 35.0

    # Repeated away-gaze detection.
    distraction_window_frames: int = 20
    distraction_min_frames: int = 10
    distraction_ratio_threshold: float = 0.45
    distraction_score_penalty: float = 0.85

    # Exponential moving average alpha. Higher values respond faster.
    score_smoothing_alpha: float = 0.35

    @property
    def weights(self) -> dict[str, float]:
        return {
            "face": self.face_weight,
            "eyes": self.eyes_weight,
            "gaze": self.gaze_weight,
            "posture": self.posture_weight,
            "alertness": self.alertness_weight,
        }
