#!/usr/bin/env python3
"""
Task 02 demo — face mesh + eye tracking (EAR) with separated rendering.

Usage (from repo root):
  .\\.venv\\Scripts\\python ai-engine\\ai_engine\\scripts\\run_eye_tracking_demo.py
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
from ai_engine.rendering.eye_renderer import EyeRenderer  # noqa: E402
from ai_engine.tracking.eye_tracker import EyeTracker  # noqa: E402


def main() -> int:
    face_mesh = FaceMeshDetector(running_mode="video")
    eye_tracker = EyeTracker()
    eye_renderer = EyeRenderer()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: could not open webcam.", file=sys.stderr)
        return 1

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fps_smooth = 0.0
    print("Eye tracking demo running. Press Q to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Error: failed to read frame.", file=sys.stderr)
                break

            t0 = time.perf_counter()
            mesh = face_mesh.detect(frame)
            eye = eye_tracker.track(mesh)
            annotated = eye_renderer.draw(frame, eye)
            elapsed = time.perf_counter() - t0
            fps = 1.0 / elapsed if elapsed > 0 else 0.0
            fps_smooth = fps_smooth * 0.9 + fps * 0.1

            if mesh.face_present and eye:
                header = f"FACE | EAR {eye.ear:.3f} | {'OPEN' if eye.eyes_open else 'CLOSED'}"
            elif mesh.face_present:
                header = "FACE | EYES NOT TRACKED"
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
            cv2.imshow("FocusLens — Eye Tracking (Task 02)", annotated)

            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                break
    finally:
        face_mesh.close()
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
