"""
SocialAI Service - 数据模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_user_email', 'email'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    avatar_url = Column(Text)
    subscription_tier = Column(String(20), default="free")
    subscription_status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    contents = relationship("Content", back_populates="user")
    social_accounts = relationship("SocialAccount", back_populates="user")


class SocialAccount(Base):
    __tablename__ = "social_accounts"
    __table_args__ = (
        Index('idx_sa_user_id', 'user_id'),
        Index('idx_sa_platform', 'platform'),
        Index('idx_sa_is_active', 'is_active'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    platform = Column(String(50), nullable=False)
    account_name = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="social_accounts")
    schedules = relationship("Schedule", back_populates="social_account")


class Content(Base):
    __tablename__ = "contents"
    __table_args__ = (
        Index('idx_content_user_id', 'user_id'),
        Index('idx_content_status', 'status'),
        Index('idx_content_type', 'content_type'),
        Index('idx_content_created_at', 'created_at'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255))
    body = Column(Text, nullable=False)
    content_type = Column(String(50))
    status = Column(String(20), default="draft")
    ai_prompt_used = Column(Text)
    platform_specific = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="contents")
    schedules = relationship("Schedule", back_populates="content")


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        Index('idx_schedule_user_id', 'user_id'),
        Index('idx_schedule_content_id', 'content_id'),
        Index('idx_schedule_account_id', 'social_account_id'),
        Index('idx_schedule_status', 'status'),
        Index('idx_schedule_scheduled_at', 'scheduled_at'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id", ondelete="CASCADE"))
    social_account_id = Column(UUID(as_uuid=True), ForeignKey("social_accounts.id", ondelete="CASCADE"))
    scheduled_at = Column(DateTime, nullable=False)
    published_at = Column(DateTime)
    status = Column(String(20), default="pending")
    platform_post_id = Column(Text)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    content = relationship("Content", back_populates="schedules")
    social_account = relationship("SocialAccount", back_populates="schedules")
    analytics = relationship("Analytics", back_populates="schedule")


class Analytics(Base):
    __tablename__ = "analytics"
    __table_args__ = (
        Index('idx_analytics_schedule_id', 'schedule_id'),
        Index('idx_analytics_platform', 'platform'),
        Index('idx_analytics_collected_at', 'collected_at'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("schedules.id", ondelete="CASCADE"))
    platform = Column(String(50), nullable=False)
    impressions = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    schedule = relationship("Schedule", back_populates="analytics")
