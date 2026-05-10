"""
内容管理模块测试
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db
from models.models import User, Content
from routers.auth import get_password_hash

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
def test_content(db, test_user):
    """创建测试内容"""
    content = Content(
        user_id=test_user.id,
        title="Test Content Title",
        body="This is test content body",
        content_type="article",
        status="draft"
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


class TestContents:
    """内容管理模块测试"""

    @pytest.mark.asyncio
    async def test_create_content(self, client, auth_headers):
        """测试创建内容"""
        response = await client.post(
            "/api/contents/",
            headers=auth_headers,
            json={
                "title": "New Content",
                "body": "This is new content body",
                "content_type": "article"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Content"
        assert data["body"] == "This is new content body"
        assert data["content_type"] == "article"
        assert data["status"] == "draft"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_content_without_title(self, client, auth_headers):
        """测试创建无标题内容"""
        response = await client.post(
            "/api/contents/",
            headers=auth_headers,
            json={
                "body": "Content without title",
                "content_type": "tweet"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] is None
        assert data["body"] == "Content without title"

    @pytest.mark.asyncio
    async def test_create_content_without_auth(self, client):
        """测试无认证创建内容"""
        response = await client.post(
            "/api/contents/",
            json={
                "title": "New Content",
                "body": "This is new content body"
            }
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_contents(self, client, auth_headers, test_content):
        """测试获取内容列表"""
        response = await client.get(
            "/api/contents/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_list_contents_with_pagination(self, client, auth_headers, test_content):
        """测试内容列表分页"""
        # 创建更多内容
        for i in range(5):
            await client.post(
                "/api/contents/",
                headers=auth_headers,
                json={
                    "title": f"Content {i}",
                    "body": f"Body {i}",
                    "content_type": "article"
                }
            )
        
        response = await client.get(
            "/api/contents/?skip=0&limit=2",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_content(self, client, auth_headers, test_content):
        """测试获取单个内容"""
        response = await client.get(
            f"/api/contents/{test_content.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == test_content.title
        assert data["body"] == test_content.body

    @pytest.mark.asyncio
    async def test_get_nonexistent_content(self, client, auth_headers):
        """测试获取不存在的内容"""
        fake_id = str(uuid.uuid4())
        response = await client.get(
            f"/api/contents/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_content(self, client, auth_headers, test_content):
        """测试更新内容"""
        response = await client.put(
            f"/api/contents/{test_content.id}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "status": "published"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "published"
        # 其他字段应保持不变
        assert data["body"] == test_content.body

    @pytest.mark.asyncio
    async def test_update_content_partial(self, client, auth_headers, test_content):
        """测试部分更新内容"""
        original_body = test_content.body
        response = await client.put(
            f"/api/contents/{test_content.id}",
            headers=auth_headers,
            json={
                "title": "New Title Only"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title Only"
        assert data["body"] == original_body  # 未更新的字段保持不变

    @pytest.mark.asyncio
    async def test_delete_content(self, client, auth_headers, test_content):
        """测试删除内容"""
        content_id = test_content.id
        response = await client.delete(
            f"/api/contents/{content_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # 验证内容已删除
        get_response = await client.get(
            f"/api/contents/{content_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_content(self, client, auth_headers):
        """测试删除不存在的内容"""
        fake_id = str(uuid.uuid4())
        response = await client.delete(
            f"/api/contents/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_content_ownership_isolation(self, client, db, auth_headers):
        """测试内容所有权隔离"""
        # 创建另一个用户
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()
        
        # 用另一个用户创建内容
        other_token_response = await client.post(
            "/api/auth/login",
            data={
                "username": "other@example.com",
                "password": "password"
            }
        )
        other_token = other_token_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # 其他用户创建内容
        other_content = await client.post(
            "/api/contents/",
            headers=other_headers,
            json={
                "title": "Other User Content",
                "body": "Private content",
                "content_type": "article"
            }
        )
        other_content_id = other_content.json()["id"]
        
        # 当前用户尝试访问其他用户的内容
        response = await client.get(
            f"/api/contents/{other_content_id}",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestContentTypes:
    """内容类型测试"""

    @pytest.mark.asyncio
    async def test_create_article(self, client, auth_headers):
        """测试创建文章"""
        response = await client.post(
            "/api/contents/",
            headers=auth_headers,
            json={
                "title": "My Article",
                "body": "Article body content",
                "content_type": "article"
            }
        )
        assert response.status_code == 200
        assert response.json()["content_type"] == "article"

    @pytest.mark.asyncio
    async def test_create_tweet(self, client, auth_headers):
        """测试创建推文"""
        response = await client.post(
            "/api/contents/",
            headers=auth_headers,
            json={
                "body": "This is a tweet",
                "content_type": "tweet"
            }
        )
        assert response.status_code == 200
        assert response.json()["content_type"] == "tweet"

    @pytest.mark.asyncio
    async def test_create_post(self, client, auth_headers):
        """测试创建帖子"""
        response = await client.post(
            "/api/contents/",
            headers=auth_headers,
            json={
                "body": "Social media post",
                "content_type": "post"
            }
        )
        assert response.status_code == 200
        assert response.json()["content_type"] == "post"


class TestContentStatus:
    """内容状态测试"""

    @pytest.mark.asyncio
    async def test_default_status_is_draft(self, client, auth_headers):
        """测试默认状态为草稿"""
        response = await client.post(
            "/api/contents/",
            headers=auth_headers,
            json={
                "body": "Test content",
                "content_type": "article"
            }
        )
        assert response.json()["status"] == "draft"

    @pytest.mark.asyncio
    async def test_update_status_to_published(self, client, auth_headers, test_content):
        """测试更新状态为已发布"""
        response = await client.put(
            f"/api/contents/{test_content.id}",
            headers=auth_headers,
            json={"status": "published"}
        )
        assert response.json()["status"] == "published"

    @pytest.mark.asyncio
    async def test_update_status_to_scheduled(self, client, auth_headers, test_content):
        """测试更新状态为已调度"""
        response = await client.put(
            f"/api/contents/{test_content.id}",
            headers=auth_headers,
            json={"status": "scheduled"}
        )
        assert response.json()["status"] == "scheduled"
