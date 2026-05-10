# SocialAI Service - 平台现状报告

**更新时间**: 2026-04-29  
**版本**: V1.0 (MVP)  
**状态**: 🟡 部分运行（离线4周后重启）

---

## 1. 服务运行状态

| 服务 | 类型 | 端口 | 地址 | 状态 |
|------|------|------|------|------|
| **PostgreSQL** | 数据库 | 5432 | localhost:5432 | ✅ 正常运行 |
| **Redis** | 缓存/队列 | 6379 | localhost:6379 | ✅ 正常运行 |
| **FastAPI** | 后端API | 8000 | http://localhost:8000 | ✅ 正常运行 |
| **Vite** | 前端开发服务器 | 5173 | http://localhost:5173 | ✅ 正常运行 |
| **Celery Worker** | 定时任务 | - | - | ❌ 未启动 |
| **Celery Beat** | 调度器 | - | - | ❌ 未启动 |

### 健康检查

```bash
# 后端
curl http://localhost:8000/health
# → {"status":"healthy"}

# 前端
curl http://localhost:5173
# → HTML页面正常返回
```

---

## 2. 技术栈现状

### 后端
- **框架**: Python/FastAPI 0.109.0
- **ASGI**: Uvicorn 0.27.0 (with reload)
- **数据库**: PostgreSQL 15 (Docker container)
- **缓存/队列**: Redis 7 (Docker container)
- **任务队列**: Celery 5.3.6
- **ORM**: SQLAlchemy 2.0.25
- **AI集成**: openai 1.10.0 / MiniMax API

### 前端
- **框架**: React 18.2.0 + Vite 5.0.8
- **UI库**: Ant Design 5.12.0
- **图表**: Recharts 3.7.0
- **路由**: React Router DOM 6.21.0
- **HTTP**: Axios 1.6.0

### 基础设施
- **容器化**: Docker 29.1.3
- **语言**: Python 3.12.3 / Node.js 22.22.2

---

## 3. 项目结构

```
SocialAI-Service/
├── api/                      # 后端
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── celery_config.py     # Celery 配置
│   ├── routers/
│   │   ├── auth.py         # 用户认证
│   │   ├── contents.py     # 内容管理
│   │   ├── schedules.py    # 发布调度
│   │   ├── analytics.py    # 数据分析
│   │   ├── social_accounts.py  # 社交账号
│   │   ├── ai.py           # AI生成
│   │   ├── dingtalk.py     # 钉钉
│   │   └── wecom.py        # 企业微信
│   ├── models/             # 数据模型
│   └── requirements.txt    # 依赖
├── frontend/                # 前端
│   ├── src/
│   │   ├── pages/          # 页面
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Accounts.jsx
│   │   │   ├── AIGenerate.jsx
│   │   │   ├── Contents.jsx
│   │   │   ├── Analytics.jsx
│   │   │   ├── Schedules.jsx
│   │   │   ├── Settings.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── components/     # 组件
│   │   └── App.jsx
│   └── package.json
├── docs/                    # 文档 (20+份)
├── docker-compose.dev.yml   # 开发环境
├── docker-compose.prod.yml  # 生产环境
├── Makefile                # 快速命令
└── start-dev.sh            # 一键启动脚本
```

---

## 4. API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `GET /` | GET | 健康检查 / API信息 |
| `GET /docs` | GET | Swagger API文档 |
| `GET /health` | GET | 健康状态 |
| `/auth/*` | * | 用户认证 |
| `/contents/*` | * | 内容管理 |
| `/schedules/*` | * | 发布调度 |
| `/analytics/*` | * | 数据分析 |
| `/social-accounts/*` | * | 社交账号管理 |
| `/ai/*` | * | AI内容生成 |
| `/MP_verify_*.txt` | GET | 微信域名验证 |

---

## 5. 已完成功能

### 核心功能
- ✅ 用户注册/登录 (JWT)
- ✅ 社交账号绑定 (微信/LinkedIn OAuth)
- ✅ AI内容生成 (MiniMax)
- ✅ 发布调度系统 (Celery + Redis)
- ✅ 内容管理 (创建/编辑/保存)
- ✅ 数据分析仪表板
- ✅ 钉钉/企业微信机器人框架

### 技术实现
- ✅ 微信公众号 OAuth 接入
- ✅ LinkedIn OAuth 接入
- ✅ Redis 任务队列
- ✅ 发布失败重试机制
- ✅ 骨架屏/错误边界/空状态 UI

---

## 6. 待完成功能 (TODO)

### 🔴 高优先级
| 功能 | 说明 | 阻塞 |
|------|------|------|
| **微信OAuth域名** | ngrok被微信风控，需已备案域名 | ⚠️ 需域名+备案 |
| **数据源接入** | GA/Mixpanel/GrowingIO 待接入 | ⏳ 待曹总决策 |
| **Celery Worker/Beat** | 定时发布任务未启动 | 🔧 待手动启动 |

### 🟡 中优先级
| 功能 | 说明 |
|------|------|
| 移动端响应式适配 |
| 主题切换 |
| 导出报告功能 |
| 数据实时更新 |
| E2E测试 |

### 🟢 低优先级
| 功能 | 说明 |
|------|------|
| 生产环境 Docker 镜像 |
| Nginx + SSL 配置 |
| 微博/B站/抖音/快手平台接入 |
| 多语言支持 |
| 团队协作功能 |
| Webhook 集成 |

### 🚀 V2.0 规划
- 热点资讯监控功能
- 一键生成+发布工作流

---

## 7. 启动方式

### 方式1: 手动逐个启动 (当前使用)

```bash
# Docker 服务 (已在运行)
docker start socialai-postgres-dev socialai-redis-dev

# 后端
cd /home/gefa/Projects/SocialAI-Service/api
DATABASE_URL="postgresql://socialai:socialai_dev_password@127.0.0.1:5432/socialai_dev" \
REDIS_URL="redis://127.0.0.1:6379" ENVIRONMENT=development \
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd /home/gefa/Projects/SocialAI-Service/frontend
npm run dev
```

### 方式2: 使用 start-dev.sh
```bash
cd /home/gefa/Projects/SocialAI-Service
./start-dev.sh
```

---

## 8. 环境变量 (.env)

核心配置项 (位于 `api/.env`):

```bash
# 数据库
DATABASE_URL=postgresql://socialai:socialai_dev_password@localhost:5432/socialai_dev

# Redis
REDIS_URL=redis://localhost:6379

# AI (MiniMax)
MINIMAX_API_KEY=sk-...
MINIMAX_MODEL=MiniMax-M2.5

# 微信
WECHAT_APP_ID=wxf37bcf043708a278
WECHAT_APP_SECRET=...
WECHAT_TOKEN=...

# 钉钉
DINGTALK_APP_KEY=...
DINGTALK_APP_SECRET=...
```

---

## 9. 已知问题

| # | 问题 | 严重度 | 说明 |
|---|------|--------|------|
| 1 | 磁盘94%紧张 | 🔴 高 | 仅~2.4GB可用，/var/log/journal占2.6G |
| 2 | Celery未启动 | 🟡 中 | 定时发布任务不可用 |
| 3 | 微信OAuth域名被风控 | 🔴 高 | 需已备案域名 |
| 4 | 无数据源 | 🟡 中 | GA/Mixpanel等待接入 |
| 5 | docker-compose段错误 | 🔴 高 | 磁盘/内存问题导致docker-compose崩溃，用docker直接管理 |

---

## 10. 访问地址

| 服务 | 地址 |
|------|------|
| 前端 (Web UI) | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 (Swagger) | http://localhost:8000/docs |
| 健康检查 | http://localhost:8000/health |
