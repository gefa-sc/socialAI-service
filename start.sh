#!/bin/bash
# SocialAI Service - 启动脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 SocialAI Service - 启动服务${NC}"

# 检查 Redis
echo -e "${YELLOW}📡 检查 Redis...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Redis 未运行，尝试启动...${NC}"
    redis-server --daemonize yes
    sleep 2
fi

# 启动 Celery Worker
echo -e "${YELLOW}🔧 启动 Celery Worker...${NC}"
cd "$(dirname "$0")/api"
celery -A tasks.publish.celery_app worker --loglevel=info --concurrency=2 &

# 启动 Celery Beat (定时任务调度器)
echo -e "${YELLOW}⏰ 启动 Celery Beat (定时任务)...${NC}"
celery -A tasks.publish.celery_app beat --loglevel=info &

# 启动 FastAPI
echo -e "${YELLOW}🌐 启动 FastAPI...${NC}"
cd "$(dirname "$0")/api"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

echo -e "${GREEN}✅ 所有服务已启动!${NC}"
echo -e "  - FastAPI: http://localhost:8000"
echo -e "  - API Docs: http://localhost:8000/docs"
echo -e "  - Celery Worker: 运行中"
echo -e "  - Celery Beat: 运行中 (每分钟检查发布任务)"
