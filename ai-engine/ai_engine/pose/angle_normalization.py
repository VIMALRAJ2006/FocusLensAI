"""Normalize solvePnP Euler angles to stable, human-readable ranges."""

from __future__ import annotations


def wrap_angle_deg(angle: float) -> float:
    """Wrap any angle to (-180, 180] degrees."""
    return (angle + 180.0) % 360.0 - 180.0


def normalize_tilt_deg(angle: float) -> float:
    """
    Map supplementary tilt angles to [-90, 90].

    Prevents 180° wrapping artifacts (e.g. roll +174° → about -6° when upright).
    """
    angle = wrap_angle_deg(angle)
    if angle > 90.0:
        return angle - 180.0
    if angle < -90.0:
        return angle + 180.0
    return angle


def normalize_head_euler_deg(
    pitch: float,
    yaw: float,
    roll: float,
) -> tuple[float, float, float]:
    """
    Produce human-readable head angles for UI and focus checks.

    - Yaw: wrapped only (left/right turns stay in (-180, 180])
    - Pitch & roll: tilt-normalized so forward/upright ≈ 0°
    """
    yaw_n = wrap_angle_deg(yaw)
    pitch_n = normalize_tilt_deg(pitch)
    roll_n = normalize_tilt_deg(roll)
    return pitch_n, yaw_n, roll_n
