"""
SocialAI Service - 配置文件
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(
        extra="ignore",  # 忽略额外字段
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # 应用配置
    APP_NAME: str = "SocialAI Service"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/socialai"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI模型配置 (MiniMax)
    MINIMAX_API_KEY: str = ""
    MINIMAX_MODEL: str = "MiniMax-M2.5"
    
    # 社交媒体API配置
    # MVP阶段: 微信 + LinkedIn
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    WECHAT_TOKEN: str = ""
    LINKEDIN_API_KEY: str = ""
    LINKEDIN_API_SECRET: str = ""
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
