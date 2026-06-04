from typing import Any

from pydantic import BaseModel, Field


class SessionSummary(BaseModel):
    """Serializable session aggregate returned by REST and WebSocket payloads."""

    id: str
    frame_count: int = 0
    duration_sec: float = 0.0
    avg_attention: float = 0.0
    min_attention: float = 0.0
    max_attention: float = 0.0


class AttentionMetricsSnapshot(BaseModel):
    """Latest attention metrics emitted by the backend streaming layer."""

    face_present: bool = False
    eyes_open: bool = False
    gaze_forward: bool = False
    head_upright: bool = False
    head_direction: str = "unknown"
    drowsy: bool = False
    drowsiness_state: str = "inactive"
    distracted: bool = False
    attention_state: str = "inactive"
    focus_state: str = "inactive"
    raw_attention_score: float = 0.0
    attention_score: float = 0.0
    components: dict[str, float] = Field(default_factory=dict)
    landmarks_detected: bool = False
    timestamp: str
    session: SessionSummary | None = None


class AttentionStatusResponse(BaseModel):
    """REST snapshot for monitoring backend attention state."""

    service: str = "focuslens-backend"
    active_sessions: int = 0
    timestamp: str
    latest_metrics: AttentionMetricsSnapshot | None = None


class WebSocketEvent(BaseModel):
    """Control event sent over the attention WebSocket."""

    event: str
    timestamp: str
    session: SessionSummary | dict[str, Any] | None = None
    detail: str | None = None
