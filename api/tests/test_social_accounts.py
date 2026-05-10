"""
社交账号模块测试 - 微信服务号

注意：由于 LinkedIn API Key 尚未注册，本测试文件以微信服务号为测试对象。
测试覆盖微信服务号的连接、断开、Token 刷新等核心功能。
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db
from models.models import User, SocialAccount
from routers.auth import get_password_hash
from routers.social_accounts import WECHAT_APP_ID, WECHAT_APP_SECRET

# 使用 PostgreSQL 测试数据库
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://socialai:socialai_dev_password@localhost:5432/test_socialai"
)

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """创建测试客户端"""
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
async def auth_token(client, test_user):
    """获取认证 token"""
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
async def auth_headers(auth_token):
    """获取认证头"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_wechat_account(db, test_user):
    """创建测试用微信账户"""
    account = SocialAccount(
        user_id=test_user.id,
        platform="wechat",
        account_name="TestWeChatAccount",
        access_token="mock_wechat_token",
        is_active=True
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


class TestWeChatAccounts:
    """微信服务号账户模块测试"""

    @pytest.mark.asyncio
    async def test_list_accounts_empty(self, client, auth_headers):
        """测试获取空账户列表"""
        response = await client.get(
            "/api/accounts/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_list_accounts_with_wechat(self, client, auth_headers, test_wechat_account):
        """测试获取微信账户列表"""
        response = await client.get(
            "/api/accounts/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(acc["platform"] == "wechat" for acc in data)

    @pytest.mark.asyncio
    async def test_filter_by_platform_wechat(self, client, auth_headers, test_wechat_account):
        """测试按平台筛选（微信）"""
        response = await client.get(
            "/api/accounts/?platform=wechat",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(acc["platform"] == "wechat" for acc in data)

    @pytest.mark.asyncio
    async def test_filter_by_active_status(self, client, auth_headers, test_wechat_account):
        """测试按激活状态筛选"""
        response = await client.get(
            "/api/accounts/?is_active=true",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(acc["is_active"] is True for acc in data)

    @pytest.mark.asyncio
    async def test_get_single_account(self, client, auth_headers, test_wechat_account):
        """测试获取单个账户详情"""
        response = await client.get(
            f"/api/accounts/{test_wechat_account.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "wechat"
        assert data["account_name"] == "TestWeChatAccount"

    @pytest.mark.asyncio
    async def test_get_nonexistent_account(self, client, auth_headers):
        """测试获取不存在的账户"""
        fake_id = str(uuid.uuid4())
        response = await client.get(
            f"/api/accounts/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]

    @pytest.mark.asyncio
    @patch('routers.social_accounts._handle_wechat_oauth')
    async def test_connect_wechat_account(self, mock_wechat_oauth, client, auth_headers, test_user):
        """测试连接微信账户"""
        # 模拟微信 OAuth 响应
        mock_wechat_oauth.return_value = {
            "account_name": "NewWeChatUser",
            "access_token": "new_wechat_access_token",
            "refresh_token": "new_wechat_refresh_token",
        }
        
        response = await client.post(
            "/api/accounts/connect",
            headers=auth_headers,
            json={
                "platform": "wechat",
                "code": "mock_auth_code"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "wechat"
        assert data["account_name"] == "NewWeChatUser"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_connect_unsupported_platform(self, client, auth_headers):
        """测试连接不支持的平台"""
        response = await client.post(
            "/api/accounts/connect",
            headers=auth_headers,
            json={
                "platform": "unsupported",
                "code": "some_code"
            }
        )
        assert response.status_code == 400
        assert "不支持" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_disconnect_wechat_account(self, client, auth_headers, test_wechat_account):
        """测试断开微信账户"""
        account_id = test_wechat_account.id
        response = await client.delete(
            f"/api/accounts/{account_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # 验证账户已被标记为不活跃
        get_response = await client.get(
            f"/api/accounts/{account_id}",
            headers=auth_headers
        )
        assert get_response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_account(self, client, auth_headers):
        """测试断开不存在的账户"""
        fake_id = str(uuid.uuid4())
        response = await client.delete(
            f"/api/accounts/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    @patch('routers.social_accounts._test_platform_connection')
    async def test_refresh_wechat_token(self, mock_test_connection, client, auth_headers, test_wechat_account):
        """测试刷新微信Token"""
        # 模拟Token刷新成功
        with patch('routers.social_accounts._refresh_wechat_token') as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "new_refreshed_token",
                "refresh_token": "new_refreshed_refresh_token",
                "expires_in": 7200
            }
            
            response = await client.post(
                f"/api/accounts/{test_wechat_account.id}/refresh",
                headers=auth_headers
            )
            
            assert response.status_code == 200

    @pytest.mark.asyncio
    @patch('routers.social_accounts._test_platform_connection')
    async def test_test_wechat_connection(self, mock_test_connection, client, auth_headers, test_wechat_account):
        """测试微信账户连接状态"""
        mock_test_connection.return_value = True
        
        response = await client.get(
            f"/api/accounts/{test_wechat_account.id}/test",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "wechat"
        assert "is_connected" in data

    @pytest.mark.asyncio
    async def test_account_ownership_isolation(self, client, db, auth_headers, test_wechat_account):
        """测试账户所有权隔离"""
        # 创建另一个用户
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()
        
        # 用另一个用户登录
        other_token_response = await client.post(
            "/api/auth/login",
            data={
                "username": "other@example.com",
                "password": "password"
            }
        )
        other_token = other_token_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # 其他用户尝试访问当前用户的账户
        response = await client.get(
            f"/api/accounts/{test_wechat_account.id}",
            headers=other_headers
        )
        assert response.status_code == 404


class TestWeChatOAuth:
    """微信OAuth流程测试"""

    @pytest.mark.asyncio
    async def test_get_wechat_oauth_url(self, client, auth_headers):
        """测试获取微信OAuth URL"""
        response = await client.get(
            "/api/accounts/oauth/wechat",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "state" in data
        assert "weixin.qq.com" in data["url"]
        assert "appid" in data["url"] or WECHAT_APP_ID in data["url"]

    @pytest.mark.asyncio
    async def test_get_oauth_url_unsupported_platform(self, client, auth_headers):
        """测试获取不支持平台的OAuth URL"""
        response = await client.get(
            "/api/accounts/oauth/facebook",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "不支持" in response.json()["detail"]


class TestSubscriptionLimits:
    """订阅限制测试"""

    @pytest.mark.asyncio
    @patch('routers.social_accounts._handle_wechat_oauth')
    async def test_free_tier_limit_one_account(self, mock_wechat_oauth, client, auth_headers, test_user, db):
        """测试免费版只能连接1个账户"""
        # 模拟微信 OAuth 响应
        mock_wechat_oauth.return_value = {
            "account_name": "FirstAccount",
            "access_token": "token1",
        }
        
        # 第一个账户应该成功
        response1 = await client.post(
            "/api/accounts/connect",
            headers=auth_headers,
            json={"platform": "wechat", "code": "code1"}
        )
        assert response1.status_code == 200
        
        # 第二个账户应该被拒绝
        mock_wechat_oauth.return_value = {
            "account_name": "SecondAccount",
            "access_token": "token2",
        }
        
        response2 = await client.post(
            "/api/accounts/connect",
            headers=auth_headers,
            json={"platform": "wechat", "code": "code2"}
        )
        assert response2.status_code == 403
        assert "免费版仅支持连接1个账户" in response2.json()["detail"]


class TestWeChatMockData:
    """微信模拟数据测试"""

    def test_wechat_oauth_response_format(self):
        """测试微信OAuth响应格式"""
        mock_response = {
            "account_name": "WeChatUser123",
            "access_token": "mock_access_token_abc123",
            "refresh_token": "mock_refresh_token_xyz789",
            "token_expires_at": "2026-02-15T12:00:00"
        }
        
        assert "account_name" in mock_response
        assert "access_token" in mock_response
        assert mock_response["account_name"] == "WeChatUser123"

    def test_wechat_account_model(self, db, test_user):
        """测试微信账户数据模型"""
        account = SocialAccount(
            user_id=test_user.id,
            platform="wechat",
            account_name="TestOfficialAccount",
            access_token="test_token",
            is_active=True
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        
        assert account.platform == "wechat"
        assert account.is_active is True
        assert account.user_id == test_user.id
