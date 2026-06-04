#!/usr/bin/env python3
"""
Task 01 demo — OpenCV webcam + face mesh detection + separated rendering.

Usage (from repo root):
  .\\.venv\\Scripts\\python ai-engine\\ai_engine\\scripts\\run_face_mesh_webcam.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import cv2

# ai-engine/ on sys.path so `ai_engine` package resolves
_AI_ENGINE_ROOT = Path(__file__).resolve().parents[2]
if str(_AI_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_AI_ENGINE_ROOT))

from ai_engine.detectors.face_mesh_detector import FaceMeshDetector  # noqa: E402
from ai_engine.rendering.face_mesh_renderer import FaceMeshRenderer  # noqa: E402


def main() -> int:
    detector = FaceMeshDetector(running_mode="video")
    renderer = FaceMeshRenderer()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: could not open webcam.", file=sys.stderr)
        return 1

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fps_smooth = 0.0
    print("Face mesh demo running. Press Q to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Error: failed to read frame.", file=sys.stderr)
                break

            t0 = time.perf_counter()
            result = detector.detect(frame)
            annotated = renderer.draw(frame, result)
            elapsed = time.perf_counter() - t0
            fps = 1.0 / elapsed if elapsed > 0 else 0.0
            fps_smooth = fps_smooth * 0.9 + fps * 0.1

            status = "FACE" if result.face_present else "NO FACE"
            cv2.putText(
                annotated,
                f"{status} | {fps_smooth:.1f} FPS | {len(result.landmarks)} pts",
                (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("FocusLens — Face Mesh (Task 01)", annotated)

            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                break
    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
