"""Rendering-only utilities for face mesh landmarks (no detection logic)."""

from __future__ import annotations

import cv2
import numpy as np

from ai_engine.models.landmark_models import FaceMeshResult, LandmarkPoint
from ai_engine.rendering.mesh_contours import FACE_OVAL, LEFT_EYE, RIGHT_EYE


class FaceMeshRenderer:
    """Draws face mesh landmarks onto an OpenCV BGR frame."""

    def __init__(
        self,
        *,
        point_radius: int = 1,
        point_color: tuple[int, int, int] = (0, 255, 0),
        contour_color: tuple[int, int, int] = (0, 200, 255),
        contour_thickness: int = 1,
    ) -> None:
        self.point_radius = point_radius
        self.point_color = point_color
        self.contour_color = contour_color
        self.contour_thickness = contour_thickness

    def draw(self, frame: np.ndarray, result: FaceMeshResult) -> np.ndarray:
        output = frame.copy()
        if not result.detected:
            return output

        index_map = {lm.index: lm for lm in result.landmarks}
        self._draw_contour(output, index_map, FACE_OVAL)
        self._draw_contour(output, index_map, LEFT_EYE, closed=True)
        self._draw_contour(output, index_map, RIGHT_EYE, closed=True)

        for lm in result.landmarks:
            cv2.circle(
                output,
                (lm.pixel_x, lm.pixel_y),
                self.point_radius,
                self.point_color,
                -1,
                lineType=cv2.LINE_AA,
            )
        return output

    def _draw_contour(
        self,
        frame: np.ndarray,
        index_map: dict[int, LandmarkPoint],
        indices: list[int],
        *,
        closed: bool = True,
    ) -> None:
        pts = [
            [index_map[idx].pixel_x, index_map[idx].pixel_y]
            for idx in indices
            if idx in index_map
        ]
        if len(pts) < 2:
            return
        cv2.polylines(
            frame,
            [np.array(pts, dtype=np.int32)],
            closed,
            self.contour_color,
            self.contour_thickness,
            lineType=cv2.LINE_AA,
        )
