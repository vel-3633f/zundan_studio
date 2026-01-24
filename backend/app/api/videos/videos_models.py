"""動画生成APIのリクエスト/レスポンスモデル"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

from app.models.scripts.common import VideoSection


class ConversationLine(BaseModel):
    """会話行"""

    speaker: str = Field(..., description="話者名")
    text: str = Field(..., description="セリフ内容")
    text_for_voicevox: Optional[str] = Field(None, description="VOICEVOX用テキスト")
    expression: str = Field(default="normal", description="表情")
    background: str = Field(default="default", description="背景")
    visible_characters: Optional[List[str]] = Field(None, description="表示するキャラクターリスト")
    character_expressions: Optional[Dict[str, str]] = Field(None, description="キャラクターごとの表情")


class VideoGenerationRequest(BaseModel):
    """動画生成リクエスト"""

    conversations: List[ConversationLine] = Field(..., description="会話リスト")
    title: Optional[str] = Field(None, description="動画のタイトル（フォルダ名として使用）")
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


class JsonFileInfo(BaseModel):
    """JSONファイル情報"""

    filename: str = Field(..., description="ファイル名")
    path: str = Field(..., description="ファイルパス")
    is_generated: bool = Field(default=False, description="動画生成済みかどうか")


class JsonFileStatusUpdate(BaseModel):
    """JSONファイルステータス更新リクエスト"""

    is_generated: bool = Field(..., description="動画生成済みかどうか")

