# SocialAI Service - Celery 定时发布任务配置

import os
from celery import Celery
from celery.schedules import crontab

# 从环境变量获取 Redis URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 创建 Celery 应用
celery_app = Celery(
    "socialai",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.publish"]
)

# Celery 配置
celery_app.conf.update(
    # 时区设置
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 任务序列化
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # 任务执行配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,  # 任务超时 5 分钟
    task_soft_time_limit=240,
    
    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # 结果过期时间 (天)
    result_expires=7,
    
    # 定时任务配置
    beat_schedule={
        # 每分钟检查一次待发布任务
        'check-pending-schedules': {
            'task': 'tasks.publish.check_pending_schedules',
            'schedule': 60.0,  # 每 60 秒
        },
    },
)
