"""
Celery 配置
创建 Celery 应用实例，配置 Redis broker 和 backend
"""
from celery import Celery
from app.config import settings

# 创建 Celery 应用实例
celery_app = Celery(
    "melodyclaw",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.audio_tasks"]
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区配置
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务结果过期时间 (秒)
    result_expires=3600,
    
    # 任务路由
    task_routes={
        "app.tasks.audio_tasks.*": {"queue": "audio"},
    },
    
    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # 重试配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
