"""Face mesh detection — MediaPipe Face Landmarker on OpenCV frames."""

from __future__ import annotations

import time

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from ai_engine.models.landmark_models import (
    FaceMeshResult,
    RunningMode,
    empty_result,
    landmarks_from_raw,
)
from ai_engine.models.model_assets import ensure_face_landmarker_model


class FaceMeshDetector:
    """
    Real-time face mesh detection via MediaPipe Face Landmarker.

    Use running_mode='video' for OpenCV webcam streams; 'image' for single frames.
    """

    def __init__(
        self,
        *,
        running_mode: RunningMode = "image",
        max_faces: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        max_frame_width: int = 640,
    ) -> None:
        self.max_frame_width = max_frame_width
        self._video_mode = running_mode == "video"
        mp_mode = (
            vision.RunningMode.VIDEO
            if self._video_mode
            else vision.RunningMode.IMAGE
        )
        options = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=ensure_face_landmarker_model()
            ),
            running_mode=mp_mode,
            num_faces=max_faces,
            min_face_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)

    def detect(
        self,
        frame: np.ndarray,
        *,
        input_is_rgb: bool = False,
    ) -> FaceMeshResult:
        """Run face mesh on a BGR or RGB OpenCV frame."""
        original_h, original_w = frame.shape[:2]
        bgr = frame if not input_is_rgb else cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        bgr, scale = self._maybe_resize(bgr)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        if self._video_mode:
            timestamp_ms = int(time.time() * 1000)
            result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        else:
            result = self._landmarker.detect(mp_image)

        if not result.face_landmarks:
            return empty_result(original_w, original_h)

        raw = result.face_landmarks[0]
        return FaceMeshResult(
            detected=True,
            landmarks=landmarks_from_raw(raw, w, h, scale),
            frame_width=original_w,
            frame_height=original_h,
            face_count=len(result.face_landmarks),
            raw_landmarks=raw,
        )

    def _maybe_resize(self, bgr: np.ndarray) -> tuple[np.ndarray, float]:
        h, w = bgr.shape[:2]
        if w <= self.max_frame_width:
            return bgr, 1.0
        scale = self.max_frame_width / w
        resized = cv2.resize(
            bgr,
            (self.max_frame_width, int(h * scale)),
            interpolation=cv2.INTER_LINEAR,
        )
        return resized, scale

    def close(self) -> None:
        self._landmarker.close()
