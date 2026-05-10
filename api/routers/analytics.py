"""
SocialAI Service - 数据分析路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db
from models.models import User, Content, SocialAccount, Schedule, Analytics
from routers.auth import get_current_user

router = APIRouter()

# ============== Pydantic Models ==============

class OverviewResponse(BaseModel):
    """数据概览响应"""
    total_contents: int
    total_schedules: int
    total_published: int
    total_failed: int
    total_impressions: int
    total_engagements: int
    total_likes: int
    total_comments: int
    total_shares: int
    engagement_rate: float

class ContentAnalyticsResponse(BaseModel):
    """内容分析响应"""
    content_id: str
    title: Optional[str]
    platform: str
    impressions: int
    engagements: int
    likes: int
    comments: int
    shares: int
    clicks: int
    engagement_rate: float
    published_at: Optional[datetime]

class AccountAnalyticsResponse(BaseModel):
    """账户分析响应"""
    account_id: str
    platform: str
    account_name: str
    total_published: int
    total_impressions: int
    total_engagements: int
    avg_engagement_rate: float

class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str
    impressions: int
    engagements: int
    published_count: int

class TrendsResponse(BaseModel):
    """趋势数据响应"""
    period: str  # daily/weekly/monthly
    data: List[TrendDataPoint]

class ReportResponse(BaseModel):
    """报告响应"""
    period: str
    start_date: str
    end_date: str
    summary: dict
    top_contents: List[dict]
    platform_stats: List[dict]

# ============== 路由 ==============

@router.get("/overview", response_model=OverviewResponse)
def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="统计天数")
):
    """
    获取数据概览
    
    - **days**: 统计天数，默认30天
    """
    # 获取用户内容ID列表
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    # 内容统计
    total_contents = db.query(Content).filter(
        Content.user_id == current_user.id
    ).count()
    
    # 调度统计
    total_schedules = db.query(Schedule).filter(
        Schedule.content_id.in_(user_content_ids)
    ).count()
    
    # 发布统计
    total_published = db.query(Schedule).filter(
        Schedule.content_id.in_(user_content_ids),
        Schedule.status == "published"
    ).count()
    
    total_failed = db.query(Schedule).filter(
        Schedule.content_id.in_(user_content_ids),
        Schedule.status == "failed"
    ).count()
    
    # 数据分析统计
    analytics_query = db.query(Analytics).join(
        Schedule, Analytics.schedule_id == Schedule.id
    ).filter(
        Schedule.content_id.in_(user_content_ids)
    )
    
    # 如果指定了天数限制
    if days:
        start_date = datetime.utcnow() - timedelta(days=days)
        analytics_query = analytics_query.filter(
            Analytics.collected_at >= start_date
        )
    
    analytics_data = analytics_query.all()
    
    # 计算总数
    total_impressions = sum(a.impressions for a in analytics_data)
    total_likes = sum(a.likes for a in analytics_data)
    total_comments = sum(a.comments for a in analytics_data)
    total_shares = sum(a.shares for a in analytics_data)
    total_engagements = total_likes + total_comments + total_shares
    
    # 计算互动率
    engagement_rate = (total_engagements / total_impressions * 100) if total_impressions > 0 else 0
    
    return OverviewResponse(
        total_contents=total_contents,
        total_schedules=total_schedules,
        total_published=total_published,
        total_failed=total_failed,
        total_impressions=total_impressions,
        total_engagements=total_engagements,
        total_likes=total_likes,
        total_comments=total_comments,
        total_shares=total_shares,
        engagement_rate=round(engagement_rate, 2)
    )


@router.get("/content/{content_id}", response_model=List[ContentAnalyticsResponse])
def get_content_analytics(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定内容的效果分析
    
    - **content_id**: 内容ID
    """
    # 验证内容属于当前用户
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="内容不存在"
        )
    
    # 查询该内容的所有调度
    schedules = db.query(Schedule).filter(
        Schedule.content_id == content_id,
        Schedule.status == "published"
    ).all()
    
    results = []
    
    for schedule in schedules:
        # 获取账户信息
        account = db.query(SocialAccount).filter(
            SocialAccount.id == schedule.social_account_id
        ).first()
        
        # 获取分析数据
        analytics = db.query(Analytics).filter(
            Analytics.schedule_id == schedule.id
        ).first()
        
        impressions = analytics.impressions if analytics else 0
        likes = analytics.likes if analytics else 0
        comments = analytics.comments if analytics else 0
        shares = analytics.shares if analytics else 0
        engagements = likes + comments + shares
        
        results.append(ContentAnalyticsResponse(
            content_id=str(content_id),
            title=content.title,
            platform=account.platform if account else "unknown",
            impressions=impressions,
            engagements=engagements,
            likes=likes,
            comments=comments,
            shares=shares,
            clicks=analytics.clicks if analytics else 0,
            engagement_rate=round((engagements / impressions * 100) if impressions > 0 else 0, 2),
            published_at=schedule.published_at
        ))
    
    return results


@router.get("/accounts", response_model=List[AccountAnalyticsResponse])
def get_accounts_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    platform: Optional[str] = None
):
    """
    获取所有账户的分析数据
    
    - **platform**: 可选，按平台筛选
    """
    # 查询用户账户
    query = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.is_active == True
    )
    
    if platform:
        query = query.filter(SocialAccount.platform == platform)
    
    accounts = query.all()
    
    results = []
    
    for account in accounts:
        # 获取该账户的发布调度
        schedules = db.query(Schedule).filter(
            Schedule.social_account_id == account.id,
            Schedule.status == "published"
        ).all()
        
        # 获取分析数据
        analytics_list = []
        for schedule in schedules:
            analytics = db.query(Analytics).filter(
                Analytics.schedule_id == schedule.id
            ).first()
            if analytics:
                analytics_list.append(analytics)
        
        total_impressions = sum(a.impressions for a in analytics_list)
        total_likes = sum(a.likes for a in analytics_list)
        total_comments = sum(a.comments for a in analytics_list)
        total_shares = sum(a.shares for a in analytics_list)
        total_engagements = total_likes + total_comments + total_shares
        
        avg_engagement_rate = (
            (total_engagements / total_impressions * 100) 
            if total_impressions > 0 else 0
        )
        
        results.append(AccountAnalyticsResponse(
            account_id=str(account.id),
            platform=account.platform,
            account_name=account.account_name,
            total_published=len(schedules),
            total_impressions=total_impressions,
            total_engagements=total_engagements,
            avg_engagement_rate=round(avg_engagement_rate, 2)
        ))
    
    return results


@router.get("/trends", response_model=TrendsResponse)
def get_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    days: int = Query(30, ge=7, le=365)
):
    """
    获取数据趋势
    
    - **period**: 统计周期 (daily/weekly/monthly)
    - **days**: 统计天数
    """
    # 获取用户内容ID列表
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    # 计算日期范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 查询已发布的调度
    schedules = db.query(Schedule).filter(
        Schedule.content_id.in_(user_content_ids),
        Schedule.status == "published",
        Schedule.published_at >= start_date
    ).all()
    
    # 按日期分组
    trends_dict = {}
    
    for schedule in schedules:
        if not schedule.published_at:
            continue
        
        # 根据周期确定日期键
        if period == "daily":
            date_key = schedule.published_at.strftime("%Y-%m-%d")
        elif period == "weekly":
            # 周一作为周的开始
            week_start = schedule.published_at - timedelta(days=schedule.published_at.weekday())
            date_key = week_start.strftime("%Y-%m-%d")
        else:  # monthly
            date_key = schedule.published_at.strftime("%Y-%m-01")
        
        if date_key not in trends_dict:
            trends_dict[date_key] = {
                "impressions": 0,
                "engagements": 0,
                "published_count": 0
            }
        
        # 获取分析数据
        analytics = db.query(Analytics).filter(
            Analytics.schedule_id == schedule.id
        ).first()
        
        if analytics:
            trends_dict[date_key]["impressions"] += analytics.impressions
            trends_dict[date_key]["engagements"] += (
                analytics.likes + analytics.comments + analytics.shares
            )
        
        trends_dict[date_key]["published_count"] += 1
    
    # 转换为响应格式
    data = [
        TrendDataPoint(
            date=date_key,
            impressions=values["impressions"],
            engagements=values["engagements"],
            published_count=values["published_count"]
        )
        for date_key, values in sorted(trends_dict.items())
    ]
    
    return TrendsResponse(period=period, data=data)


@router.get("/report", response_model=ReportResponse)
def generate_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    period: str = Query("weekly", regex="^(weekly|monthly)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    生成数据报告
    
    - **period**: 报告周期 (weekly/monthly)
    - **start_date**: 可选，自定义开始日期 (YYYY-MM-DD)
    - **end_date**: 可选，自定义结束日期 (YYYY-MM-DD)
    """
    # 确定日期范围
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    elif period == "weekly":
        end = datetime.utcnow()
        start = end - timedelta(days=7)
    else:  # monthly
        end = datetime.utcnow()
        start = end - timedelta(days=30)
    
    # 获取用户内容ID列表
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    # 查询该期间的发布
    schedules = db.query(Schedule).filter(
        Schedule.content_id.in_(user_content_ids),
        Schedule.status == "published",
        Schedule.published_at >= start,
        Schedule.published_at <= end
    ).all()
    
    # 计算汇总数据
    total_published = len(schedules)
    total_impressions = 0
    total_engagements = 0
    platform_stats = {}
    content_stats = []
    
    for schedule in schedules:
        # 获取分析数据
        analytics = db.query(Analytics).filter(
            Analytics.schedule_id == schedule.id
        ).first()
        
        # 获取内容信息
        content = db.query(Content).filter(
            Content.id == schedule.content_id
        ).first()
        
        # 获取账户信息
        account = db.query(SocialAccount).filter(
            SocialAccount.id == schedule.social_account_id
        ).first()
        
        impressions = analytics.impressions if analytics else 0
        likes = analytics.likes if analytics else 0
        comments = analytics.comments if analytics else 0
        shares = analytics.shares if analytics else 0
        engagements = likes + comments + shares
        
        total_impressions += impressions
        total_engagements += engagements
        
        # 平台统计
        if account:
            platform = account.platform
            if platform not in platform_stats:
                platform_stats[platform] = {
                    "published": 0,
                    "impressions": 0,
                    "engagements": 0
                }
            platform_stats[platform]["published"] += 1
            platform_stats[platform]["impressions"] += impressions
            platform_stats[platform]["engagements"] += engagements
        
        # 内容统计
        if content:
            content_stats.append({
                "content_id": str(content.id),
                "title": content.title or "无标题",
                "published_at": schedule.published_at.isoformat() if schedule.published_at else None,
                "impressions": impressions,
                "engagements": engagements,
                "engagement_rate": round((engagements / impressions * 100) if impressions > 0 else 0, 2)
            })
    
    # 按互动量排序，取TOP10
    content_stats.sort(key=lambda x: x["engagements"], reverse=True)
    top_contents = content_stats[:10]
    
    # 格式化平台统计
    platform_list = [
        {
            "platform": platform,
            "published": stats["published"],
            "impressions": stats["impressions"],
            "engagements": stats["engagements"],
            "avg_engagement_rate": round(
                (stats["engagements"] / stats["impressions"] * 100) 
                if stats["impressions"] > 0 else 0, 
                2
            )
        }
        for platform, stats in platform_stats.items()
    ]
    
    # 汇总
    summary = {
        "total_published": total_published,
        "total_impressions": total_impressions,
        "total_engagements": total_engagements,
        "avg_engagement_rate": round(
            (total_engagements / total_impressions * 100) 
            if total_impressions > 0 else 0, 
            2
        )
    }
    
    return ReportResponse(
        period=period,
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        summary=summary,
        top_contents=top_contents,
        platform_stats=platform_list
    )


@router.get("/realtime")
def get_realtime_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取实时统计数据（最近24小时）
    """
    # 获取用户内容ID列表
    user_content_ids = db.query(Content.id).filter(
        Content.user_id == current_user.id
    ).subquery()
    
    # 最近24小时
    last_24h = datetime.utcnow() - timedelta(hours=24)
    
    # 新发布数量
    new_published = db.query(Schedule).filter(
        Schedule.content_id.in_(user_content_ids),
        Schedule.status == "published",
        Schedule.published_at >= last_24h
    ).count()
    
    # 新增互动
    recent_analytics = db.query(Analytics).join(
        Schedule, Analytics.schedule_id == Schedule.id
    ).filter(
        Schedule.content_id.in_(user_content_ids),
        Analytics.collected_at >= last_24h
    ).all()
    
    new_impressions = sum(a.impressions for a in recent_analytics)
    new_engagements = sum(a.likes + a.comments + a.shares for a in recent_analytics)
    
    return {
        "period": "last_24h",
        "new_published": new_published,
        "new_impressions": new_impressions,
        "new_engagements": new_engagements,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/comparison")
def compare_platforms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=365)
):
    """
    对比各平台表现
    
    - **days**: 统计天数
    """
    # 获取用户账户
    accounts = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.is_active == True
    ).all()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = []
    
    for account in accounts:
        # 该账户的发布
        schedules = db.query(Schedule).filter(
            Schedule.social_account_id == account.id,
            Schedule.status == "published",
            Schedule.published_at >= start_date
        ).all()
        
        # 汇总分析数据
        total_impressions = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        
        for schedule in schedules:
            analytics = db.query(Analytics).filter(
                Analytics.schedule_id == schedule.id
            ).first()
            
            if analytics:
                total_impressions += analytics.impressions
                total_likes += analytics.likes
                total_comments += analytics.comments
                total_shares += analytics.shares
        
        total_engagements = total_likes + total_comments + total_shares
        
        results.append({
            "platform": account.platform,
            "account_name": account.account_name,
            "published_count": len(schedules),
            "impressions": total_impressions,
            "engagements": total_engagements,
            "likes": total_likes,
            "comments": total_comments,
            "shares": total_shares,
            "engagement_rate": round(
                (total_engagements / total_impressions * 100) 
                if total_impressions > 0 else 0, 
                2
            )
        })
    
    return {
        "period_days": days,
        "platforms": results
    }
