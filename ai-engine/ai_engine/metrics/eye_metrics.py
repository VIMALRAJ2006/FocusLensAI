"""
Reusable eye metrics utilities — EAR calculation and gaze helpers.

No rendering or MediaPipe session logic belongs here.
"""

from __future__ import annotations

import numpy as np

from ai_engine.models.eye_models import EyePoint
from ai_engine.models.landmark_models import FaceMeshResult, LandmarkPoint

# Six-point EAR contours (MediaPipe face mesh indices)
EAR_LEFT_EYE = [33, 160, 158, 133, 153, 144]
EAR_RIGHT_EYE = [362, 385, 387, 263, 373, 380]
LEFT_IRIS_INDEX = 468
RIGHT_IRIS_INDEX = 473

DEFAULT_EAR_THRESHOLD = 0.21
DEFAULT_GAZE_OFFSET_THRESHOLD = 0.035


def compute_ear(eye_points: np.ndarray) -> float:
    """
    Eye Aspect Ratio from six ordered pixel points (6, 2).

    EAR = (||p1-p5|| + ||p2-p4||) / (2 * ||p0-p3||)
    """
    if eye_points.shape[0] < 6:
        return 0.0
    vertical = np.linalg.norm(eye_points[1] - eye_points[5]) + np.linalg.norm(
        eye_points[2] - eye_points[4]
    )
    horizontal = np.linalg.norm(eye_points[0] - eye_points[3])
    if horizontal < 1e-6:
        return 0.0
    return float(vertical / (2.0 * horizontal))


def compute_ear_from_landmarks(
    landmarks: Any,
    indices: list[int],
    frame_width: int,
    frame_height: int,
) -> float:
    """EAR from MediaPipe normalized raw landmarks."""
    pts = np.array(
        [(landmarks[i].x * frame_width, landmarks[i].y * frame_height) for i in indices],
        dtype=np.float64,
    )
    return compute_ear(pts)


def average_ear(left_ear: float, right_ear: float) -> float:
    return (left_ear + right_ear) / 2.0


def eyes_open(ear: float, threshold: float = DEFAULT_EAR_THRESHOLD) -> bool:
    return ear >= threshold


def extract_eye_points_from_mesh(
    landmarks: list[LandmarkPoint],
    indices: list[int],
) -> tuple[EyePoint, ...]:
    index_map = {lm.index: lm for lm in landmarks}
    return tuple(
        EyePoint(index_map[i].pixel_x, index_map[i].pixel_y)
        for i in indices
        if i in index_map
    )


def extract_eye_points_from_landmarks(
    landmarks: Any,
    indices: list[int],
    frame_width: int,
    frame_height: int,
) -> tuple[EyePoint, ...]:
    return tuple(
        EyePoint(int(landmarks[i].x * frame_width), int(landmarks[i].y * frame_height))
        for i in indices
        if i < len(landmarks)
    )


def _eye_points_to_array(points: tuple[EyePoint, ...]) -> np.ndarray:
    return np.array([p.as_tuple() for p in points], dtype=np.float64)


def estimate_gaze(
    landmarks: Any,
    *,
    gaze_offset_threshold: float = DEFAULT_GAZE_OFFSET_THRESHOLD,
) -> tuple[bool, float]:
    """
    Approximate forward gaze via horizontal iris offset (extensible for Task 03+).

    Returns (gaze_forward, average_offset).
    """
    if landmarks is None or len(landmarks) <= RIGHT_IRIS_INDEX:
        return True, 0.0

    def iris_offset(eye_indices: list[int], iris_idx: int) -> float:
        eye_x = np.mean([landmarks[i].x for i in eye_indices])
        return landmarks[iris_idx].x - eye_x

    left_off = iris_offset(EAR_LEFT_EYE, LEFT_IRIS_INDEX)
    right_off = iris_offset(EAR_RIGHT_EYE, RIGHT_IRIS_INDEX)
    avg_off = (left_off + right_off) / 2.0
    return abs(avg_off) < gaze_offset_threshold, float(avg_off)


def compute_metrics_from_mesh(
    mesh: FaceMeshResult,
    *,
    ear_threshold: float = DEFAULT_EAR_THRESHOLD,
    gaze_offset_threshold: float = DEFAULT_GAZE_OFFSET_THRESHOLD,
) -> tuple[float, float, float, bool, bool, float, tuple[EyePoint, ...], tuple[EyePoint, ...]]:
    """Returns left_ear, right_ear, avg_ear, eyes_open, gaze_forward, gaze_offset, left_pts, right_pts."""
    left_pts = extract_eye_points_from_mesh(mesh.landmarks, EAR_LEFT_EYE)
    right_pts = extract_eye_points_from_mesh(mesh.landmarks, EAR_RIGHT_EYE)

    left_ear = compute_ear(_eye_points_to_array(left_pts)) if len(left_pts) >= 6 else 0.0
    right_ear = compute_ear(_eye_points_to_array(right_pts)) if len(right_pts) >= 6 else 0.0
    ear = average_ear(left_ear, right_ear)
    open_state = eyes_open(ear, ear_threshold)

    gaze_forward, gaze_offset = estimate_gaze(
        mesh.raw_landmarks,
        gaze_offset_threshold=gaze_offset_threshold,
    )

    return left_ear, right_ear, ear, open_state, gaze_forward, gaze_offset, left_pts, right_pts


def compute_metrics_from_raw(
    landmarks: Any,
    frame_width: int,
    frame_height: int,
    *,
    ear_threshold: float = DEFAULT_EAR_THRESHOLD,
    gaze_offset_threshold: float = DEFAULT_GAZE_OFFSET_THRESHOLD,
) -> tuple[float, float, float, bool, bool, float, tuple[EyePoint, ...], tuple[EyePoint, ...]]:
    left_pts = extract_eye_points_from_landmarks(
        landmarks, EAR_LEFT_EYE, frame_width, frame_height
    )
    right_pts = extract_eye_points_from_landmarks(
        landmarks, EAR_RIGHT_EYE, frame_width, frame_height
    )

    left_ear = compute_ear_from_landmarks(landmarks, EAR_LEFT_EYE, frame_width, frame_height)
    right_ear = compute_ear_from_landmarks(landmarks, EAR_RIGHT_EYE, frame_width, frame_height)
    ear = average_ear(left_ear, right_ear)
    open_state = eyes_open(ear, ear_threshold)
    gaze_forward, gaze_offset = estimate_gaze(
        landmarks,
        gaze_offset_threshold=gaze_offset_threshold,
    )

    return left_ear, right_ear, ear, open_state, gaze_forward, gaze_offset, left_pts, right_pts
