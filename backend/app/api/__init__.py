"""API routers"""

from .scripts import router as scripts_router
from .videos import router as videos_router
from . import voices, management, websocket

__all__ = ["scripts", "videos", "voices", "management", "websocket"]

# 後方互換性のため
scripts = type("scripts", (), {"router": scripts_router})()
videos = type("videos", (), {"router": videos_router})()
