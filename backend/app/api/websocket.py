from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from celery.result import AsyncResult
import asyncio
import logging
import json

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/progress/{task_id}")
async def websocket_progress(websocket: WebSocket, task_id: str):
    """
    タスクの進捗をWebSocketでリアルタイム配信

    Args:
        task_id: Celeryタスクのタスク ID
    """
    await websocket.accept()
    logger.info(f"WebSocket接続確立: task_id={task_id}")

    try:
        while True:
            task = AsyncResult(task_id, app=celery_app)

            if task.state == "PENDING":
                response = {
                    "task_id": task_id,
                    "status": "pending",
                    "progress": 0.0,
                    "message": "タスクは待機中です",
                }
            elif task.state == "PROGRESS":
                info = task.info or {}
                response = {
                    "task_id": task_id,
                    "status": "processing",
                    "progress": info.get("progress", 0.0),
                    "message": info.get("message", "処理中..."),
                }
            elif task.state == "SUCCESS":
                result = task.result or {}
                response = {
                    "task_id": task_id,
                    "status": "completed",
                    "progress": 1.0,
                    "message": result.get("message", "完了しました"),
                    "result": result,
                }
            elif task.state == "FAILURE":
                info = task.info or {}
                response = {
                    "task_id": task_id,
                    "status": "failed",
                    "progress": 0.0,
                    "message": info.get("message", "タスクが失敗しました"),
                    "error": str(info.get("error", task.info)),
                }
            else:
                response = {
                    "task_id": task_id,
                    "status": task.state.lower(),
                    "progress": 0.0,
                    "message": f"状態: {task.state}",
                }

            await websocket.send_json(response)

            if task.state in ["SUCCESS", "FAILURE", "REVOKED"]:
                logger.info(
                    f"タスク完了、WebSocket接続を閉じます: task_id={task_id}, state={task.state}"
                )
                break

            await asyncio.sleep(0.5)

        await websocket.close()

    except WebSocketDisconnect:
        logger.info(f"WebSocket接続が切断されました: task_id={task_id}")
    except Exception as e:
        logger.error(
            f"WebSocketエラー: task_id={task_id}, error={str(e)}", exc_info=True
        )
        try:
            await websocket.send_json(
                {
                    "task_id": task_id,
                    "status": "error",
                    "message": "サーバーエラーが発生しました",
                    "error": str(e),
                }
            )
            await websocket.close()
        except:
            pass


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    汎用通知用WebSocket
    """
    await websocket.accept()
    logger.info("通知用WebSocket接続確立")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            await websocket.send_json(
                {"type": "notification", "message": f"受信しました: {message}"}
            )

    except WebSocketDisconnect:
        logger.info("通知用WebSocket接続が切断されました")
    except Exception as e:
        logger.error(f"通知用WebSocketエラー: {str(e)}", exc_info=True)
