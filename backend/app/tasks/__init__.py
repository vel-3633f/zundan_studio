"""Celery tasks"""
# タスクを明示的にインポートしてCeleryに登録
# 動画生成タスクのみをインポート（script_tasksは別途必要に応じてインポート）
from app.tasks import video_tasks

__all__ = ['video_tasks']
