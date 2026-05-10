"""
SocialAI Service - 内容管理路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
import uuid
from database import get_db
from models.models import User, Content
from routers.auth import get_current_user

router = APIRouter()

# Pydantic模型
class ContentCreate(BaseModel):
    title: Optional[str] = None
    body: str
    content_type: str = "article"
    status: str = "draft"
    ai_prompt_used: Optional[str] = None
    ai_prompt_used: Optional[str] = None

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[str] = None

class ContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: Optional[str]
    body: str
    content_type: str
    status: str
    created_at: datetime
    
    @classmethod
    def from_orm_with_id(cls, obj):
        """将 ORM 对象转换为响应模型，处理 UUID"""
        return cls(
            id=str(obj.id),
            title=obj.title,
            body=obj.body,
            content_type=obj.content_type,
            status=obj.status,
            created_at=obj.created_at
        )

# 路由
@router.get("/", response_model=List[ContentResponse])
def list_contents(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contents = db.query(Content).filter(
        Content.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return [ContentResponse.from_orm_with_id(c) for c in contents]

@router.post("/", response_model=ContentResponse)
def create_content(
    content: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_content = Content(
        user_id=current_user.id,
        title=content.title,
        body=content.body,
        content_type=content.content_type,
        status=content.status or "draft",
        ai_prompt_used=content.ai_prompt_used
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return ContentResponse.from_orm_with_id(db_content)

@router.get("/{content_id}", response_model=ContentResponse)
def get_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.user_id == current_user.id
    ).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return ContentResponse.from_orm_with_id(content)

@router.put("/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: str,
    content: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_content = db.query(Content).filter(
        Content.id == content_id,
        Content.user_id == current_user.id
    ).first()
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    update_data = content.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_content, field, value)
    
    db.commit()
    db.refresh(db_content)
    return ContentResponse.from_orm_with_id(db_content)

@router.delete("/{content_id}")
def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_content = db.query(Content).filter(
        Content.id == content_id,
        Content.user_id == current_user.id
    ).first()
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db.delete(db_content)
    db.commit()
    return {"message": "Content deleted successfully"}
