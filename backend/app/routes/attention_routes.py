from fastapi import APIRouter, Request

from app.models.websocket_models import AttentionStatusResponse

router = APIRouter(prefix="/attention", tags=["attention"])


@router.get("/status", response_model=AttentionStatusResponse)
async def attention_status(request: Request):
    return request.app.state.attention.status_snapshot()
