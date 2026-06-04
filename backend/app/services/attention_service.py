import copy
import time
from datetime import datetime, timezone
from typing import Any

from app.services.session_service import Session, SessionService


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00",
        "Z",
    )


class AttentionService:
    """Coordinates the AI engine and session state for attention streaming."""

    def __init__(self) -> None:
        self.sessions = SessionService()
        self._latest_metrics: dict[str, Any] | None = None

    def start_session(self) -> Session:
        return self.sessions.create()

    async def analyze_frame(self, session_id: str, jpeg_bytes: bytes) -> dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Unknown session: {session_id}")

        metrics = await session.bridge.analyze_jpeg_async(jpeg_bytes)
        session.record_frame(metrics.get("attention_score", 0.0))
        payload = self._stream_payload(metrics, session.summary())
        self._latest_metrics = copy.deepcopy(payload)
        return payload

    def reset_session(self, session_id: str) -> dict[str, Any] | None:
        session = self.sessions.get(session_id)
        if not session:
            return None
        session.bridge.reset()
        session.frame_count = 0
        session.scores.clear()
        session.started_at = time.time()
        if self._latest_session_id() == session_id:
            self._latest_metrics = None
        return session.summary()

    def end_session(self, session_id: str) -> dict[str, Any] | None:
        summary = self.sessions.end(session_id)
        if self._latest_session_id() == session_id:
            self._latest_metrics = None
        return summary

    def status_snapshot(self) -> dict[str, Any]:
        return {
            "service": "focuslens-backend",
            "active_sessions": self.sessions.active_count(),
            "timestamp": utc_timestamp(),
            "latest_metrics": copy.deepcopy(self._latest_metrics),
        }

    def close_all(self) -> None:
        self.sessions.close_all()
        self._latest_metrics = None

    def _stream_payload(
        self,
        metrics: dict[str, Any],
        session_summary: dict[str, Any],
    ) -> dict[str, Any]:
        focus_state = metrics.get("attention_state", "inactive")
        return {
            **metrics,
            "focus_state": focus_state,
            "drowsiness_state": self._drowsiness_state(metrics),
            "timestamp": utc_timestamp(),
            "session": session_summary,
        }

    @staticmethod
    def _drowsiness_state(metrics: dict[str, Any]) -> str:
        if not metrics.get("face_present", False):
            return "inactive"
        return "drowsy" if metrics.get("drowsy", False) else "alert"

    def _latest_session_id(self) -> str | None:
        if not self._latest_metrics:
            return None
        session = self._latest_metrics.get("session")
        if not isinstance(session, dict):
            return None
        session_id = session.get("id")
        return session_id if isinstance(session_id, str) else None
