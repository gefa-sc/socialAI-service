# SocialAI Service - 开发手册

**项目**: SocialAI Service  
**版本**: V1.0  
**编制日期**: 2026-02-14  
**目标**: 12个月内MRR达到$50,000

---

## 目录

1. [环境准备阶段](#1-环境准备阶段)
2. [开发阶段](#2-开发阶段)
3. [测试阶段](#3-测试阶段)
4. [部署阶段](#4-部署阶段)
5. [日常维护](#5-日常维护)

---

## 1. 环境准备阶段

### 1.1 安装开发工具

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 1.1.1 | 安装代码编辑器 | 1. 下载VS Code: https://code.visualstudio.com/<br>2. 运行安装包并完成安装<br>3. 打开VS Code安装必要插件 | 推荐安装: Python, Docker, ESLint, Prettier |
| 1.1.2 | 安装Git | 1. Ubuntu: `sudo apt install git`<br>2. macOS: `brew install git`<br>3. Windows: 下载Git for Windows | 配置SSH Key以便推送代码 |
| 1.1.3 | 安装Docker | 1. Ubuntu: `curl -fsSL https://get.docker.com \| sh`<br>2. 启动: `sudo systemctl start docker`<br>3. 自启: `sudo systemctl enable docker`<br>4. 添加用户组: `sudo usermod -aG docker $USER` | 需要注销后生效；生产环境建议使用Docker Engine而非Docker Desktop |
| 1.1.4 | 安装Docker Compose | 1. 大多数Docker已自带<br>2. 验证: `docker-compose --version`<br>3. 如需单独安装: `sudo apt install docker-compose` | 确保版本 >= 2.0 |
| 1.1.5 | 安装Node.js(前端开发) | 1. 使用nvm管理: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh \| bash`<br>2. 安装LTS版本: `nvm install --lts` | 前端开发需要，MVP阶段可延后 |

### 1.2 克隆项目仓库

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 1.2.1 | 创建工作目录 | 1. 打开终端<br>2. 创建目录: `mkdir -p ~/projects`<br>3. 进入目录: `cd ~/projects` | 建议使用统一的开发目录 |
| 1.2.2 | 克隆代码仓库 | 1. 如果有Git仓库: `git clone <repository-url> SocialAI-Service`<br>2. 如果是本地创建: 将SocialAI-Service文件夹拷贝到工作目录 | 当前为本地开发，暂无远程仓库 |
| 1.2.3 | 验证项目结构 | 1. 进入项目目录: `cd SocialAI-Service`<br>2. 列出文件: `ls -la` | 确认看到 README.md, api/, docs/ 等目录 |

### 1.3 配置开发环境

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 1.3.1 | 复制环境变量配置 | 1. 进入api目录: `cd api`<br>2. 复制模板: `cp .env.example .env`<br>3. 编辑配置: `nano .env` 或用VS Code打开编辑 | ⚠️ 敏感信息勿提交到版本控制 |
| 1.3.2 | 配置数据库连接 | 编辑.env文件中的DATABASE_URL:<br>`DATABASE_URL=postgresql://socialai:密码@localhost:5432/socialai_dev` | 开发环境可使用弱密码，生产环境必须使用强密码 |
| 1.3.3 | 配置API密钥 | 1. MiniMax: 申请API Key并填入<br>2. 微信: 申请公众号/企业微信获取AppID<br>3. LinkedIn: 申请开发者账号获取API Key | ⚠️ API密钥需要付费或申请开发者账号 |

---

## 2. 开发阶段

### 2.1 启动开发环境

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 2.1.1 | 启动Docker服务 | 1. 确保Docker运行: `sudo systemctl start docker`<br>2. 验证: `docker ps` | 如果启动失败，检查Docker daemon是否正常运行 |
| 2.1.2 | 启动开发容器 | 1. 进入项目目录: `cd SocialAI-Service`<br>2. 启动服务: `docker-compose -f docker-compose.dev.yml up -d`<br>3. 或者用Makefile: `make dev` | 首次启动需要下载镜像，约5-10分钟 |
| 2.1.3 | 验证服务状态 | 1. 查看运行中的容器: `docker ps`<br>2. 检查API: `curl http://localhost:8000/health`<br>3. 查看API文档: 浏览器访问 http://localhost:8000/docs | 应该返回 {"status":"healthy"} |
| 2.1.4 | 查看日志 | 1. 查看所有日志: `make logs`<br>2. 查看API日志: `docker-compose -f docker-compose.dev.yml logs -f api` | 日志中红色输出不一定表示错误，可能是警告 |

### 2.2 后端开发

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 2.2.1 | 进入API容器 | 1. `docker-compose -f docker-compose.dev.yml exec api /bin/bash`<br>2. 或者: `make shell` | 容器内已配置好Python环境 |
| 2.2.2 | 安装Python依赖 | 1. 容器内执行: `pip install -r requirements.txt`<br>2. Docker方式: 依赖已在镜像中安装 | 如添加新依赖，需要重新构建: `make build` |
| 2.2.3 | 运行数据库迁移 | 1. 容器内: `alembic upgrade head`<br>2. 或者: 修改models后重新创建表 | 开发阶段可删除容器重建数据库 |
| 2.2.4 | 测试API端点 | 1. 浏览器打开: http://localhost:8000/docs<br>2. 使用Swagger UI测试各接口 | 或使用Postman/curl测试 |
| 2.2.5 | 常用开发命令 | 容器内:<br>- 运行服务器: `uvicorn main:app --reload`<br>- 运行测试: `pytest`<br>- 代码检查: `flake8 .` | 修改代码后自动重载生效 |

### 2.3 前端开发

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 2.3.1 | 初始化前端项目 | 1. 创建目录: `mkdir -p frontend && cd frontend`<br>2. 使用Vite创建: `npm create vite@latest . -- --template react`<br>3. 安装依赖: `npm install` | 可选择Vue或React框架 |
| 2.3.2 | 安装UI组件库 | 1. 安装Ant Design: `npm install antd`<br>2. 或安装MUI: `npm install @mui/material @emotion/react @emotion/styled` | 选择一个UI库并统一使用 |
| 2.3.3 | 配置代理 | 在vite.config.js中配置代理指向后端API:<br>```js<br>server: {<br>  proxy: {<br>    '/api': 'http://localhost:8000'<br>  }<br>}<br>``` | 解决跨域问题 |
| 2.3.4 | 启动前端开发服务器 | 1. `npm run dev`<br>2. 浏览器访问: http://localhost:5173 | 热重载已配置 |

### 2.4 代码管理

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 2.4.1 | 初始化Git仓库(首次) | 1. `git init`<br>2. 创建.gitignore文件<br>3. 首次提交: `git add . && git commit -m "Initial commit"` | .gitignore需排除: node_modules/, venv/, .env, __pycache__/ |
| 2.4.2 | 创建功能分支 | 1. 创建: `git checkout -b feature/功能名称`<br>2. 切换: `git checkout main` | 分支命名规范: feature/, bugfix/, hotfix/ |
| 2.4.3 | 提交代码 | 1. 查看状态: `git status`<br>2. 添加文件: `git add 文件名` 或 `git add .`<br>3. 提交: `git commit -m "描述"` | 提交信息要清晰描述改动 |
| 2.4.4 | 推送代码 | 1. 首次推送: `git push -u origin main`<br>2. 后续: `git push` | 需要先在Git平台创建远程仓库 |

---

## 3. 测试阶段

### 3.1 单元测试

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 3.1.1 | 运行后端测试 | 1. 进入容器: `make shell`<br>2. 执行: `pytest -v` | 确保测试覆盖核心业务逻辑 |
| 3.1.2 | 运行前端测试 | 1. `npm test`<br>2. 或: `npm run test:coverage` | 查看测试覆盖率报告 |
| 3.1.3 | 添加新测试 | 后端: 在tests/目录下创建test_*.py文件<br>前端: 在src/__tests__/目录下创建*.test.js | 测试文件命名规范: test_*.py, *.test.js |

### 3.2 集成测试

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 3.2.1 | API集成测试 | 1. 启动完整开发环境<br>2. 使用Postman测试完整业务流程<br>3. 测试用户注册 → 创建内容 → 调度发布流程 | 准备测试数据 |
| 3.2.2 | 前后端集成测试 | 1. 启动前后端服务<br>2. 在前端进行实际用户操作<br>3. 验证数据流转正确 | 检查Network面板确认API调用正常 |

### 3.3 验收测试

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 3.3.1 | 功能验收 | 1. 对照MVP功能清单<br>2. 逐项测试每个功能<br>3. 记录测试结果 | 见MVP_DOCS.md |
| 3.3.2 | 用户体验测试 | 1. 请目标用户试用<br>2. 收集反馈<br>3. 优化用户体验 | 提前准备测试账号 |

---

## 4. 部署阶段

### 4.1 生产环境准备

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 4.1.1 | 配置生产环境变量 | 1. 复制配置: `cp api/.env.example api/.env.production`<br>2. 编辑生产配置<br>3. ⚠️ 使用强密码和安全的SECRET_KEY | 生产环境变量不要存储在代码仓库 |
| 4.1.2 | 申请域名(可选) | 1. 购买域名<br>2. 配置DNS解析<br>3. 申请SSL证书(推荐Let's Encrypt免费) | 可先使用IP+端口测试 |
| 4.1.3 | 配置云服务器 | 1. 选择云服务商(阿里云/腾讯云/AWS)<br>2. 创建服务器实例<br>3. 配置安全组(开放80, 443, 22端口) | 开发阶段可用最低配置 |

### 4.2 部署实施

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 4.2.1 | 构建生产镜像 | 1. 进入项目目录<br>2. 执行: `docker-compose -f docker-compose.prod.yml build` | 首次构建约10分钟 |
| 4.2.2 | 启动生产服务 | 1. `docker-compose -f docker-compose.prod.yml up -d`<br>2. 检查状态: `docker ps` | 先在测试环境验证 |
| 4.2.3 | 配置Nginx(可选) | 1. 编辑nginx/nginx.conf<br>2. 配置SSL证书<br>3. 重载: `docker-compose exec nginx nginx -s reload` | 处理HTTPS和负载均衡 |
| 4.2.4 | 验证部署 | 1. 访问: http://your-domain.com<br>2. 测试核心功能<br>3. 检查日志: `make prod-logs` | 确保所有功能正常 |

### 4.3 持续部署(CI/CD)

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 4.3.1 | 配置GitHub Actions | 1. 创建.github/workflows/deploy.yml<br>2. 配置自动化部署<br>3. 添加Secrets | 自动化部署需谨慎测试 |
| 4.3.2 | 配置自动备份 | 1. 定期备份数据库<br>2. 备份配置文件<br>3. 存储到云存储 | 至少每周备份一次 |

---

## 5. 日常维护

### 5.1 日常开发流程

| 序号 | 操作环节 | 操作步骤 | 注意事项 |
|------|---------|---------|---------|
| 5.1.1 | 每日启动 | 1. 启动Docker: `sudo systemctl start docker`<br>2. 启动开发环境: `make dev`<br>3. 确认服务运行: `docker ps` | 形成固定开发习惯 |
| 5.1.2 | 每日工作 | 1. 创建/切换分支<br>2. 开发功能<br>3. 编写测试<br>4. 提交代码 | 保持小步提交 |
| 5.1.3 | 每日结束 | 1. 提交未完成的代码<br>2. 推送代码<br>3. 停止开发容器: `make down`(可选) | 养成提交习惯 |

### 5.2 常见问题处理

| 问题 | 解决方案 |
|------|---------|
| Docker容器启动失败 | 1. 检查端口占用: `netstat -tlnp`<br>2. 查看日志: `docker-compose logs` |
| 数据库连接失败 | 1. 检查PostgreSQL容器: `docker ps`<br>2. 重启数据库: `docker-compose restart postgres` |
| API返回500错误 | 1. 查看API日志: `docker-compose logs api`<br>2. 检查.env配置 |
| 前端无法连接API | 1. 检查代理配置<br>2. 检查后端是否运行<br>3. 检查跨域设置 |
| 依赖安装失败 | 1. 清理缓存: `docker-compose build --no-cache`<br>2. 检查网络连接 |

---

## 附录

### 常用命令速查表

```bash
# Docker开发环境
make dev          # 启动开发环境
make down         # 停止服务
make restart      # 重启服务
make logs         # 查看日志
make build        # 构建镜像
make clean        # 清理容器和数据
make db-reset     # 重置数据库

# Git操作
git status        # 查看状态
git add .         # 添加所有文件
git commit -m "" # 提交
git push          # 推送到远程
git pull          # 拉取代码
git checkout -b  # 创建并切换分支

# Docker手动操作
docker ps                    # 查看运行中的容器
docker-compose logs -f       # 查看日志
docker-compose exec api /bin/bash  # 进入容器
docker-compose down -v      # 清理所有数据

# 测试
pytest                      # 运行后端测试
npm test                    # 运行前端测试
```

### 环境变量清单

| 变量名 | 必需 | 说明 | 示例值 |
|--------|------|------|--------|
| ENVIRONMENT | 是 | 环境类型 | development/production |
| DATABASE_URL | 是 | PostgreSQL连接字符串 | postgresql://user:pass@host:5432/db |
| REDIS_URL | 是 | Redis连接字符串 | redis://localhost:6379 |
| SECRET_KEY | 是 | JWT签名密钥 | (32位以上随机字符串) |
| OPENAI_API_KEY | 否(已替换) | OpenAI API密钥 | sk-... |
| MINIMAX_API_KEY | 是(MVP) | MiniMax API密钥 | ... |
| MINIMAX_MODEL | 是(MVP) | MiniMax模型名称 | MiniMax-M2.5 |
| WECHAT_APP_ID | 是(MVP) | 微信AppID | wx... |
| WECHAT_APP_SECRET | 是(MVP) | 微信AppSecret | ... |
| WECHAT_TOKEN | 是(MVP) | 微信Token | ... |
| LINKEDIN_API_KEY | 是(MVP) | LinkedIn API Key | ... |
| LINKEDIN_API_SECRET | 是(MVP) | LinkedIn API Secret | ... |
| TWITTER_API_KEY | 否(后续扩展) | Twitter API Key | ... |
| TWITTER_API_SECRET | 否(后续扩展) | Twitter API Secret | ... |

---

**手册版本**: 1.0  
**最后更新**: 2026-02-14
