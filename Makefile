# SocialAI Service - Makefile

.PHONY: help dev up down restart logs build clean test celery

help:
	@echo "SocialAI Service - Docker Commands"
	@echo "===================================="
	@echo "make dev        - 启动开发环境（Docker）"
	@echo "make up         - 启动所有服务"
	@echo "make down       - 停止所有服务"
	@echo "make restart    - 重启所有服务"
	@echo "make logs       - 查看日志"
	@echo "make build      - 构建镜像"
	@echo "make clean      - 清理容器和数据"
	@echo "make test       - 运行测试"
	@echo "make celery     - 启动 Celery（定时发布）"
	@echo "make start      - 一键启动所有服务（推荐）"

# 一键启动所有服务（推荐）
start:
	@./start-dev.sh

# 启动 Celery（定时发布任务）
celery:
	@echo "启动 Celery Worker..."
	@cd api && celery -A tasks.publish.celery_app worker --loglevel=info &
	@echo "启动 Celery Beat..."
	@cd api && celery -A tasks.publish.celery_app beat --loglevel=info &
	@echo "✅ Celery 已启动"

# 开发环境
dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "开发环境已启动: http://localhost:8000"

up:
	docker-compose -f docker-compose.dev.yml up -d

down:
	docker-compose -f docker-compose.dev.yml down

restart:
	docker-compose -f docker-compose.dev.yml restart

logs:
	docker-compose -f docker-compose.dev.yml logs -f

build:
	docker-compose -f docker-compose.dev.yml build

# 清理
clean:
	docker-compose -f docker-compose.dev.yml down -v
	@echo "已清理容器和数据卷"

# 生产环境
prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# 测试
test:
	docker-compose -f docker-compose.dev.yml exec api pytest

# 数据库
db-reset:
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml up -d
	@echo "数据库已重置"

# 进入容器
shell:
	docker-compose -f docker-compose.dev.yml exec api /bin/bash
