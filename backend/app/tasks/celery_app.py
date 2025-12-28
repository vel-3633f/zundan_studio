"""Celery application configuration"""
from celery import Celery
import os

# Celeryアプリケーションの作成
celery_app = Celery(
    'zundan_studio',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
)

# Celery設定
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Tokyo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1時間
    task_soft_time_limit=3300,  # 55分
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# タスクの自動検出
# app.tasksパッケージ内のすべてのタスクを自動検出
celery_app.autodiscover_tasks(['app.tasks'])
