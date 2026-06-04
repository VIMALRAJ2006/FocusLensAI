"""Configurable thresholds for head pose estimation (Task 04)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PoseThresholds:
    """Angles (degrees) for focused posture and directional look detection."""

    # Within these bounds → focused / head_upright
    max_yaw_focus_deg: float = 15.0
    max_pitch_focus_deg: float = 15.0
    max_roll_focus_deg: float = 20.0

    # Minimum |angle| to classify a directional look (left/right/up/down)
    yaw_direction_deg: float = 12.0
    pitch_direction_deg: float = 12.0
