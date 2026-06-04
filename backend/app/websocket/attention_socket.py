from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from app.models.websocket_models import WebSocketEvent
from app.services.attention_service import AttentionService, utc_timestamp


def _model_payload(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Convert NumPy scalar types into native Python types
    so FastAPI JSON serialization works correctly.
    """
    sanitized = {}

    for key, value in payload.items():
        if hasattr(value, "item"):
            sanitized[key] = value.item()
        else:
            sanitized[key] = value

    return sanitized


class AttentionWebSocketHandler:
    """Handles WebSocket lifecycle and frame streaming for one client."""

    def __init__(self, attention_service: AttentionService) -> None:
        self._attention = attention_service

    async def handle(self, websocket: WebSocket) -> None:
        await websocket.accept()

        session = self._attention.start_session()

        try:
            await websocket.send_json(
                _model_payload(
                    WebSocketEvent(
                        event="session_started",
                        timestamp=utc_timestamp(),
                        session=session.summary(),
                    )
                )
            )

            while True:
                message = await websocket.receive()

                if message.get("type") == "websocket.disconnect":
                    break

                if message.get("bytes"):
                    await self._handle_frame(
                        websocket,
                        session.id,
                        message["bytes"],
                    )

                elif "text" in message:
                    await self._handle_text(
                        websocket,
                        session.id,
                        message["text"],
                    )

        except WebSocketDisconnect:
            pass

        finally:
            summary = self._attention.end_session(session.id)

            if summary:
                try:
                    await websocket.send_json(
                        _model_payload(
                            WebSocketEvent(
                                event="session_ended",
                                timestamp=utc_timestamp(),
                                session=summary,
                            )
                        )
                    )
                except Exception:
                    pass

    async def _handle_frame(
        self,
        websocket: WebSocket,
        session_id: str,
        jpeg_bytes: bytes,
    ) -> None:
        try:
            payload = await self._attention.analyze_frame(
                session_id,
                jpeg_bytes,
            )

        except ValueError as exc:
            await websocket.send_json(
                _model_payload(
                    WebSocketEvent(
                        event="error",
                        timestamp=utc_timestamp(),
                        detail=str(exc),
                    )
                )
            )
            return

        # Fix NumPy serialization issues
        payload = _sanitize_payload(payload)

        await websocket.send_json(payload)

    async def _handle_text(
        self,
        websocket: WebSocket,
        session_id: str,
        text: str,
    ) -> None:
        command = text.strip().lower()

        if command == "reset":
            summary = self._attention.reset_session(session_id)

            await websocket.send_json(
                _model_payload(
                    WebSocketEvent(
                        event="reset",
                        timestamp=utc_timestamp(),
                        session=summary,
                    )
                )
            )
            return

        if command == "ping":
            await websocket.send_json(
                _model_payload(
                    WebSocketEvent(
                        event="pong",
                        timestamp=utc_timestamp(),
                    )
                )
            )
            return

        await websocket.send_json(
            _model_payload(
                WebSocketEvent(
                    event="error",
                    timestamp=utc_timestamp(),
                    detail=f"Unknown command: {text}",
                )
            )
        )