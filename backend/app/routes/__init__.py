from fastapi import APIRouter

from app.routes.attention_routes import router as attention_router
from app.routes.health import router as health_router
from app.routes.websocket import router as websocket_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(attention_router)
api_router.include_router(websocket_router)
