"""
任务包初始化
"""
from app.tasks.celery_app import celery_app
from app.tasks import audio_tasks

__all__ = ["celery_app", "audio_tasks"]
