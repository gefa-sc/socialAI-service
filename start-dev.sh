#!/bin/bash
# SocialAI Service - 一键启动所有服务

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 SocialAI Service - 启动所有服务${NC}\n"

# 检查 Redis
echo -e "${YELLOW}📡 检查 Redis...${NC}"
if docker ps | grep -q socialai-redis-dev; then
    echo -e "✅ Redis 已运行"
else
    echo -e "${RED}⚠️  Redis 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 检查 PostgreSQL
echo -e "${YELLOW}🗄️ 检查 PostgreSQL...${NC}"
if docker ps | grep -q socialai-postgres-dev; then
    echo -e "✅ PostgreSQL 已运行"
else
    echo -e "${RED}⚠️  PostgreSQL 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 启动 Celery Worker
echo -e "${YELLOW}🔧 启动 Celery Worker...${NC}"
cd "$SCRIPT_DIR/api"
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "✅ Celery Worker 已运行"
else
    nohup celery -A tasks.publish.celery_app worker --loglevel=info > /tmp/celery-worker.log 2>&1 &
    sleep 2
    echo -e "✅ Celery Worker 已启动"
fi

# 启动 Celery Beat
echo -e "${YELLOW}⏰ 启动 Celery Beat...${NC}"
if pgrep -f "celery.*beat" > /dev/null; then
    echo -e "✅ Celery Beat 已运行"
else
    nohup celery -A tasks.publish.celery_app beat --loglevel=info > /tmp/celery-beat.log 2>&1 &
    sleep 2
    echo -e "✅ Celery Beat 已启动"
fi

# 启动 FastAPI
echo -e "${YELLOW}🌐 启动 FastAPI...${NC}"
if lsof -i:8000 > /dev/null 2>&1; then
    echo -e "✅ FastAPI 已运行"
else
    cd "$SCRIPT_DIR/api"
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
    sleep 3
    echo -e "✅ FastAPI 已启动"
fi

# 启动 Vite 前端
echo -e "${YELLOW}🎨 启动 Vite 前端...${NC}"
if lsof -i:5173 > /dev/null 2>&1; then
    echo -e "✅ Vite 前端 已运行"
else
    cd "$SCRIPT_DIR/frontend"
    nohup npm run dev > /tmp/vite.log 2>&1 &
    sleep 3
    echo -e "✅ Vite 前端 已启动"
fi

echo -e "\n${GREEN}✅ 所有服务已启动!${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  🎨 前端:    http://localhost:5173"
echo -e "  🌐 后端:    http://localhost:8000"
echo -e "  📚 API文档: http://localhost:8000/docs"
echo -e "  📊 Celery:  运行中 (Worker + Beat)"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
