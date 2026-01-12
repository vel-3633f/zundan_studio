"""動画生成APIのエンドポイントハンドラー"""

from fastapi import HTTPException
from typing import Dict, Any, List
import logging
from pathlib import Path
from celery.result import AsyncResult

from app.tasks.video_tasks import generate_video_task
from app.tasks.celery_app import celery_app
from app.config.app import Paths
from .videos_models import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoStatusResponse,
    JsonFileInfo,
    JsonFileStatusUpdate,
)

logger = logging.getLogger(__name__)


async def handle_generate_video(request: VideoGenerationRequest) -> VideoGenerationResponse:
    """会話動画を生成する"""
    try:
        logger.info(f"動画生成リクエスト: {len(request.conversations)}会話")

        conversations_dict = [conv.model_dump() for conv in request.conversations]
        
        sections_dict = None
        if request.sections:
            sections_dict = [section.model_dump() for section in request.sections]

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


async def handle_get_video_status(task_id: str) -> VideoStatusResponse:
    """動画生成のステータスを取得する"""
    try:
        task_result = AsyncResult(task_id, app=celery_app)

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


async def handle_list_json_files() -> List[JsonFileInfo]:
    """outputs/json/ディレクトリ内のJSONファイル一覧を取得する"""
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

        import json

        json_files = []
        for file_path in json_dir.glob("*.json"):
            is_generated = False
            try:
                # JSONファイルを読み込んでis_generatedフラグを取得
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    is_generated = data.get("is_generated", False)
            except Exception as e:
                logger.warning(f"JSONファイル読み込みエラー ({file_path.name}): {e}")
                # 読み込みエラーが発生した場合はFalseとして扱う

            json_files.append(
                JsonFileInfo(
                    filename=file_path.name,
                    path=str(file_path.relative_to(Paths.get_outputs_dir())),
                    is_generated=is_generated,
                )
            )

        json_files.sort(key=lambda x: x.filename, reverse=True)

        logger.info(f"JSONファイル一覧取得: {len(json_files)}件")
        return json_files

    except Exception as e:
        logger.error(f"JSONファイル一覧取得エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def handle_get_json_file(filename: str) -> Dict[str, Any]:
    """指定されたJSONファイルの内容を取得する"""
    try:
        json_dir = Path(Paths.get_outputs_dir()) / "json"
        file_path = json_dir / filename

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


async def handle_update_json_file_status(
    filename: str, status_update: JsonFileStatusUpdate
) -> JsonFileInfo:
    """JSONファイルのis_generatedステータスを更新する"""
    try:
        json_dir = Path(Paths.get_outputs_dir()) / "json"
        file_path = json_dir / filename

        if not file_path.resolve().is_relative_to(json_dir.resolve()):
            raise HTTPException(status_code=400, detail="無効なファイルパスです")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")

        if not file_path.suffix == ".json":
            raise HTTPException(status_code=400, detail="JSONファイルではありません")

        import json

        # JSONファイルを読み込む
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # is_generatedフラグを更新
        data["is_generated"] = status_update.is_generated

        # JSONファイルに書き戻す
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(
            f"JSONファイルステータス更新: {filename}, is_generated={status_update.is_generated}"
        )

        return JsonFileInfo(
            filename=file_path.name,
            path=str(file_path.relative_to(Paths.get_outputs_dir())),
            is_generated=status_update.is_generated,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JSONファイルステータス更新エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def handle_delete_json_file(filename: str) -> Dict[str, Any]:
    """JSONファイルを削除する"""
    try:
        json_dir = Path(Paths.get_outputs_dir()) / "json"
        file_path = json_dir / filename

        if not file_path.resolve().is_relative_to(json_dir.resolve()):
            raise HTTPException(status_code=400, detail="無効なファイルパスです")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")

        if not file_path.suffix == ".json":
            raise HTTPException(status_code=400, detail="JSONファイルではありません")

        # ファイルを削除
        file_path.unlink()

        logger.info(f"JSONファイル削除: {filename}")

        return {"success": True, "message": f"ファイル「{filename}」を削除しました"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JSONファイル削除エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

