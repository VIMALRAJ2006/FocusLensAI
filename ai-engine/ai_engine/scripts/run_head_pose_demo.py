#!/usr/bin/env python3
"""
Task 04 demo — face mesh + solvePnP head pose + separated rendering.

Usage (from repo root):
  .\\.venv\\Scripts\\python ai-engine\\ai_engine\\scripts\\run_head_pose_demo.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import cv2

_AI_ENGINE_ROOT = Path(__file__).resolve().parents[2]
if str(_AI_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_AI_ENGINE_ROOT))

from ai_engine.detectors.face_mesh_detector import FaceMeshDetector  # noqa: E402
from ai_engine.pose.head_pose_estimator import HeadPoseEstimator  # noqa: E402
from ai_engine.rendering.head_pose_renderer import HeadPoseRenderer  # noqa: E402


def main() -> int:
    face_mesh = FaceMeshDetector(running_mode="video")
    pose_estimator = HeadPoseEstimator()
    pose_renderer = HeadPoseRenderer()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: could not open webcam.", file=sys.stderr)
        return 1

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fps_smooth = 0.0
    print("Head pose demo running. Press Q to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Error: failed to read frame.", file=sys.stderr)
                break

            t0 = time.perf_counter()
            mesh = face_mesh.detect(frame)
            pose = pose_estimator.estimate(mesh)
            annotated = pose_renderer.draw(
                frame,
                pose,
                raw_landmarks=mesh.raw_landmarks,
            )
            elapsed = time.perf_counter() - t0
            fps = 1.0 / elapsed if elapsed > 0 else 0.0
            fps_smooth = fps_smooth * 0.9 + fps * 0.1

            if pose:
                header = f"{pose.direction.value.upper()} | {'FOCUSED' if pose.is_focused else 'DISTRACTED'}"
            elif mesh.face_present:
                header = "FACE | POSE UNAVAILABLE"
            else:
                header = "NO FACE"

            cv2.putText(
                annotated,
                f"{header} | {fps_smooth:.1f} FPS",
                (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("FocusLens — Head Pose (Task 04)", annotated)

            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                break
    finally:
        face_mesh.close()
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
