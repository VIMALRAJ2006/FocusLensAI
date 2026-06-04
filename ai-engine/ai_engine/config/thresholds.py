"""Configurable thresholds for AI engine modules."""

from dataclasses import dataclass

from ai_engine.metrics.eye_metrics import (
    DEFAULT_EAR_THRESHOLD,
    DEFAULT_GAZE_OFFSET_THRESHOLD,
)


@dataclass(frozen=True)
class EyeThresholds:
    """Eye openness and gaze thresholds (Task 02)."""

    ear_open_threshold: float = DEFAULT_EAR_THRESHOLD
    gaze_offset_threshold: float = DEFAULT_GAZE_OFFSET_THRESHOLD


@dataclass(frozen=True)
class DrowsinessThresholds:
    """
  Thresholds for drowsiness vs blinking (Task 03).

  Blinks: short closures (<= blink_max_closed_frames).
  Drowsiness: sustained closure (>= drowsiness_min_consecutive_frames).
  """

    # EAR below this counts as physically closed (stricter than open threshold)
    ear_closed_threshold: float = 0.18
    # Closures this short or shorter are treated as blinks when eyes reopen
    blink_max_closed_frames: int = 5
    # Consecutive closed frames required to enter drowsy state
    drowsiness_min_consecutive_frames: int = 12
    # Frames required before detection activates (avoids cold-start noise)
    warmup_frames: int = 3
