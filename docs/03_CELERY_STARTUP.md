# SocialAI Service - Celery 启动问题详细报告

**问题日期**: 2026-04-29  
**状态**: ✅ 已解决  
**更新日期**: 2026-04-29

---

## 1. 问题概述

SocialAI 平台的定时发布功能依赖 **Celery Worker + Celery Beat**。

平台在离线4周后（2026-04-29）重启，发现这两个服务未自动启动。

### 问题影响

- ❌ 定时发布任务无法执行
- ❌ 失败任务无法自动重试
- ✅ 但手动发布功能不受影响（可通过 API 直接触发）

---

## 2. Celery 组件说明

SocialAI 使用 Celery 作为异步任务队列和定时调度器。

### 组件职责

| 组件 | 进程名 | 职责 |
|------|--------|------|
| **Worker** | `celery worker` | 执行实际的发布任务（发微信/LinkedIn帖子） |
| **Beat** | `celery beat` | 定时调度器，每60秒触发一次 `check_pending_schedules` 任务 |

### 任务列表

| 任务名 | 说明 | 触发方式 |
|--------|------|----------|
| `tasks.publish.check_pending_schedules` | 检查并执行待发布任务 | Beat 每 60 秒 |
| `tasks.publish.execute_publish` | 执行单个发布任务 | API 手动触发 |
| `tasks.publish.retry_failed` | 重试失败任务 | API 手动触发 |

### 架构图

```
┌─────────────┐     ┌─────────┐     ┌──────────────┐
│  Celery     │────▶│  Redis  │◀────│  Celery      │
│  Beat       │     │  (Broker│     │  Worker      │
│  (调度器)    │     │   &     │     │  (执行器)    │
│             │     │  Backend)│    │              │
└─────────────┘     └─────────┘     └──────────────┘
      │                                    │
      │ 每60秒检查                          │ 执行发布
      ▼                                    ▼
┌─────────────┐                     ┌─────────────┐
│ PostgreSQL  │                     │   微信/     │
│ (调度记录)  │                     │  LinkedIn   │
└─────────────┘                     └─────────────┘
```

---

## 3. 依赖服务状态

启动 Celery 前需确保以下服务正常运行：

| 服务 | 地址 | 检查命令 | 状态 |
|------|------|----------|------|
| PostgreSQL | localhost:5432 | `docker ps \| grep postgres` | ✅ 已启动 |
| Redis | localhost:6379 | `docker exec socialai-redis-dev redis-cli ping` | ✅ 已启动 |

---

## 4. 已完成的操作 (2026-04-29)

### 4.1 环境准备

```bash
# 1. 启动 Docker 容器
docker start socialai-postgres-dev socialai-redis-dev

# 2. 验证容器运行
docker ps | grep -E "postgres|redis"
```

### 4.2 数据库初始化

首次启动时需创建数据库用户和数据库：

```bash
# 创建角色
docker exec socialai-postgres-dev psql -U postgres -c \
  "CREATE ROLE socialai WITH LOGIN PASSWORD 'socialai_dev_password';"

# 创建数据库
docker exec socialai-postgres-dev psql -U postgres -c \
  "CREATE DATABASE socialai_dev OWNER socialai;"
```

### 4.3 启动 Celery Worker

```bash
cd /home/gefa/Projects/SocialAI-Service/api

DATABASE_URL="postgresql://socialai:socialai_dev_password@127.0.0.1:5432/socialai_dev" \
REDIS_URL="redis://localhost:6379" \
celery -A tasks.publish.celery_app worker \
  --loglevel=info \
  > /tmp/celery-worker.log 2>&1 &
```

### 4.4 启动 Celery Beat

```bash
cd /home/gefa/Projects/SocialAI-Service/api

DATABASE_URL="postgresql://socialai:socialai_dev_password@127.0.0.1:5432/socialai_dev" \
REDIS_URL="redis://localhost:6379" \
celery -A tasks.publish.celery_app beat \
  --loglevel=info \
  > /tmp/celery-beat.log 2>&1 &
```

### 4.5 验证启动成功

```bash
# 检查进程
pgrep -a -f "celery"

# 查看 Worker 日志
tail -20 /tmp/celery-worker.log

# 查看 Beat 日志
tail -10 /tmp/celery-beat.log
```

**期望输出**:
```
# Worker
celery@gefa ready.

# Beat
beat: Starting...
```

---

## 5. 一键启动脚本 (start-dev.sh)

当前 `start-dev.sh` 脚本内容已包含 Celery 启动逻辑：

```bash
#!/bin/bash
# SocialAI Service - 一键启动所有服务

# 检查 Redis
if docker ps | grep -q socialai-redis-dev; then
    echo "✅ Redis 已运行"
else
    echo "⚠️  Redis 未运行，请先启动 Docker"
    exit 1
fi

# 检查 PostgreSQL
if docker ps | grep -q socialai-postgres-dev; then
    echo "✅ PostgreSQL 已运行"
else
    echo "⚠️  PostgreSQL 未运行，请先启动 Docker"
    exit 1
fi

# 启动 Celery Worker
if pgrep -f "celery.*worker" > /dev/null; then
    echo "✅ Celery Worker 已运行"
else
    nohup celery -A tasks.publish.celery_app worker --loglevel=info \
      > /tmp/celery-worker.log 2>&1 &
    sleep 2
    echo "✅ Celery Worker 已启动"
fi

# 启动 Celery Beat
if pgrep -f "celery.*beat" > /dev/null; then
    echo "✅ Celery Beat 已运行"
else
    nohup celery -A tasks.publish.celery_app beat --loglevel=info \
      > /tmp/celery-beat.log 2>&1 &
    sleep 2
    echo "✅ Celery Beat 已启动"
fi

# 启动 FastAPI
# ... (见 start-dev.sh 完整内容)

# 启动 Vite 前端
# ... (见 start-dev.sh 完整内容)
```

**问题**: `start-dev.sh` 依赖环境变量文件 `.env`，但需要手动 `source` 或导出。

---

## 6. 启动命令完整版

### 完整启动步骤（每次重启后需执行）

```bash
# ===== 第一步：启动 Docker 服务 =====
docker start socialai-postgres-dev socialai-redis-dev

# ===== 第二步：初始化数据库（如首次）=====
docker exec socialai-postgres-dev psql -U postgres -c \
  "CREATE ROLE socialai WITH LOGIN PASSWORD 'socialai_dev_password';"
docker exec socialai-postgres-dev psql -U postgres -c \
  "CREATE DATABASE socialai_dev OWNER socialai;"

# ===== 第三步：启动后端 =====
cd /home/gefa/Projects/SocialAI-Service/api
export DATABASE_URL="postgresql://socialai:socialai_dev_password@127.0.0.1:5432/socialai_dev"
export REDIS_URL="redis://localhost:6379"
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload \
  > /tmp/backend.log 2>&1 &

# ===== 第四步：启动 Celery Worker =====
cd /home/gefa/Projects/SocialAI-Service/api
export DATABASE_URL="postgresql://socialai:socialai_dev_password@127.0.0.1:5432/socialai_dev"
export REDIS_URL="redis://localhost:6379"
nohup celery -A tasks.publish.celery_app worker --loglevel=info \
  > /tmp/celery-worker.log 2>&1 &

# ===== 第五步：启动 Celery Beat =====
cd /home/gefa/Projects/SocialAI-Service/api
export DATABASE_URL="postgresql://socialai:socialai_dev_password@127.0.0.1:5432/socialai_dev"
export REDIS_URL="redis://localhost:6379"
nohup celery -A tasks.publish.celery_app beat --loglevel=info \
  > /tmp/celery-beat.log 2>&1 &

# ===== 第六步：启动前端 =====
cd /home/gefa/Projects/SocialAI-Service/frontend
nohup npm run dev > /tmp/vite.log 2>&1 &
```

---

## 7. 已知问题

### 7.1 docker-compose 段错误

**问题**: 在当前环境（磁盘 94% 紧张）下，`docker-compose` 命令执行会段错误。

**现象**:
```
段错误 (core dumped)
```

**影响**: 无法使用 `docker-compose -f docker-compose.dev.yml up -d` 方式启动。

**临时解决方案**: 直接使用 `docker run` 或 `docker start` 管理容器。

**建议**: 清理磁盘空间后重试。

### 7.2 环境变量需手动导出

**问题**: Celery 启动命令需要显式传入 `DATABASE_URL` 和 `REDIS_URL` 环境变量。

**原因**: `start-dev.sh` 脚本不会自动从 `.env` 文件加载环境变量。

**建议**: 
- 修改 `start-dev.sh` 自动加载 `.env`
- 或使用 systemd/supervisor 管理服务并配置环境变量

### 7.3 Celery 无开机自启

**问题**: 服务器重启后 Celery 服务不会自动启动。

**建议方案**:
1. 使用 `systemd` 创建服务单元
2. 或使用 `supervisor` 管理进程
3. 或使用 `pm2` 管理 Node/Python 混合服务

---

## 8. 推荐的 systemd 服务配置

### /etc/systemd/system/socialai-worker.service

```ini
[Unit]
Description=SocialAI Celery Worker
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=gefa
WorkingDirectory=/home/gefa/Projects/SocialAI-Service/api
Environment="DATABASE_URL=postgresql://socialai:socialai_dev_password@127.0.0.1:5432/socialai_dev"
Environment="REDIS_URL=redis://localhost:6379"
ExecStart=/usr/bin/python3 -m celery -A tasks.publish.celery_app worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### /etc/systemd/system/socialai-beat.service

```ini
[Unit]
Description=SocialAI Celery Beat
After=network.target redis.service postgresql.service socialai-worker.service

[Service]
Type=simple
User=gefa
WorkingDirectory=/home/gefa/Projects/SocialAI-Service/api
Environment="DATABASE_URL=postgresql://socialai:socialai_dev_password@127.0.0.1:5432/socialai_dev"
Environment="REDIS_URL=redis://localhost:6379"
ExecStart=/usr/bin/python3 -m celery -A tasks.publish.celery_app beat --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**使用**:
```bash
sudo systemctl enable socialai-worker socialai-beat
sudo systemctl start socialai-worker socialai-beat
```

---

## 9. 日志位置

| 服务 | 日志文件 |
|------|----------|
| 后端 | `/tmp/backend.log` |
| Celery Worker | `/tmp/celery-worker.log` |
| Celery Beat | `/tmp/celery-beat.log` |
| Vite 前端 | `/tmp/vite.log` |

---

## 10. 相关文件

| 文件 | 说明 |
|------|------|
| `api/celery_config.py` | Celery 配置（含 Beat 调度表） |
| `api/tasks/publish.py` | 定时发布任务定义 |
| `api/.env` | 环境变量配置 |
| `start-dev.sh` | 一键启动脚本 |
| `docker-compose.dev.yml` | 开发环境 Docker 配置 |
| `Makefile` | 快速命令 |

---

## 11. 状态总结 (2026-04-29 13:27)

| 检查项 | 状态 | 说明 |
|--------|------|------|
| Docker 容器 | ✅ | postgres + redis 已启动 |
| PostgreSQL | ✅ | socialai_dev 数据库已创建 |
| Redis | ✅ | 响应 PONG |
| Celery Worker | ✅ | celery@gefa ready |
| Celery Beat | ✅ | beat: Starting... |
| FastAPI | ✅ | http://localhost:8000 |
| Vite 前端 | ✅ | http://localhost:5173 |

**结论**: 所有服务已就绪，问题已解决。