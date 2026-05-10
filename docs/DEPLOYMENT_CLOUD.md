# SocialAI Service 云端部署方案

**版本**: v1.2
**更新日期**: 2026-03-03

---

## 1. 项目概述

- **项目名称**: SocialAI Service
- **项目描述**: AI驱动的社交媒体管理助手
- **目标**: 12个月内MRR达到$50,000
- **技术栈**: React + FastAPI + PostgreSQL + Redis + Celery

---

## 2. 云端架构

```
┌─────────────────────────────────────────────────────────────┐
│                      云服务器                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              OpenClaw Gateway (Agent)                 │  │
│  │              agent-socialai                          │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Frontend  │  │   API      │  │  Worker    │           │
│  │  (Vite)    │  │ (FastAPI)  │  │  (Celery)  │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                             │
│  ┌────────────┐  ┌────────────┐                          │
│  │ PostgreSQL │  │   Redis    │                          │
│  └────────────┘  └────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 部署步骤

### 3.1 环境准备

```bash
# 1. 安装Docker
curl -fsSL https://get.docker.com | sh

# 2. 安装Docker Compose
apt install docker-compose

# 3. 创建工作目录
mkdir -p ~/socialai-manager
cd ~/socialai-manager
```

### 3.2 项目部署

```bash
# 方式A: Docker Compose (推荐)
git clone https://github.com/your-repo/SocialAI-Service.git
cd SocialAI-Service

# 配置环境变量
cp api/.env.example api/.env
# 编辑 .env 文件

# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps
```

### 3.3 端口配置

| 服务 | 端口 | 说明 |
|------|------|------|
| Frontend | 5173 | Vite开发服务器 |
| API | 8000 | FastAPI后端 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| Celery | 5555 | Celery Flower (可选) |

---

## 4. Agent集成

### 4.1 agent-socialai 配置

```yaml
# 云端 openclaw.json
{
  "agents": {
    "socialai": {
      "model": "minimax-portal/MiniMax-M2.5",
      "workspace": "~/socialai-manager/SocialAI-Service",
      "skills": ["github", "feishu-doc"]
    }
  }
}
```

### 4.2 启动Agent

```bash
# 在云端启动Agent
openclaw agent --agent socialai --mode session
```

---

## 5. 本地连接

### 5.1 SSH隧道方式

```bash
# 本地执行
ssh -NL 18789:localhost:18789 user@cloud-ip

# 或使用SSH隧道脚本
./connect-cloud.sh
```

### 5.2 验证连接

```bash
# 测试API
curl http://localhost:8000/health

# 测试Web
curl http://localhost:5173
```

---

## 6. 运维

### 6.1 日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f api
docker-compose logs -f frontend
```

### 6.2 备份

```bash
# 数据库备份
docker-compose exec postgres pg_dump -U socialai > backup_$(date +%Y%m%d).sql

# 备份脚本
./backup.sh
```

---

*更新: 曹佬 | 2026-03-02*
