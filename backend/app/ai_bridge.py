import asyncio
import sys
from pathlib import Path

from app.config import AI_ENGINE_ROOT

if str(AI_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_ROOT))

from focuslens.pipeline import AttentionPipeline  # noqa: E402


class AIBridge:
    """Thin adapter between FastAPI and the FocusLens AI engine."""

    def __init__(self) -> None:
        self._pipeline = AttentionPipeline()

    def analyze_jpeg(self, jpeg_bytes: bytes) -> dict:
        return self._pipeline.process_jpeg_bytes(jpeg_bytes).to_dict()

    async def analyze_jpeg_async(self, jpeg_bytes: bytes) -> dict:
        return await asyncio.to_thread(self.analyze_jpeg, jpeg_bytes)

    def reset(self) -> None:
        self._pipeline.reset()

    def close(self) -> None:
        self._pipeline.close()
