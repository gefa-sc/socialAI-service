"""
SocialAI Service - 发布调度路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db
from models.models import User, Content, SocialAccount, Schedule
from routers.auth import get_current_user

router = APIRouter()

# ============== Pydantic Models ==============

class ScheduleCreate(BaseModel):
    """创建调度请求"""
    content_id: str
    social_account_id: str
    scheduled_at: datetime

class ScheduleUpdate(BaseModel):
    """更新调度请求"""
    scheduled_at: Optional[datetime] = None
    social_account_id: Optional[str] = None

class ScheduleResponse(BaseModel):
    """调度响应"""
    id: str
    content_id: str
    social_account_id: str
    scheduled_at: datetime
    published_at: Optional[datetime] = None
    status: str
    platform_post_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ScheduleListResponse(BaseModel):
    """调度列表响应"""
    total: int
    items: List[ScheduleResponse]

# ============== 路由 ==============

@router.get("/", response_model=ScheduleListResponse)
def list_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    platform: Optional[str] = None
):
    """
    获取调度列表
    
    - **page**: 页码，默认1
    - **page_size**: 每页数量，默认20
    - **status**: 按状态筛选 (pending/published/failed/cancelled)
    - **platform**: 按平台筛选 (wechat/linkedin)
    """
    # 查询用户的内容
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    # 查询调度
    query = db.query(Schedule).filter(
        Schedule.content_id.in_(user_content_ids)
    )
    
    # 按平台筛选
    if platform:
        account_ids = db.query(SocialAccount.id).filter(
            SocialAccount.user_id == current_user.id,
            SocialAccount.platform == platform
        ).subquery()
        query = query.filter(Schedule.social_account_id.in_(account_ids))
    
    # 按状态筛选
    if status:
        query = query.filter(Schedule.status == status)
    
    # 总数
    total = query.count()
    
    # 分页
    schedules = query.order_by(Schedule.scheduled_at.asc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {"total": total, "items": schedules}


@router.post("/", response_model=ScheduleResponse)
def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的调度
    
    - **content_id**: 要发布的内容ID
    - **social_account_id**: 目标社交账户ID
    - **scheduled_at**: 计划发布时间
    """
    # 验证内容属于当前用户
    content = db.query(Content).filter(
        Content.id == schedule_data.content_id,
        Content.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="内容不存在"
        )
    
    # 验证内容状态
    if content.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已发布的内容不能再次调度"
        )
    
    # 验证社交账户属于当前用户
    account = db.query(SocialAccount).filter(
        SocialAccount.id == schedule_data.social_account_id,
        SocialAccount.user_id == current_user.id,
        SocialAccount.is_active == True
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社交账户不存在或已断开"
        )
    
    # 验证发布时间
    if schedule_data.scheduled_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="发布时间必须是将来的时间"
        )
    
    # 检查是否已存在相同调度
    existing = db.query(Schedule).filter(
        Schedule.content_id == schedule_data.content_id,
        Schedule.social_account_id == schedule_data.social_account_id,
        Schedule.status == "pending"
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该内容已存在待发布的调度"
        )
    
    # 创建调度
    new_schedule = Schedule(
        user_id=current_user.id,
        content_id=schedule_data.content_id,
        social_account_id=schedule_data.social_account_id,
        scheduled_at=schedule_data.scheduled_at,
        status="pending"
    )
    db.add(new_schedule)
    
    # 更新内容状态
    content.status = "scheduled"
    
    db.commit()
    db.refresh(new_schedule)
    
    return new_schedule


@router.get("/queue", response_model=List[ScheduleResponse])
def get_publish_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """
    获取待发布队列（即将执行的调度）
    """
    # 查询用户的内容ID
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    # 查询即将发布的调度
    schedules = db.query(Schedule).filter(
        Schedule.content_id.in_(user_content_ids),
        Schedule.status == "pending",
        Schedule.scheduled_at <= datetime.utcnow() + timedelta(minutes=5)
    ).order_by(Schedule.scheduled_at.asc())\
        .limit(limit)\
        .all()
    
    return schedules


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取调度详情"""
    # 验证调度属于当前用户
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.content_id.in_(user_content_ids)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="调度不存在"
        )
    
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新调度
    
    - 只能更新 pending 状态的调度
    - 只能修改发布时间和目标账户
    """
    # 验证调度属于当前用户
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.content_id.in_(user_content_ids)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="调度不存在"
        )
    
    # 只能更新pending状态的调度
    if schedule.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法更新{schedule.status}状态的调度"
        )
    
    # 更新发布时间
    if schedule_data.scheduled_at:
        if schedule_data.scheduled_at <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="发布时间必须是将来的时间"
            )
        schedule.scheduled_at = schedule_data.scheduled_at
    
    # 更新目标账户
    if schedule_data.social_account_id:
        account = db.query(SocialAccount).filter(
            SocialAccount.id == schedule_data.social_account_id,
            SocialAccount.user_id == current_user.id,
            SocialAccount.is_active == True
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="社交账户不存在或已断开"
            )
        
        schedule.social_account_id = schedule_data.social_account_id
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除调度
    
    - pending状态：直接删除
    - 其他状态：标记为cancelled
    """
    # 验证调度属于当前用户
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.content_id.in_(user_content_ids)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="调度不存在"
        )
    
    # 更新内容状态
    content = db.query(Content).filter(
        Content.id == schedule.content_id
    ).first()
    
    if schedule.status == "pending":
        # 直接删除
        db.delete(schedule)
        # 恢复内容为草稿
        if content:
            content.status = "draft"
    else:
        # 标记为取消
        schedule.status = "cancelled"
        if content and content.status == "scheduled":
            content.status = "draft"
    
    db.commit()
    
    return {"message": "调度已删除"}


@router.post("/{schedule_id}/cancel", response_model=ScheduleResponse)
def cancel_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取消调度
    """
    # 验证调度属于当前用户
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.content_id.in_(user_content_ids)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="调度不存在"
        )
    
    if schedule.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法取消{schedule.status}状态的调度"
        )
    
    # 标记为取消
    schedule.status = "cancelled"
    
    # 更新内容状态
    content = db.query(Content).filter(
        Content.id == schedule.content_id
    ).first()
    if content:
        content.status = "draft"
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.post("/{schedule_id}/publish-now", response_model=ScheduleResponse)
def publish_now(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    立即发布（跳过定时，立即执行）
    """
    # 验证调度属于当前用户
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.content_id.in_(user_content_ids)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="调度不存在"
        )
    
    if schedule.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法立即发布{schedule.status}状态的调度"
        )
    
    # 立即执行发布
    success, result = _execute_publish(schedule, db)
    
    if success:
        schedule.status = "published"
        schedule.published_at = datetime.utcnow()
        schedule.platform_post_id = result.get("post_id")
        
        # 更新内容状态
        content = db.query(Content).filter(
            Content.id == schedule.content_id
        ).first()
        if content:
            content.status = "published"
    else:
        schedule.status = "failed"
        schedule.error_message = result.get("error")
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.get("/{schedule_id}/status")
def get_schedule_status(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取调度状态详情
    """
    # 验证调度属于当前用户
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.content_id.in_(user_content_ids)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="调度不存在"
        )
    
    # 获取关联信息
    content = db.query(Content).filter(
        Content.id == schedule.content_id
    ).first()
    
    account = db.query(SocialAccount).filter(
        SocialAccount.id == schedule.social_account_id
    ).first()
    
    return {
        "schedule_id": str(schedule.id),
        "status": schedule.status,
        "scheduled_at": schedule.scheduled_at.isoformat() if schedule.scheduled_at else None,
        "published_at": schedule.published_at.isoformat() if schedule.published_at else None,
        "error_message": schedule.error_message,
        "content": {
            "id": str(content.id) if content else None,
            "title": content.title if content else None,
            "body": content.body[:100] + "..." if content and len(content.body) > 100 else content.body if content else None
        } if content else None,
        "account": {
            "id": str(account.id) if account else None,
            "platform": account.platform if account else None,
            "account_name": account.account_name if account else None
        } if account else None
    }


# ============== 发布执行函数 ==============

def _execute_publish(schedule: Schedule, db: Session) -> tuple:
    """
    执行发布操作
    
    返回: (success: bool, result: dict)
    """
    # 获取内容和账户
    content = db.query(Content).filter(
        Content.id == schedule.content_id
    ).first()
    
    account = db.query(SocialAccount).filter(
        SocialAccount.id == schedule.social_account_id
    ).first()
    
    if not content or not account:
        return (False, {"error": "内容或账户不存在"})
    
    try:
        # 根据平台调用不同的发布API
        if account.platform == "wechat":
            post_id = _publish_to_wechat(account, content)
        elif account.platform == "linkedin":
            post_id = _publish_to_linkedin(account, content)
        else:
            return (False, {"error": f"不支持的平台: {account.platform}"})
        
        return (True, {"post_id": post_id})
    
    except Exception as e:
        return (False, {"error": str(e)})


def _publish_to_wechat(account: SocialAccount, content: Content) -> str:
    """
    发布到微信公众号
    """
    import httpx
    
    # 调用微信群发API
    url = "https://api.weixin.qq.com/cgi-bin/message/mass/sendall"
    params = {
        "access_token": account.access_token
    }
    
    data = {
        "filter": {
            "is_to_all": True
        },
        "text": {
            "content": content.body
        },
        "msgtype": "text"
    }
    
    response = httpx.post(url, params=params, json=data)
    result = response.json()
    
    if "errcode" in result and result["errcode"] != 0:
        raise Exception(f"微信发布失败: {result.get('errmsg')}")
    
    # 返回msg_id作为post_id
    return str(result.get("msg_id", ""))


def _publish_to_linkedin(account: SocialAccount, content: Content) -> str:
    """
    发布到LinkedIn
    """
    import httpx
    
    # 调用LinkedIn API
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {account.access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    # 构建LinkedIn帖子数据
    data = {
        "author": f"urn:li:person:{account.account_name}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content.body
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    response = httpx.post(url, headers=headers, json=data)
    
    if response.status_code != 201:
        raise Exception(f"LinkedIn发布失败: {response.text}")
    
    result = response.json()
    return result.get("id", "")
