# SocialAI Service - 产品部署手册

**文档版本**: V1.0  
**产品名称**: SocialAI Service  
**编制日期**: 2026-02-15

---

## 目录

1. [部署概述](#1-部署概述)
2. [环境要求](#2-环境要求)
3. [部署架构](#3-部署架构)
4. [快速部署](#4-快速部署)
5. [Docker部署](#5-docker部署)
6. [手动部署](#6-手动部署)
7. [配置说明](#7-配置说明)
8. [验证部署](#8-验证部署)
9. [运维监控](#9-运维监控)
10. [故障排除](#10-故障排除)

---

## 1. 部署概述

### 1.1 部署模式

| 模式 | 适用场景 | 复杂度 |
|------|---------|--------|
| Docker | 生产环境 | 中 |
| 手动部署 | 开发/测试 | 低 |
| Kubernetes | 大规模 | 高 |

### 1.2 部署流程

```
1. 环境准备 → 2. 资源配置 → 3. 部署实施 → 4. 验证测试 → 5. 上线
```

---

## 2. 环境要求

### 2.1 硬件要求

| 规模 | CPU | 内存 | 磁盘 | 带宽 |
|------|-----|------|------|------|
| 开发 | 1核 | 2GB | 20GB | 5Mbps |
| 测试 | 2核 | 4GB | 50GB | 10Mbps |
| 生产 | 4核+ | 8GB+ | 100GB+ | 20Mbps |

### 2.2 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| 操作系统 | Ubuntu 20.04+ / CentOS 8+ | 推荐 Ubuntu |
| Docker | 20.10+ | 容器引擎 |
| Docker Compose | 2.0+ | 编排工具 |
| PostgreSQL | 14+ | 数据库 |
| Redis | 6.0+ | 缓存(可选) |
| Nginx | 1.18+ | 反向代理 |

---

## 3. 部署架构

### 3.1 系统架构

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (端口 80)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌────▼────┐ ┌────▼─────┐
        │  Web UI   │ │ API服务  │ │  Worker  │
        │  (5173)   │ │ (8000)   │ │ (后台任务)│
        └───────────┘ └─────────┘ └──────────┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │ PostgreSQL  │
                    │  (5432)     │
                    └─────────────┘
```

### 3.2 端口规划

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx | 80 | HTTP入口 |
| Nginx | 443 | HTTPS(可选) |
| API | 8000 | 后端接口 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存(可选) |

---

## 4. 快速部署

### 4.1 一键部署脚本

```bash
# 克隆项目
git clone https://github.com/gefa-sc/SocialAI-Service.git
cd SocialAI-Service

# 运行部署脚本
chmod +x deploy.sh
./deploy.sh
```

### 4.2 Docker Compose 部署

```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 5. Docker部署

### 5.1 环境变量

创建 `.env` 文件：

```bash
# 数据库
DATABASE_URL=postgresql://user:password@db:5432/socialai
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=socialai

# 应用
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 微信API (生产环境使用真实值)
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
```

### 5.2 Docker Compose 配置

```yaml
version: '3.8'

services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    restart: unless-stopped

  web:
    build: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - api
    restart: unless-stopped

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    restart: unless-stopped

volumes:
  postgres_data:
```

### 5.3 构建和启动

```bash
# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 初始化数据库
docker-compose exec api python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# 查看状态
docker-compose ps
```

---

## 6. 手动部署

### 6.1 后端部署

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
cd api
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 4. 初始化数据库
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# 5. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6.2 前端部署

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 配置环境
cp .env.example .env
# 编辑 .env 文件

# 3. 构建
npm run build

# 4. 使用Nginx部署
# 配置 nginx.conf
sudo cp nginx.conf /etc/nginx/sites-available/socialai
sudo nginx -t
sudo systemctl reload nginx
```

---

## 7. 配置说明

### 7.1 关键配置项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| DATABASE_URL | 数据库连接串 | postgresql://... |
| SECRET_KEY | JWT密钥 | random-string |
| WECHAT_APP_ID | 微信AppID | wx123456789 |
| WECHAT_APP_SECRET | 微信密钥 | abcdefghijk |
| REDIS_URL | Redis连接 | redis://localhost:6379 |

### 7.2 安全配置

```bash
# 生成密钥
python3 -c "import secrets; print(secrets.token_hex(32))"

# 设置文件权限
chmod 600 .env
```

---

## 8. 验证部署

### 8.1 API验证

```bash
# 健康检查
curl http://localhost:8000/health

# 预期响应
{"status":"healthy"}

# 用户注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456","name":"Test"}'
```

### 8.2 前端验证

```bash
# 访问 http://your-server-ip
# 预期: 看到登录页面
```

### 8.3 自动化验证脚本

```bash
./scripts/verify-deployment.sh
```

---

## 9. 运维监控

### 9.1 日志管理

```bash
# 查看API日志
docker-compose logs -f api

# 查看所有日志
docker-compose logs -f
```

### 9.2 监控指标

| 指标 | 阈值 | 告警 |
|------|------|------|
| CPU使用率 | >80% | ⚠️ |
| 内存使用率 | >85% | ⚠️ |
| 磁盘使用率 | >90% | ⚠️ |
| API响应时间 | >2s | ⚠️ |
| 错误率 | >1% | ⚠️ |

### 9.3 备份策略

```bash
# 数据库备份
docker-compose exec db pg_dump -U user socialai > backup_$(date +%Y%m%d).sql

# 定时备份 (crontab)
0 2 * * * /path/to/backup.sh
```

---

## 10. 故障排除

### 10.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 502 Bad Gateway | 服务未启动 | 检查docker-compose ps |
| 数据库连接失败 | 配置错误 | 检查DATABASE_URL |
| 静态资源404 | 构建问题 | 重新npm run build |
| 内存不足 | 资源限制 | 调整docker内存 |

### 10.2 紧急回滚

```bash
# 回滚到上一个版本
git revert HEAD
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

## 附录

### 附录A: 部署检查清单

- [ ] 服务器环境准备完成
- [ ] 域名解析配置
- [ ] SSL证书配置(可选)
- [ ] 防火墙端口开放
- [ ] 数据库初始化
- [ ] 管理员账户创建
- [ ] 第三方API配置
- [ ] 监控告警配置
- [ ] 备份策略配置
- [ ] 部署验证通过

---

**编制**: SocialAI Team  
**审核**: -  
**发布日期**: 2026-02-15

---

**文档结束**
