"""Head pose estimation from face mesh landmarks using OpenCV solvePnP."""

from __future__ import annotations

from typing import Any

from ai_engine.config.pose_thresholds import PoseThresholds
from ai_engine.models.landmark_models import FaceMeshResult
from ai_engine.models.pose_models import HeadDirection, HeadPoseResult
from ai_engine.pose.pose_math import (
    POSE_LANDMARK_INDICES,
    image_points_from_landmarks,
    solve_head_pose,
)


class HeadPoseEstimator:
    """
    Estimates head rotation and look direction from existing face mesh landmarks.

    Does not run MediaPipe; consumes FaceMeshResult or raw landmarks.
    """

    def __init__(self, thresholds: PoseThresholds | None = None) -> None:
        self.config = thresholds or PoseThresholds()

    def estimate(self, mesh: FaceMeshResult) -> HeadPoseResult | None:
        if not mesh.face_present or mesh.raw_landmarks is None:
            return None
        h, w = mesh.frame_height, mesh.frame_width
        return self._estimate_from_raw(mesh.raw_landmarks, w, h)

    def analyze(self, landmarks: Any, frame_shape: tuple[int, ...]) -> dict | None:
        """Backward-compatible dict API for pipeline migration."""
        if landmarks is None:
            return None
        h, w = frame_shape[:2]
        result = self._estimate_from_raw(landmarks, w, h)
        return result.to_dict() if result else None

    def _estimate_from_raw(
        self,
        landmarks: Any,
        frame_width: int,
        frame_height: int,
    ) -> HeadPoseResult | None:
        if len(landmarks) <= max(POSE_LANDMARK_INDICES):
            return None

        image_points = image_points_from_landmarks(
            landmarks, frame_width, frame_height
        )
        angles = solve_head_pose(image_points, frame_width, frame_height)
        if angles is None:
            return None

        pitch_deg, yaw_deg, roll_deg = angles
        direction = self._classify_direction(pitch_deg, yaw_deg)
        is_focused = self._is_focused(pitch_deg, yaw_deg, roll_deg)

        return HeadPoseResult(
            pitch_deg=pitch_deg,
            yaw_deg=yaw_deg,
            roll_deg=roll_deg,
            direction=direction,
            is_focused=is_focused,
            head_upright=is_focused,
        )

    def _is_focused(self, pitch: float, yaw: float, roll: float) -> bool:
        # Angles are already normalized in solve_head_pose; compare magnitudes directly.
        return (
            abs(yaw) <= self.config.max_yaw_focus_deg
            and abs(pitch) <= self.config.max_pitch_focus_deg
            and abs(roll) <= self.config.max_roll_focus_deg
        )

    def _classify_direction(self, pitch: float, yaw: float) -> HeadDirection:
        cfg = self.config
        if (
            abs(yaw) < cfg.yaw_direction_deg
            and abs(pitch) < cfg.pitch_direction_deg
        ):
            return HeadDirection.CENTER

        if abs(yaw) >= abs(pitch):
            if yaw > cfg.yaw_direction_deg:
                return HeadDirection.RIGHT
            if yaw < -cfg.yaw_direction_deg:
                return HeadDirection.LEFT

        if pitch > cfg.pitch_direction_deg:
            return HeadDirection.DOWN
        if pitch < -cfg.pitch_direction_deg:
            return HeadDirection.UP

        return HeadDirection.CENTER
