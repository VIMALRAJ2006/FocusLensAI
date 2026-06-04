from dataclasses import dataclass

import cv2
import numpy as np

from ai_engine.detection.drowsiness_detector import DrowsinessDetector
from ai_engine.detectors.face_mesh_detector import FaceMeshDetector
from ai_engine.models.drowsiness_models import DrowsinessResult
from ai_engine.models.eye_models import EyeTrackingResult
from ai_engine.models.landmark_models import FaceMeshResult, RunningMode
from ai_engine.models.pose_models import HeadPoseResult
from ai_engine.pose.head_pose_estimator import HeadPoseEstimator
from ai_engine.tracking.eye_tracker import EyeTracker

from focuslens.scoring import AttentionScorer
from focuslens.types import FrameMetrics


@dataclass
class AttentionPipelineResult:
    """Full per-frame pipeline output for local demos and diagnostics."""

    mesh: FaceMeshResult
    eye: EyeTrackingResult | None
    drowsiness: DrowsinessResult | None
    pose: HeadPoseResult | None
    metrics: FrameMetrics


class AttentionPipeline:
    """
    Orchestrates CV analysis: OpenCV frame decode → MediaPipe landmarks
    → detection modules → attention scoring.
    """

    def __init__(self, *, running_mode: RunningMode = "image") -> None:
        self.face_mesh = FaceMeshDetector(running_mode=running_mode)
        self.eye_tracker = EyeTracker()
        self.drowsiness_detector = DrowsinessDetector()
        self.head_pose_estimator = HeadPoseEstimator()
        self.scorer = AttentionScorer()

    def process_frame(self, bgr_frame: np.ndarray) -> FrameMetrics:
        return self.process_frame_details(bgr_frame).metrics

    def process_frame_details(self, bgr_frame: np.ndarray) -> AttentionPipelineResult:
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mesh = self.face_mesh.detect(rgb, input_is_rgb=True)
        face_present = mesh.face_present

        eye = self.eye_tracker.track(mesh) if face_present else None
        drowsiness = (
            self.drowsiness_detector.update_from_eye(eye) if face_present else None
        )
        drowsy = drowsiness.is_drowsy if drowsiness else False
        pose = self.head_pose_estimator.estimate(mesh) if face_present else None

        metrics = self.scorer.score(
            face_present=face_present,
            eyes_open=eye.eyes_open if eye else False,
            gaze_forward=eye.gaze_forward if eye else False,
            head_upright=pose.head_upright if pose else False,
            drowsy=drowsy,
        )
        metrics.head_direction = pose.direction.value if pose else "unknown"

        return AttentionPipelineResult(
            mesh=mesh,
            eye=eye,
            drowsiness=drowsiness,
            pose=pose,
            metrics=metrics,
        )

    def process_jpeg_bytes(self, jpeg_bytes: bytes) -> FrameMetrics:
        arr = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            return FrameMetrics()
        return self.process_frame(frame)

    def reset(self) -> None:
        self.drowsiness_detector.reset()
        self.scorer.reset()

    def close(self) -> None:
        self.face_mesh.close()
