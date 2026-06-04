import os
from pathlib import Path

AI_ENGINE_ROOT = Path(__file__).resolve().parents[2] / "ai-engine"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
