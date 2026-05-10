# SocialAI Service - 后端API

## 项目结构
```
api/
├── main.py                 # FastAPI应用入口
├── config.py               # 配置管理
├── database.py             # 数据库连接
├── Dockerfile              # 生产环境镜像
├── Dockerfile.dev          # 开发环境镜像
├── .env.example            # 环境变量示例
├── models/                 # 数据模型
│   ├── __init__.py
│   └── models.py
├── routers/                # API路由
│   ├── __init__.py
│   ├── auth.py
│   ├── contents.py
│   ├── schedules.py
│   ├── analytics.py
│   └── social_accounts.py
├── services/               # 业务逻辑(待实现)
│   ├── auth_service.py
│   ├── content_generator.py
│   ├── scheduler_service.py
│   └── platform_service.py
└── requirements.txt        # Python依赖
```

## 快速开始

### 方式一：Docker开发环境（推荐）

```bash
# 1. 进入项目根目录
cd SocialAI-Service

# 2. 复制环境变量配置
cp api/.env.example api/.env
# 编辑 .env 填入配置

# 3. 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 4. 查看日志
docker-compose -f docker-compose.dev.yml logs -f api

# 5. 访问API
# API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式二：本地虚拟环境

```bash
# 1. 进入api目录
cd api

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 5. 运行服务器
uvicorn main:app --reload
```

## 使用Makefile命令

在项目根目录执行：

```bash
make dev      # 启动开发环境
make down     # 停止服务
make restart  # 重启服务
make logs     # 查看日志
make build    # 构建镜像
make clean    # 清理容器和数据
make db-reset # 重置数据库
```

## Docker服务说明

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| PostgreSQL | socialai-postgres-dev | 5432:5432 | 数据库 |
| Redis | socialai-redis-dev | 6379:6379 | 缓存/队列 |
| API | socialai-api-dev | 8000:8000 | FastAPI应用 |

## 环境变量

必需的环境变量（见 `.env.example`）:

```bash
# 数据库
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key

# OpenAI
OPENAI_API_KEY=your-api-key
```

## API端点

### 认证
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- POST /api/auth/refresh - 刷新令牌
- POST /api/auth/logout - 登出

### 社交账户
- GET /api/accounts - 获取用户账户列表
- POST /api/accounts/connect - 连接社交账户
- DELETE /api/accounts/{id} - 断开账户

### 内容管理
- GET /api/contents - 获取内容列表
- POST /api/contents - 创建内容
- PUT /api/contents/{id} - 更新内容
- DELETE /api/contents/{id} - 删除内容
- POST /api/contents/generate - AI生成内容

### 发布调度
- GET /api/schedules - 获取调度列表
- POST /api/schedules - 创建调度
- PUT /api/schedules/{id} - 更新调度
- DELETE /api/schedules/{id} - 删除调度

### 数据分析
- GET /api/analytics/overview - 概览数据
- GET /api/analytics/content/{id} - 内容效果分析
- GET /api/analytics/accounts - 账户表现分析