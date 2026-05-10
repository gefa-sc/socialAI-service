"""
SocialAI Service - 社交账户路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from database import get_db
from models.models import User, SocialAccount
from routers.auth import get_current_user

router = APIRouter()

# ============== Pydantic Models ==============

class SocialAccountCreate(BaseModel):
    """创建社交账户请求"""
    platform: str  # wechat, linkedin
    code: Optional[str] = None  # OAuth授权码

class SocialAccountResponse(BaseModel):
    """社交账户响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    platform: str
    account_name: str
    is_active: bool
    created_at: datetime
    
    @classmethod
    def from_orm_with_id(cls, obj):
        return cls(
            id=str(obj.id),
            platform=obj.platform,
            account_name=obj.account_name,
            is_active=obj.is_active,
            created_at=obj.created_at
        )

class OAuthUrlResponse(BaseModel):
    """OAuth授权URL响应"""
    url: str
    state: str

class AccountConnectRequest(BaseModel):
    """账户连接请求"""
    platform: str
    code: str

# ============== OAuth 配置 ==============

# ============== OAuth 配置 ==============

from config import settings

# 微信OAuth配置
WECHAT_APP_ID = settings.WECHAT_APP_ID or "your_app_id"
WECHAT_APP_SECRET = settings.WECHAT_APP_SECRET or "your_app_secret"
WECHAT_REDIRECT_URI = "https://hypothyroid-salvatore-silty.ngrok-free.dev/api/accounts/callback/wechat"

# LinkedIn OAuth配置
LINKEDIN_CLIENT_ID = settings.LINKEDIN_API_KEY or "your_client_id"
LINKEDIN_CLIENT_SECRET = settings.LINKEDIN_API_SECRET or "your_client_secret"
LINKEDIN_REDIRECT_URI = "https://hypothyroid-salvatore-silty.ngrok-free.dev/api/accounts/callback/linkedin"

# ============== 路由 ==============

@router.get("/", response_model=List[SocialAccountResponse])
def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    platform: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """
    获取当前用户的社交账户列表
    
    - **platform**: 可选，按平台筛选 (wechat/linkedin)
    - **is_active**: 可选，按激活状态筛选
    """
    query = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id
    )
    
    if platform:
        query = query.filter(SocialAccount.platform == platform)
    if is_active is not None:
        query = query.filter(SocialAccount.is_active == is_active)
    
    accounts = query.order_by(SocialAccount.created_at.desc()).all()
    return [SocialAccountResponse.from_orm_with_id(a) for a in accounts]


@router.post("/connect", response_model=SocialAccountResponse)
def connect_account(
    request: AccountConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    连接新的社交账户（通过OAuth授权码）
    
    - **platform**: 平台类型 (wechat/linkedin)
    - **code**: OAuth授权码
    """
    # 检查订阅限制（免费版只能连接1个账户）
    if current_user.subscription_tier == "free":
        existing_count = db.query(SocialAccount).filter(
            SocialAccount.user_id == current_user.id,
            SocialAccount.is_active == True
        ).count()
        if existing_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="免费版仅支持连接1个账户，请升级到专业版"
            )
    
    # 根据平台处理OAuth
    if request.platform == "wechat":
        account_info = _handle_wechat_oauth(request.code)
    elif request.platform == "linkedin":
        account_info = _handle_linkedin_oauth(request.code)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的平台: {request.platform}"
        )
    
    # 检查是否已存在相同账户
    existing = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform == request.platform,
        SocialAccount.account_name == account_info["account_name"]
    ).first()
    
    if existing:
        # 更新现有账户
        existing.access_token = account_info["access_token"]
        existing.refresh_token = account_info.get("refresh_token")
        existing.token_expires_at = account_info.get("token_expires_at")
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing
    
    # 创建新账户
    new_account = SocialAccount(
        user_id=current_user.id,
        platform=request.platform,
        account_name=account_info["account_name"],
        access_token=account_info["access_token"],
        refresh_token=account_info.get("refresh_token"),
        token_expires_at=account_info.get("token_expires_at"),
        is_active=True
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return SocialAccountResponse.from_orm_with_id(new_account)


@router.get("/oauth/{platform}", response_model=OAuthUrlResponse)
def get_oauth_url(
    platform: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取OAuth授权URL（用于前端跳转）
    """
    import secrets
    
    state = secrets.token_urlsafe(16)
    
    if platform == "wechat":
        url = (
            f"https://open.weixin.qq.com/connect/oauth2/authorize?"
            f"appid={WECHAT_APP_ID}&"
            f"redirect_uri={WECHAT_REDIRECT_URI}&"
            f"response_type=code&"
            f"scope=snsapi_base&"
            f"state={state}#wechat_redirect"
        )
    elif platform == "linkedin":
        url = (
            f"https://www.linkedin.com/oauth/v2/authorization?"
            f"response_type=code&"
            f"client_id={LINKEDIN_CLIENT_ID}&"
            f"redirect_uri={LINKEDIN_REDIRECT_URI}&"
            f"scope=r_liteprofile%20w_member_social&"
            f"state={state}"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的平台: {platform}"
        )
    
    return {"url": url, "state": state}


@router.get("/callback/{platform}")
def oauth_callback(
    platform: str,
    code: str = Query(...),
    state: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    OAuth授权回调处理
    """
    # 处理微信回调
    if platform == "wechat":
        account_info = _handle_wechat_oauth(code)
    elif platform == "linkedin":
        account_info = _handle_linkedin_oauth(code)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的平台: {platform}"
        )
    
    # 创建或更新账户
    existing = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform == platform,
        SocialAccount.account_name == account_info["account_name"]
    ).first()
    
    if existing:
        existing.access_token = account_info["access_token"]
        existing.is_active = True
        db.commit()
    else:
        new_account = SocialAccount(
            user_id=current_user.id,
            platform=platform,
            account_name=account_info["account_name"],
            access_token=account_info["access_token"],
            refresh_token=account_info.get("refresh_token"),
            is_active=True
        )
        db.add(new_account)
        db.commit()
    
    # 返回成功页面（前端可以跳转到管理页面）
    return {
        "status": "success",
        "message": f"{platform} 账户连接成功",
        "platform": platform
    }


@router.get("/{account_id}", response_model=SocialAccountResponse)
def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定账户详情"""
    account = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账户不存在"
        )
    
    return SocialAccountResponse.from_orm_with_id(account)


@router.delete("/{account_id}")
def disconnect_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    断开社交账户连接
    """
    account = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账户不存在"
        )
    
    # 软删除：标记为不活跃
    account.is_active = False
    db.commit()
    
    return {"message": f"{account.platform} 账户已断开连接"}


@router.post("/{account_id}/refresh")
def refresh_account_token(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    刷新账户Token
    """
    account = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账户不存在"
        )
    
    # 根据平台刷新Token
    if account.platform == "wechat":
        new_token = _refresh_wechat_token(account.refresh_token)
    elif account.platform == "linkedin":
        new_token = _refresh_linkedin_token(account.refresh_token)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的平台: {account.platform}"
        )
    
    account.access_token = new_token["access_token"]
    if new_token.get("refresh_token"):
        account.refresh_token = new_token["refresh_token"]
    if new_token.get("expires_in"):
        from datetime import timedelta
        account.token_expires_at = datetime.utcnow() + timedelta(seconds=new_token["expires_in"])
    
    db.commit()
    
    return {"message": "Token刷新成功"}


@router.get("/{account_id}/test")
def test_account_connection(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    测试账户连接状态
    """
    account = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账户不存在"
        )
    
    # 简单测试：验证Token是否有效
    is_valid = _test_platform_connection(account.platform, account.access_token)
    
    return {
        "account_id": str(account.id),
        "platform": account.platform,
        "is_connected": is_valid,
        "account_name": account.account_name
    }


# ============== 平台OAuth处理函数 ==============

def _handle_wechat_oauth(code: str) -> dict:
    """处理微信OAuth"""
    import httpx
    
    # 用授权码换取access_token
    url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    params = {
        "appid": WECHAT_APP_ID,
        "secret": WECHAT_APP_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    
    try:
        response = httpx.get(url, params=params)
        data = response.json()
        
        if "errcode" in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"微信授权失败: {data.get('errmsg')}"
            )
        
        # 获取用户信息
        user_info_url = "https://api.weixin.qq.com/sns/userinfo"
        user_params = {
            "access_token": data["access_token"],
            "openid": data["openid"]
        }
        user_response = httpx.get(user_info_url, params=user_params)
        user_data = user_response.json()
        
        from datetime import timedelta
        return {
            "account_name": user_data.get("nickname", data["openid"]),
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "token_expires_at": datetime.utcnow() + timedelta(seconds=data.get("expires_in", 7200))
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信授权处理失败: {str(e)}"
        )


def _handle_linkedin_oauth(code: str) -> dict:
    """处理LinkedIn OAuth"""
    import httpx
    
    # 用授权码换取access_token
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET
    }
    
    try:
        response = httpx.post(url, data=data)
        token_data = response.json()
        
        if "access_token" not in token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"LinkedIn授权失败: {token_data}"
            )
        
        # 获取用户信息
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        profile_response = httpx.get(
            "https://api.linkedin.com/v2/me",
            headers=headers
        )
        profile_data = profile_response.json()
        
        from datetime import timedelta
        return {
            "account_name": f"{profile_data.get('localizedFirstName', '')} {profile_data.get('localizedLastName', '')}".strip(),
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "token_expires_at": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000))
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LinkedIn授权处理失败: {str(e)}"
        )


def _refresh_wechat_token(refresh_token: str) -> dict:
    """刷新微信Token"""
    import httpx
    
    url = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
    params = {
        "appid": WECHAT_APP_ID,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = httpx.get(url, params=params)
    data = response.json()
    
    from datetime import timedelta
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "expires_in": data.get("expires_in", 7200)
    }


def _refresh_linkedin_token(refresh_token: str) -> dict:
    """刷新LinkedIn Token"""
    # LinkedIn的refresh token只能使用一次，需要重新授权
    # 这里返回一个错误提示
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="LinkedIn Token已过期，请重新授权"
    )


def _test_platform_connection(platform: str, access_token: str) -> bool:
    """测试平台连接是否有效"""
    import httpx
    
    try:
        if platform == "wechat":
            url = "https://api.weixin.qq.com/sns/userinfo"
            params = {"access_token": access_token, "openid": "test"}
            response = httpx.get(url, params=params)
            return "errcode" not in response.json()
        
        elif platform == "linkedin":
            headers = {"Authorization": f"Bearer {access_token}"}
            response = httpx.get("https://api.linkedin.com/v2/me", headers=headers)
            return response.status_code == 200
        
        return False
    except:
        return False
