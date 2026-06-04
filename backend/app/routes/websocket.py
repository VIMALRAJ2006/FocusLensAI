from fastapi import APIRouter, WebSocket

from app.websocket.attention_socket import AttentionWebSocketHandler

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/attention")
async def attention_stream(websocket: WebSocket):
    handler = AttentionWebSocketHandler(websocket.app.state.attention)
    await handler.handle(websocket)