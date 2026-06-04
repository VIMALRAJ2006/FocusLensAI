"""Eye tracking — consumes face mesh output, delegates metrics to eye_metrics."""

from __future__ import annotations

from typing import Any

from ai_engine.metrics.eye_metrics import (
    DEFAULT_EAR_THRESHOLD,
    DEFAULT_GAZE_OFFSET_THRESHOLD,
    compute_metrics_from_mesh,
    compute_metrics_from_raw,
)
from ai_engine.models.eye_models import EyeTrackingResult
from ai_engine.models.landmark_models import FaceMeshResult


class EyeTracker:
    """
    Tracks eye openness and gaze using existing face mesh landmarks.

    Does not run MediaPipe; pass output from FaceMeshDetector.
    """

    def __init__(
        self,
        *,
        ear_threshold: float = DEFAULT_EAR_THRESHOLD,
        gaze_offset_threshold: float = DEFAULT_GAZE_OFFSET_THRESHOLD,
    ) -> None:
        self.ear_threshold = ear_threshold
        self.gaze_offset_threshold = gaze_offset_threshold

    def track(self, mesh: FaceMeshResult) -> EyeTrackingResult | None:
        if not mesh.face_present or not mesh.landmarks:
            return None

        (
            left_ear,
            right_ear,
            ear,
            eyes_open,
            gaze_forward,
            gaze_offset,
            left_pts,
            right_pts,
        ) = compute_metrics_from_mesh(
            mesh,
            ear_threshold=self.ear_threshold,
            gaze_offset_threshold=self.gaze_offset_threshold,
        )

        return EyeTrackingResult(
            left_ear=left_ear,
            right_ear=right_ear,
            ear=ear,
            eyes_open=eyes_open,
            gaze_forward=gaze_forward,
            gaze_offset=gaze_offset,
            left_eye_points=left_pts,
            right_eye_points=right_pts,
        )

    def track_raw(
        self,
        landmarks: Any,
        frame_shape: tuple[int, ...],
    ) -> EyeTrackingResult | None:
        if landmarks is None:
            return None
        h, w = frame_shape[:2]
        (
            left_ear,
            right_ear,
            ear,
            eyes_open,
            gaze_forward,
            gaze_offset,
            left_pts,
            right_pts,
        ) = compute_metrics_from_raw(
            landmarks,
            w,
            h,
            ear_threshold=self.ear_threshold,
            gaze_offset_threshold=self.gaze_offset_threshold,
        )
        return EyeTrackingResult(
            left_ear=left_ear,
            right_ear=right_ear,
            ear=ear,
            eyes_open=eyes_open,
            gaze_forward=gaze_forward,
            gaze_offset=gaze_offset,
            left_eye_points=left_pts,
            right_eye_points=right_pts,
        )

    def analyze(self, landmarks: Any, frame_shape: tuple[int, ...]) -> dict | None:
        """Backward-compatible dict API for focuslens pipeline callers."""
        result = self.track_raw(landmarks, frame_shape)
        return result.to_dict() if result else None
