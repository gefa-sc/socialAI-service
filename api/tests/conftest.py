"""
SocialAI Service - 后端测试配置
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试配置 - 使用与开发环境相同的数据库
TEST_DATABASE_URL = "postgresql://socialai:socialai_dev_password@localhost:5432/test_socialai"
