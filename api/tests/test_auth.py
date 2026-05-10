"""
认证模块测试
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import uuid

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db
from models.models import User
from routers.auth import get_password_hash, pwd_context

# 使用 PostgreSQL 测试数据库
# 注意：需要先创建 test_socialai 数据库: CREATE DATABASE test_socialai;
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
    """创建测试数据库表"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.rollback()
    db.close()
    # 清理测试数据
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


class TestAuth:
    """认证模块测试"""

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """测试用户注册成功"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "newpassword123",
                "name": "New User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, test_user):
        """测试重复邮箱注册"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "name": "Duplicate User"
            }
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """测试无效邮箱注册"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
                "name": "Bad Email"
            }
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user):
        """测试登录成功"""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_user):
        """测试错误密码登录"""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """测试不存在的用户登录"""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client, test_user):
        """测试获取当前用户信息"""
        # 先登录获取 token
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            }
        )
        token = login_response.json()["access_token"]

        # 获取当前用户信息
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client):
        """测试无 token 获取用户信息"""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client):
        """测试无效 token 获取用户信息"""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


class TestPasswordUtils:
    """密码工具函数测试"""

    def test_password_hashing(self):
        """测试密码哈希"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert pwd_context.verify(password, hashed) is True
        assert pwd_context.verify("wrongpassword", hashed) is False

    def test_password_hash_unique(self):
        """测试相同密码生成不同哈希"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # bcrypt 生成随机盐
        assert pwd_context.verify(password, hash1) is True
        assert pwd_context.verify(password, hash2) is True
