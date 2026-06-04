"""Drowsiness detection — prolonged eye closure vs blinks, using EAR from eye tracking."""

from __future__ import annotations

from ai_engine.config.thresholds import DrowsinessThresholds
from ai_engine.models.drowsiness_models import DrowsinessResult
from ai_engine.models.eye_models import EyeTrackingResult


class DrowsinessDetector:
    """
    Detects drowsiness from sustained eye closure.

    Reuses EAR / eyes_open from the eye tracking pipeline. Short closures are
    classified as blinks; only consecutive closed frames beyond the blink window
    trigger drowsiness. State resets when eyes reopen.
    """

    def __init__(self, thresholds: DrowsinessThresholds | None = None) -> None:
        self.config = thresholds or DrowsinessThresholds()
        self._consecutive_closed = 0
        self._frame_count = 0
        self._is_drowsy = False

    def update_from_eye(self, eye: EyeTrackingResult | None) -> DrowsinessResult:
        if eye is None:
            return self._inactive_result()
        closed = not eye.eyes_open or eye.ear < self.config.ear_closed_threshold
        return self._step(ear=eye.ear, eyes_closed=closed)

    def update(self, ear: float | None) -> bool:
        """Backward-compatible API: returns drowsy boolean from EAR only."""
        if ear is None:
            return False
        closed = ear < self.config.ear_closed_threshold
        return self._step(ear=ear, eyes_closed=closed).is_drowsy

    def _step(self, *, ear: float, eyes_closed: bool) -> DrowsinessResult:
        self._frame_count += 1

        if eyes_closed:
            self._consecutive_closed += 1
            warmed_up = self._frame_count >= self.config.warmup_frames
            if (
                warmed_up
                and self._consecutive_closed >= self.config.drowsiness_min_consecutive_frames
            ):
                self._is_drowsy = True
        else:
            self._consecutive_closed = 0
            self._is_drowsy = False

        is_blink = (
            eyes_closed
            and self._consecutive_closed <= self.config.blink_max_closed_frames
        )

        return DrowsinessResult(
            is_drowsy=self._is_drowsy,
            eyes_closed=eyes_closed,
            is_blink=is_blink,
            consecutive_closed_frames=self._consecutive_closed,
            ear=ear,
        )

    def _inactive_result(self) -> DrowsinessResult:
        return DrowsinessResult(
            is_drowsy=False,
            eyes_closed=False,
            is_blink=False,
            consecutive_closed_frames=0,
            ear=None,
        )

    def reset(self) -> None:
        self._consecutive_closed = 0
        self._frame_count = 0
        self._is_drowsy = False
