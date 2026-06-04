"""Reusable solvePnP helpers for head pose (no rendering)."""

from __future__ import annotations

import cv2
import numpy as np

from ai_engine.pose.angle_normalization import normalize_head_euler_deg

# MediaPipe landmark indices for 6-point face model
LANDMARK_NOSE_TIP = 1
LANDMARK_CHIN = 152
LANDMARK_LEFT_EYE = 33
LANDMARK_RIGHT_EYE = 263
LANDMARK_LEFT_MOUTH = 61
LANDMARK_RIGHT_MOUTH = 291

POSE_LANDMARK_INDICES = (
    LANDMARK_NOSE_TIP,
    LANDMARK_CHIN,
    LANDMARK_LEFT_EYE,
    LANDMARK_RIGHT_EYE,
    LANDMARK_LEFT_MOUTH,
    LANDMARK_RIGHT_MOUTH,
)

# Generic 3D face model (millimetres) aligned with landmark order above
MODEL_POINTS_3D = np.array(
    [
        (0.0, 0.0, 0.0),
        (0.0, -330.0, -65.0),
        (-225.0, 170.0, -135.0),
        (225.0, 170.0, -135.0),
        (-150.0, -150.0, -125.0),
        (150.0, -150.0, -125.0),
    ],
    dtype=np.float64,
)


def build_camera_matrix(frame_width: int, frame_height: int) -> np.ndarray:
    focal = float(frame_width)
    center = (frame_width / 2.0, frame_height / 2.0)
    return np.array(
        [
            [focal, 0.0, center[0]],
            [0.0, focal, center[1]],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )


def image_points_from_landmarks(
    landmarks: Any,
    frame_width: int,
    frame_height: int,
    indices: tuple[int, ...] = POSE_LANDMARK_INDICES,
) -> np.ndarray:
    points = []
    for idx in indices:
        lm = landmarks[idx]
        points.append([lm.x * frame_width, lm.y * frame_height])
    return np.array(points, dtype=np.float64)


def solve_head_pose(
    image_points: np.ndarray,
    frame_width: int,
    frame_height: int,
) -> tuple[float, float, float] | None:
    """
    Estimate pitch, yaw, roll (degrees) via cv2.solvePnP.

    Returns None if pose solving fails.
    """
    if image_points.shape[0] < 6:
        return None

    camera_matrix = build_camera_matrix(frame_width, frame_height)
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    ok, rotation_vector, _translation = cv2.solvePnP(
        MODEL_POINTS_3D,
        image_points.reshape(-1, 1, 2),
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not ok:
        return None

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    return normalize_head_euler_deg(*rotation_matrix_to_euler_deg(rotation_matrix))


def rotation_matrix_to_euler_deg(rotation_matrix: np.ndarray) -> tuple[float, float, float]:
    """Extract pitch, yaw, roll in degrees (Y-X-Z convention)."""
    r = rotation_matrix
    sy = np.sqrt(r[0, 0] ** 2 + r[1, 0] ** 2)
    singular = sy < 1e-6

    if not singular:
        pitch = np.arctan2(-r[2, 0], sy)
        yaw = np.arctan2(r[1, 0], r[0, 0])
        roll = np.arctan2(r[2, 1], r[2, 2])
    else:
        pitch = np.arctan2(-r[2, 0], sy)
        yaw = np.arctan2(-r[0, 1], r[1, 1])
        roll = 0.0

    return (
        float(np.degrees(pitch)),
        float(np.degrees(yaw)),
        float(np.degrees(roll)),
    )
