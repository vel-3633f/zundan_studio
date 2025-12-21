from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import logging

from app.models.food_over import VideoSection

logger = logging.getLogger(__name__)

router = APIRouter()


class ConversationLine(BaseModel):
    """会話行"""
    speaker: str = Field(..., description="話者名")
    text: str = Field(..., description="セリフ内容")
    text_for_voicevox: Optional[str] = Field(None, description="VOICEVOX用テキスト")
    expression: str = Field(default="normal", description="表情")
    background: str = Field(default="default", description="背景")


class VideoGenerationRequest(BaseModel):
    """動画生成リクエスト"""
    conversations: List[ConversationLine] = Field(..., description="会話リスト")
    enable_subtitles: bool = Field(default=True, description="字幕を有効にする")
    conversation_mode: str = Field(default="duo", description="会話モード")
    sections: Optional[List[VideoSection]] = Field(None, description="セクション情報")
    speed: Optional[float] = Field(None, description="話速")
    pitch: Optional[float] = Field(None, description="音高")
    intonation: Optional[float] = Field(None, description="抑揚")


class VideoGenerationResponse(BaseModel):
    """動画生成レスポンス"""
    task_id: str = Field(..., description="タスクID")
    status: str = Field(..., description="ステータス")
    message: str = Field(..., description="メッセージ")


class VideoStatusResponse(BaseModel):
    """動画生成ステータスレスポンス"""
    task_id: str
    status: str
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """
    会話動画を生成する
    
    - **conversations**: 会話リスト
    - **enable_subtitles**: 字幕を有効にするか
    - **conversation_mode**: 会話モード（duo, solo等）
    - **sections**: セクション情報（オプション）
    """
    try:
        logger.info(f"動画生成リクエスト: {len(request.conversations)}会話")
        
        return VideoGenerationResponse(
            task_id="temp-task-id",
            status="pending",
            message="動画生成機能は実装中です（Celeryタスク統合待ち）"
        )
        
    except Exception as e:
        logger.error(f"動画生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=VideoStatusResponse)
async def get_video_status(task_id: str):
    """
    動画生成のステータスを取得する
    
    - **task_id**: タスクID
    """
    try:
        return VideoStatusResponse(
            task_id=task_id,
            status="pending",
            progress=0.0,
            message="ステータス取得機能は実装中です（Celeryタスク統合待ち）"
        )
        
    except Exception as e:
        logger.error(f"ステータス取得エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """動画生成APIのヘルスチェック"""
    return {"status": "healthy", "service": "videos"}
