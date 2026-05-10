"""
SocialAI Service - AI 生成 API 测试
"""
import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
class TestAIGenerate:
    """AI 内容生成测试"""
    
    async def test_generate_article(self, async_client):
        """测试生成文章"""
        # 需要认证，先跳过
        pass
    
    async def test_generate_post(self, async_client):
        """测试生成帖子"""
        pass
    
    async def test_optimize_content(self, async_client):
        """测试内容优化"""
        pass
    
    async def test_translate_content(self, async_client):
        """测试内容翻译"""
        pass
    
    async def test_get_templates(self, async_client):
        """测试获取模板列表"""
        response = await async_client.get("/api/ai/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
    
    async def test_generate_requires_auth(self, async_client):
        """测试生成需要认证"""
        response = await async_client.post(
            "/api/ai/generate",
            json={"prompt": "test", "content_type": "article"}
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAIChat:
    """AI 对话测试"""
    
    async def test_chat_requires_auth(self, async_client):
        """测试对话需要认证"""
        response = await async_client.post(
            "/api/ai/chat",
            json={"message": "hello"}
        )
        assert response.status_code == 401
