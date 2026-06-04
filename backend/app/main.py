from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routes import api_router
from app.services.attention_service import AttentionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.attention = AttentionService()
    yield
    app.state.attention.close_all()


def create_app() -> FastAPI:
    application = FastAPI(
        title="FocusLens AI API",
        description="Real-time classroom attention tracking backend",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)
    return application


app = create_app()
