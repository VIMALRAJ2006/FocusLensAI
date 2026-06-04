"""Rendering-only eye tracking overlay (no metrics or detection logic)."""

from __future__ import annotations

import cv2
import numpy as np

from ai_engine.models.eye_models import EyePoint, EyeTrackingResult


class EyeRenderer:
    """Draws eye contours and EAR / openness labels on a BGR frame."""

    def __init__(
        self,
        *,
        contour_color: tuple[int, int, int] = (255, 180, 0),
        open_color: tuple[int, int, int] = (0, 255, 120),
        closed_color: tuple[int, int, int] = (0, 80, 255),
        contour_thickness: int = 1,
    ) -> None:
        self.contour_color = contour_color
        self.open_color = open_color
        self.closed_color = closed_color
        self.contour_thickness = contour_thickness

    def draw(self, frame: np.ndarray, eye: EyeTrackingResult | None) -> np.ndarray:
        output = frame.copy()
        if eye is None:
            return output

        self._draw_eye_polygon(output, eye.left_eye_points)
        self._draw_eye_polygon(output, eye.right_eye_points)

        state_color = self.open_color if eye.eyes_open else self.closed_color
        state_label = "OPEN" if eye.eyes_open else "CLOSED"
        lines = [
            f"L-EAR {eye.left_ear:.3f}  R-EAR {eye.right_ear:.3f}",
            f"EAR {eye.ear:.3f}  {state_label}",
        ]
        y = 56
        for line in lines:
            cv2.putText(
                output,
                line,
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                state_color,
                2,
                cv2.LINE_AA,
            )
            y += 22

        return output

    def _draw_eye_polygon(
        self,
        frame: np.ndarray,
        points: tuple[EyePoint, ...],
    ) -> None:
        if len(points) < 2:
            return
        pts = np.array([p.as_tuple() for p in points], dtype=np.int32)
        closed = len(points) >= 6
        cv2.polylines(
            frame,
            [pts],
            closed,
            self.contour_color,
            self.contour_thickness,
            lineType=cv2.LINE_AA,
        )
