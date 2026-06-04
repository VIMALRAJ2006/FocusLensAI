"""Rendering-only drowsiness overlay (no detection logic)."""

from __future__ import annotations

import cv2
import numpy as np

from ai_engine.models.drowsiness_models import DrowsinessResult


class DrowsinessRenderer:
    """Draws drowsiness status and closure counters on a BGR frame."""

    def __init__(
        self,
        *,
        alert_color: tuple[int, int, int] = (0, 255, 120),
        drowsy_color: tuple[int, int, int] = (0, 80, 255),
        blink_color: tuple[int, int, int] = (200, 200, 0),
        y_offset: int = 100,
    ) -> None:
        self.alert_color = alert_color
        self.drowsy_color = drowsy_color
        self.blink_color = blink_color
        self.y_offset = y_offset

    def draw(
        self,
        frame: np.ndarray,
        state: DrowsinessResult | None,
    ) -> np.ndarray:
        output = frame.copy()
        if state is None:
            return output

        if state.is_drowsy:
            label = "DROWSY"
            color = self.drowsy_color
        elif state.is_blink and state.eyes_closed:
            label = "BLINK"
            color = self.blink_color
        elif state.eyes_closed:
            label = "EYES CLOSED"
            color = self.blink_color
        else:
            label = "ALERT"
            color = self.alert_color

        lines = [
            f"State: {label}",
            f"Closed frames: {state.consecutive_closed_frames}",
        ]
        if state.ear is not None:
            lines.append(f"EAR {state.ear:.3f}")

        y = self.y_offset
        for line in lines:
            cv2.putText(
                output,
                line,
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                2,
                cv2.LINE_AA,
            )
            y += 22

        if state.is_drowsy:
            cv2.rectangle(output, (0, 0), (output.shape[1] - 1, output.shape[0] - 1), color, 3)

        return output
