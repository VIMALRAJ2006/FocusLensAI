from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AttentionState(str, Enum):
    """High-level attention classification for a processed frame."""

    FOCUSED = "focused"
    DISTRACTED = "distracted"
    DROWSY = "drowsy"
    INACTIVE = "inactive"


@dataclass
class FrameMetrics:
    """Per-frame analysis output consumed by the backend and dashboard."""

    face_present: bool = False
    eyes_open: bool = True
    gaze_forward: bool = True
    head_upright: bool = True
    head_direction: str = "unknown"
    drowsy: bool = False
    distracted: bool = False
    attention_state: AttentionState = AttentionState.INACTIVE
    raw_attention_score: float = 0.0
    attention_score: float = 0.0
    components: dict[str, float] = field(default_factory=dict)
    landmarks_detected: bool = False

    def to_dict(self) -> dict[str, Any]:
        state = (
            self.attention_state.value
            if isinstance(self.attention_state, AttentionState)
            else str(self.attention_state)
        )
        return {
            "face_present": self.face_present,
            "eyes_open": self.eyes_open,
            "gaze_forward": self.gaze_forward,
            "head_upright": self.head_upright,
            "head_direction": self.head_direction,
            "drowsy": self.drowsy,
            "distracted": self.distracted,
            "attention_state": state,
            "raw_attention_score": round(self.raw_attention_score, 2),
            "attention_score": round(self.attention_score, 2),
            "components": {k: round(v, 3) for k, v in self.components.items()},
            "landmarks_detected": self.landmarks_detected,
        }
