from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import logging
import os
from pathlib import Path
from celery.result import AsyncResult

from app.models.scripts.common import VideoSection
from app.config.app import Paths
from app.tasks.video_tasks import generate_video_task
from app.tasks.celery_app import celery_app

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

        # リクエストデータをDict形式に変換
        conversations_dict = [conv.model_dump() for conv in request.conversations]
        
        # セクション情報をDict形式に変換
        sections_dict = None
        if request.sections:
            sections_dict = [section.model_dump() for section in request.sections]

        # Celeryタスクを呼び出し
        task = generate_video_task.delay(
            conversations=conversations_dict,
            enable_subtitles=request.enable_subtitles,
            conversation_mode=request.conversation_mode,
            sections=sections_dict,
            speed=request.speed,
            pitch=request.pitch,
            intonation=request.intonation
        )

        logger.info(f"動画生成タスク開始: task_id={task.id}")

        return VideoGenerationResponse(
            task_id=task.id,
            status="pending",
            message="動画生成を開始しました",
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
        # Celeryタスクの結果を取得
        task_result = AsyncResult(task_id, app=celery_app)

        # タスクの状態に応じてレスポンスを構築
        if task_result.state == "PENDING":
            response = VideoStatusResponse(
                task_id=task_id,
                status="pending",
                progress=0.0,
                message="タスクは待機中です",
            )
        elif task_result.state == "PROGRESS":
            info = task_result.info or {}
            response = VideoStatusResponse(
                task_id=task_id,
                status="processing",
                progress=info.get("progress", 0.0),
                message=info.get("message", "処理中..."),
            )
        elif task_result.state == "SUCCESS":
            result = task_result.result or {}
            response = VideoStatusResponse(
                task_id=task_id,
                status="completed",
                progress=1.0,
                message=result.get("message", "完了しました"),
                result=result,
            )
        elif task_result.state == "FAILURE":
            info = task_result.info or {}
            error_msg = str(info.get("error", task_result.info)) if isinstance(task_result.info, dict) else str(task_result.info)
            response = VideoStatusResponse(
                task_id=task_id,
                status="failed",
                progress=0.0,
                message=info.get("message", "タスクが失敗しました") if isinstance(info, dict) else "タスクが失敗しました",
                error=error_msg,
            )
        else:
            response = VideoStatusResponse(
                task_id=task_id,
                status=task_result.state.lower(),
                progress=0.0,
                message=f"状態: {task_result.state}",
            )

        return response

    except Exception as e:
        logger.error(f"ステータス取得エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """動画生成APIのヘルスチェック"""
    return {"status": "healthy", "service": "videos"}


class JsonFileInfo(BaseModel):
    """JSONファイル情報"""

    filename: str = Field(..., description="ファイル名")
    path: str = Field(..., description="ファイルパス")


@router.get("/json-files", response_model=List[JsonFileInfo])
async def list_json_files():
    """
    outputs/json/ディレクトリ内のJSONファイル一覧を取得する
    """
    try:
        outputs_dir = Paths.get_outputs_dir()
        json_dir = Path(outputs_dir) / "json"

        if not json_dir.exists():
            logger.warning(f"JSONディレクトリが存在しません: {json_dir}")
            try:
                json_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"JSONディレクトリを作成しました: {json_dir}")
            except Exception as e:
                logger.error(f"JSONディレクトリの作成に失敗しました: {e}")
            return []

        json_files = []
        for file_path in json_dir.glob("*.json"):
            json_files.append(
                {
                    "filename": file_path.name,
                    "path": str(file_path.relative_to(Paths.get_outputs_dir())),
                }
            )

        json_files.sort(key=lambda x: x["filename"], reverse=True)

        logger.info(f"JSONファイル一覧取得: {len(json_files)}件")
        return json_files

    except Exception as e:
        logger.error(f"JSONファイル一覧取得エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/json-files/{filename:path}")
async def get_json_file(filename: str):
    """
    指定されたJSONファイルの内容を取得する

    - **filename**: ファイル名（パスセパレータを含む場合はエスケープ）
    """
    try:
        json_dir = Path(Paths.get_outputs_dir()) / "json"
        file_path = json_dir / filename

        # セキュリティチェック: ディレクトリトラバーサル攻撃を防ぐ
        if not file_path.resolve().is_relative_to(json_dir.resolve()):
            raise HTTPException(status_code=400, detail="無効なファイルパスです")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")

        if not file_path.suffix == ".json":
            raise HTTPException(status_code=400, detail="JSONファイルではありません")

        import json

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"JSONファイル読み込み: {filename}")
        return data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JSONファイル読み込みエラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
