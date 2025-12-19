"""Voice generation API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class VoiceGenerationRequest(BaseModel):
    """音声生成リクエスト"""
    text: str = Field(..., description="読み上げテキスト")
    speaker: str = Field(default="zundamon", description="話者名")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="話速")
    pitch: float = Field(default=0.0, ge=-0.15, le=0.15, description="音高")
    intonation: float = Field(default=1.0, ge=0.0, le=2.0, description="抑揚")


class VoiceGenerationResponse(BaseModel):
    """音声生成レスポンス"""
    audio_path: str = Field(..., description="生成された音声ファイルのパス")
    duration: float = Field(..., description="音声の長さ（秒）")


@router.post("/generate", response_model=VoiceGenerationResponse)
async def generate_voice(request: VoiceGenerationRequest):
    """
    音声を生成する
    
    - **text**: 読み上げテキスト
    - **speaker**: 話者名
    - **speed**: 話速
    - **pitch**: 音高
    - **intonation**: 抑揚
    """
    try:
        logger.info(f"音声生成リクエスト: speaker={request.speaker}, text={request.text[:50]}...")
        
        # TODO: VoiceGeneratorを使用して音声生成
        # from app.core.voice_generator import VoiceGenerator
        # generator = VoiceGenerator()
        # audio_path = generator.generate_voice(
        #     text=request.text,
        #     speaker=request.speaker,
        #     speed=request.speed,
        #     pitch=request.pitch,
        #     intonation=request.intonation
        # )
        
        # 仮実装
        raise HTTPException(
            status_code=501,
            detail="音声生成機能は実装中です（VoiceGenerator統合待ち）"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"音声生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/speakers")
async def get_speakers():
    """
    利用可能な話者一覧を取得する
    """
    try:
        # TODO: Charactersから話者一覧を取得
        # from app.config.characters import Characters
        # speakers = Characters.get_all()
        
        # 仮実装
        return {
            "speakers": [
                {"id": "zundamon", "name": "ずんだもん"},
                {"id": "metan", "name": "四国めたん"}
            ]
        }
        
    except Exception as e:
        logger.error(f"話者一覧取得エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """音声生成APIのヘルスチェック"""
    return {"status": "healthy", "service": "voices"}
