#!/usr/bin/env python3
"""
Task 05 demo - complete AttentionPipeline attention scoring.

Usage (from repo root):
  .\\.venv\\Scripts\\python ai-engine\\ai_engine\\scripts\\run_attention_demo.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import cv2
import numpy as np

_AI_ENGINE_ROOT = Path(__file__).resolve().parents[2]
if str(_AI_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_AI_ENGINE_ROOT))

from ai_engine.rendering.drowsiness_renderer import DrowsinessRenderer  # noqa: E402
from ai_engine.rendering.eye_renderer import EyeRenderer  # noqa: E402
from ai_engine.rendering.face_mesh_renderer import FaceMeshRenderer  # noqa: E402
from ai_engine.rendering.head_pose_renderer import HeadPoseRenderer  # noqa: E402
from focuslens.pipeline import AttentionPipeline, AttentionPipelineResult  # noqa: E402
from focuslens.types import AttentionState  # noqa: E402


def _attention_color(state: AttentionState | str) -> tuple[int, int, int]:
    value = state.value if isinstance(state, AttentionState) else str(state)
    if value == AttentionState.FOCUSED.value:
        return (0, 255, 120)
    if value == AttentionState.DROWSY.value:
        return (0, 80, 255)
    if value == AttentionState.DISTRACTED.value:
        return (0, 180, 255)
    return (190, 190, 190)


def _drowsiness_label(result: AttentionPipelineResult) -> str:
    state = result.drowsiness
    if not result.metrics.face_present:
        return "INACTIVE"
    if state is None:
        return "UNKNOWN"
    if state.is_drowsy:
        return "DROWSY"
    if state.is_blink and state.eyes_closed:
        return "BLINK"
    if state.eyes_closed:
        return "EYES CLOSED"
    return "ALERT"


def _draw_attention_status(
    frame: np.ndarray,
    result: AttentionPipelineResult,
    fps: float,
) -> np.ndarray:
    output = frame.copy()
    metrics = result.metrics
    state = metrics.attention_state
    state_text = state.value.upper() if isinstance(state, AttentionState) else str(state).upper()
    color = _attention_color(state)
    head_direction = metrics.head_direction.upper()
    drowsiness = _drowsiness_label(result)

    lines = [
        f"Attention {metrics.attention_score:5.1f} / 100",
        f"Focus state: {state_text}",
        f"Drowsiness: {drowsiness}",
        f"Head direction: {head_direction} | FPS {fps:.1f}",
    ]

    x = 10
    line_height = 24
    panel_height = 22 + line_height * len(lines)
    y0 = max(10, output.shape[0] - panel_height - 10)
    y1 = output.shape[0] - 10

    cv2.rectangle(output, (0, y0 - 8), (430, y1), (15, 23, 42), -1)
    cv2.rectangle(output, (0, y0 - 8), (430, y1), color, 2)

    y = y0 + 14
    for index, line in enumerate(lines):
        line_color = color if index == 0 else (235, 235, 235)
        cv2.putText(
            output,
            line,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            line_color,
            2,
            cv2.LINE_AA,
        )
        y += line_height

    return output


def main() -> int:
    pipeline = AttentionPipeline(running_mode="video")
    face_renderer = FaceMeshRenderer()
    eye_renderer = EyeRenderer()
    drowsy_renderer = DrowsinessRenderer()
    pose_renderer = HeadPoseRenderer()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        pipeline.close()
        print("Error: could not open webcam.", file=sys.stderr)
        return 1

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fps_smooth = 0.0
    print("Attention scoring demo running. Press Q to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Error: failed to read frame.", file=sys.stderr)
                break

            t0 = time.perf_counter()
            result = pipeline.process_frame_details(frame)
            annotated = face_renderer.draw(frame, result.mesh)
            annotated = eye_renderer.draw(annotated, result.eye)
            annotated = drowsy_renderer.draw(annotated, result.drowsiness)
            annotated = pose_renderer.draw(
                annotated,
                result.pose,
                raw_landmarks=result.mesh.raw_landmarks,
            )
            elapsed = time.perf_counter() - t0
            fps = 1.0 / elapsed if elapsed > 0 else 0.0
            fps_smooth = fps if fps_smooth <= 0 else fps_smooth * 0.9 + fps * 0.1

            annotated = _draw_attention_status(annotated, result, fps_smooth)
            cv2.imshow("FocusLens - Attention (Task 05)", annotated)

            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                break
    finally:
        pipeline.close()
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
