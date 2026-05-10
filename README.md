# SocialAI Service

🤖 AI驱动的社交媒体管理助手

## 项目概述

SocialAI Service是一个AI驱动的社交媒体管理平台，旨在帮助用户自动化内容生成、发布调度和数据分析。

## 核心功能 **多平台管理

-**: 微信服务号、LinkedIn（测试阶段）
- **AI内容生成**: 智能生成高质量内容
- **定时发布**: 预设时间自动发布
- **数据分析**: 全面的数据分析和报告

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python/FastAPI |
| AI | 集成多种语言模型 |
| 前端 | React.js + Ant Design |
| 数据库 | PostgreSQL |
| 缓存 | Redis |
| 部署 | Docker + Docker Compose |

## 快速开始

### 前置要求

- Docker >= 20.10
- Docker Compose >= 2.0
- PostgreSQL >= 14

### 启动服务

#### 方式 1：一键启动（推荐）

```bash
cd SocialAI-Service
./start-dev.sh
```

这会自动检查并启动所有服务：
- ✅ Celery Worker（处理定时发布任务）
- ✅ Celery Beat（定时调度器）
- ✅ FastAPI 后端
- ✅ Vite 前端

#### 方式 2：Docker Compose 启动

```bash
# 1. 克隆项目
git clone https://github.com/gefa-sc/SocialAI-Service.git
cd SocialAI-Service

# 2. 复制环境变量
cp api/.env.example api/.env

# 3. 启动开发环境（不含 Celery）
docker-compose -f docker-compose.dev.yml up -d

# 4. 单独启动 Celery（处理定时发布）
cd api
celery -A tasks.publish.celery_app worker --loglevel=info &
celery -A tasks.publish.celery_app beat --loglevel=info &
```

#### 方式 3：手动启动各服务

```bash
# 终端1: 启动后端
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 终端2: 启动前端
cd frontend
npm run dev

# 终端3: 启动 Celery Worker（处理发布任务）
cd api
celery -A tasks.publish.celery_app worker --loglevel=info

# 终端4: 启动 Celery Beat（定时调度）
cd api
celery -A tasks.publish.celery_app beat --loglevel=info
```

#### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

### 使用Makefile

```bash
make dev      # 启动开发环境
make down     # 停止服务
make logs     # 查看日志
make test     # 运行测试
```

## 项目结构

```
SocialAI-Service/
├── api/                    # 后端API
│   ├── main.py            # FastAPI入口
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── models/           # 数据模型
│   ├── routers/          # API路由
│   ├── tests/            # 单元测试
│   └── requirements.txt  # Python依赖
├── frontend/              # 前端项目
│   ├── src/              # 源代码
│   └── package.json      # Node依赖
├── docs/                  # 项目文档
│   ├── 01_INDEX.md       # 文档索引
│   ├── 11-15_xxx.md     # 阶段1: 项目启动
│   ├── 21-25_xxx.md     # 阶段2: 技术准备
│   ├── 31-33_xxx.md     # 阶段3: 产品开发
│   ├── 41-43_xxx.md     # 阶段4: 测试优化
│   └── 51-52_xxx.md     # 阶段5: 上线推广
├── docker-compose.dev.yml # 开发环境
├── docker-compose.prod.yml# 生产环境
└── Makefile              # 快速命令
```

## 测试

```bash
# 运行所有测试
cd api
DATABASE_URL="postgresql://socialai:password@localhost:5432/test_socialai" \
  python3 -m pytest tests/ -v

# 测试覆盖
- 单元测试: 57个
- 集成测试: 3个
- 通过率: 98.3%
```

## 相关文档

| 序号 | 文档 | 说明 |
|------|------|------|
| 01 | 文档索引 | 所有文档清单 |
| 11 | 商业分析报告 | 市场规模分析 |
| 12 | 商业需求文档(BRD) | 业务目标 |
| 13 | 市场需求文档(MRD) | 市场分析 |
| 15 | 竞品分析报告 | 竞争对比 |
| 21 | 技术架构 | 系统架构设计 |
| 24 | API接口文档 | 接口详细说明 |
| 31 | 产品需求文档(PRD) | 产品功能需求 |
| 41 | 测试用例 | 测试用例定义 |
| 43 | 阶段测试报告 | 测试结果汇总 |
| 51 | 用户使用手册 | 操作指南 |
| 52 | 产品部署手册 | 部署安装指南 |

完整文档列表见 [docs/01_INDEX.md](docs/01_INDEX.md)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

---

**当前版本**: V1.0 (MVP) — **平台已重启 (2026-04-29)**  
**GitHub**: https://github.com/gefa-sc/SocialAI-Service

### 平台状态 (2026-04-29)

| 服务 | 端口 | 状态 |
|------|------|------|
| 前端 | http://localhost:5173 | ✅ 运行中 |
| 后端 API | http://localhost:8000 | ✅ 运行中 |
| PostgreSQL | localhost:5432 | ✅ 运行中 |
| Redis | localhost:6379 | ✅ 运行中 |
| Celery Worker/Beat | - | ❌ 未启动 |

> ⚠️ 详细状态见 [docs/00_PLATFORM_STATUS.md](docs/00_PLATFORM_STATUS.md)
