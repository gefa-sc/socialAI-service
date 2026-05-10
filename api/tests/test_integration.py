"""
SocialAI Service - 集成测试
验证多个模块之间的协作
"""
import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# 使用 PostgreSQL 测试数据库
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://socialai:socialai_dev_password@localhost:5432/test_socialai"
)


class TestUserFlow:
    """用户流程集成测试：注册→登录→创建内容"""
    
    @pytest.mark.asyncio
    async def test_complete_user_flow(self):
        """测试完整用户流程"""
        # 设置数据库URL
        os.environ['DATABASE_URL'] = TEST_DATABASE_URL
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # 1. 注册新用户
            register_response = await client.post(
                "/api/auth/register",
                json={
                    "email": "integration@test.com",
                    "password": "test123456",
                    "name": "Integration Test"
                }
            )
            assert register_response.status_code == 200
            user_data = register_response.json()
            assert user_data["email"] == "integration@test.com"
            user_id = user_data["id"]
            
            # 2. 登录
            login_response = await client.post(
                "/api/auth/login",
                data={
                    "username": "integration@test.com",
                    "password": "test123456"
                }
            )
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3. 创建内容
            content_response = await client.post(
                "/api/contents/",
                headers=headers,
                json={
                    "title": "集成测试内容",
                    "body": "这是集成测试创建的内容",
                    "content_type": "article"
                }
            )
            assert content_response.status_code == 200
            content_data = content_response.json()
            content_id = content_data["id"]
            
            # 4. 获取内容列表
            list_response = await client.get(
                "/api/contents/",
                headers=headers
            )
            assert list_response.status_code == 200
            contents = list_response.json()
            assert len(contents) >= 1
            
            # 5. 获取用户信息
            me_response = await client.get(
                "/api/auth/me",
                headers=headers
            )
            assert me_response.status_code == 200
            me_data = me_response.json()
            assert me_data["email"] == "integration@test.com"
            
            print(f"✅ 完整用户流程测试通过! 用户ID: {user_id}, 内容ID: {content_id}")


class TestContentSchedulingFlow:
    """内容→调度流程集成测试"""
    
    @pytest.mark.asyncio
    async def test_content_to_scheduling_flow(self):
        """测试内容创建到调度的流程"""
        os.environ['DATABASE_URL'] = TEST_DATABASE_URL
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # 1. 注册登录
            await client.post(
                "/api/auth/register",
                json={
                    "email": "schedule@test.com",
                    "password": "test123456",
                    "name": "Schedule Test"
                }
            )
            
            login_resp = await client.post(
                "/api/auth/login",
                data={"username": "schedule@test.com", "password": "test123456"}
            )
            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. 创建内容
            content_resp = await client.post(
                "/api/contents/",
                headers=headers,
                json={
                    "title": "调度测试内容",
                    "body": "测试调度流程",
                    "content_type": "article"
                }
            )
            content_id = content_resp.json()["id"]
            
            # 3. 获取调度列表（空）
            schedules_resp = await client.get(
                "/api/schedules/",
                headers=headers
            )
            assert schedules_resp.status_code == 200
            initial_count = len(schedules_resp.json())
            
            # 4. 获取数据概览
            analytics_resp = await client.get(
                "/api/analytics/overview",
                headers=headers,
                params={"days": 7}
            )
            assert analytics_resp.status_code == 200
            
            print(f"✅ 内容→调度流程测试通过! 内容ID: {content_id}, 初始调度数: {initial_count}")


class TestAPIHealth:
    """API健康检查"""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试API健康检查"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            print(f"✅ 健康检查通过: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
