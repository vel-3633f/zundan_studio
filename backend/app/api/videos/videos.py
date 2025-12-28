"""動画生成API"""

from fastapi import APIRouter
from typing import List
from .videos_models import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoStatusResponse,
    JsonFileInfo,
)
from .videos_handlers import (
    handle_generate_video,
    handle_get_video_status,
    handle_list_json_files,
    handle_get_json_file,
)

router = APIRouter()


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """会話動画を生成する"""
    return await handle_generate_video(request)


@router.get("/status/{task_id}", response_model=VideoStatusResponse)
async def get_video_status(task_id: str):
    """動画生成のステータスを取得する"""
    return await handle_get_video_status(task_id)


@router.get("/health")
async def health_check():
    """動画生成APIのヘルスチェック"""
    return {"status": "healthy", "service": "videos"}


@router.get("/json-files", response_model=List[JsonFileInfo])
async def list_json_files():
    """outputs/json/ディレクトリ内のJSONファイル一覧を取得する"""
    return await handle_list_json_files()


@router.get("/json-files/{filename:path}")
async def get_json_file(filename: str):
    """指定されたJSONファイルの内容を取得する"""
    return await handle_get_json_file(filename)
