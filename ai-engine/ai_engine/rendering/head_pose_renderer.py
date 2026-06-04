"""Rendering-only head pose overlay (no pose estimation logic)."""

from __future__ import annotations

import cv2
import numpy as np

from ai_engine.models.pose_models import HeadPoseResult
from ai_engine.pose.pose_math import LANDMARK_NOSE_TIP


class HeadPoseRenderer:
    """Draws pose angles, direction label, and optional 3D axes on the nose."""

    def __init__(
        self,
        *,
        focused_color: tuple[int, int, int] = (0, 255, 120),
        distracted_color: tuple[int, int, int] = (0, 140, 255),
        axis_length: int = 60,
        y_offset: int = 148,
    ) -> None:
        self.focused_color = focused_color
        self.distracted_color = distracted_color
        self.axis_length = axis_length
        self.y_offset = y_offset

    def draw(
        self,
        frame: np.ndarray,
        pose: HeadPoseResult | None,
        *,
        raw_landmarks: Any | None = None,
    ) -> np.ndarray:
        output = frame.copy()
        if pose is None:
            return output

        color = self.focused_color if pose.is_focused else self.distracted_color
        focus_label = "FOCUSED" if pose.is_focused else "DISTRACTED"

        lines = [
            f"Pose: {pose.direction.value.upper()} | {focus_label}",
            f"Pitch {pose.pitch_deg:+.1f}  Yaw {pose.yaw_deg:+.1f}  Roll {pose.roll_deg:+.1f}",
        ]
        y = self.y_offset
        for line in lines:
            cv2.putText(
                output,
                line,
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                color,
                2,
                cv2.LINE_AA,
            )
            y += 22

        if raw_landmarks is not None:
            self._draw_axes(output, pose, raw_landmarks)

        return output

    def _draw_axes(
        self,
        frame: np.ndarray,
        pose: HeadPoseResult,
        raw_landmarks: Any,
    ) -> None:
        h, w = frame.shape[:2]
        nose = raw_landmarks[LANDMARK_NOSE_TIP]
        nose_2d = np.array([[nose.x * w, nose.y * h]], dtype=np.float64)

        # Simple axis hint from yaw/pitch (visual only; not re-solving PnP)
        length = self.axis_length
        yaw_rad = np.radians(pose.yaw_deg)
        pitch_rad = np.radians(pose.pitch_deg)
        origin = (int(nose_2d[0, 0]), int(nose_2d[0, 1]))

        x_end = (
            int(origin[0] + length * np.cos(yaw_rad)),
            int(origin[1] + length * np.sin(pitch_rad) * 0.5),
        )
        y_end = (origin[0], origin[1] - length)
        z_end = (
            int(origin[0] - length * np.sin(yaw_rad)),
            int(origin[1] + length * np.cos(pitch_rad) * 0.5),
        )

        cv2.line(frame, origin, x_end, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.line(frame, origin, y_end, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.line(frame, origin, z_end, (255, 0, 0), 2, cv2.LINE_AA)
