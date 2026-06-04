import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.ai_bridge import AIBridge


@dataclass
class Session:
    """Tracks one live attention-monitoring session."""

    id: str
    bridge: AIBridge
    started_at: float = field(default_factory=time.time)
    frame_count: int = 0
    scores: list[float] = field(default_factory=list)

    def record_frame(self, attention_score: float) -> None:
        self.frame_count += 1
        self.scores.append(attention_score)

    def summary(self) -> dict[str, Any]:
        duration = max(time.time() - self.started_at, 0.0)
        avg = sum(self.scores) / len(self.scores) if self.scores else 0.0
        return {
            "id": self.id,
            "frame_count": self.frame_count,
            "duration_sec": round(duration, 1),
            "avg_attention": round(avg, 2),
            "min_attention": round(min(self.scores), 2) if self.scores else 0.0,
            "max_attention": round(max(self.scores), 2) if self.scores else 0.0,
        }


class SessionService:
    """Creates, tracks, and tears down monitoring sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, bridge=AIBridge())
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def active_count(self) -> int:
        return len(self._sessions)

    def end(self, session_id: str) -> dict[str, Any] | None:
        session = self._sessions.pop(session_id, None)
        if not session:
            return None
        summary = session.summary()
        session.bridge.close()
        return summary

    def close_all(self) -> None:
        for session_id in list(self._sessions):
            self.end(session_id)
