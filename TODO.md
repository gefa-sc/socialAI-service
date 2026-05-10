# SocialAI Service - 待办任务清单

最后更新: 2026-04-29

## 平台现状 (2026-04-29)

- **重启日期**: 2026-04-29（离线4周后恢复）
- **运行状态**: ✅ 后端+前端+数据库已启动
- **磁盘**: ⚠️ 94%紧张（~2.4GB可用）
- **待启动**: Celery Worker/Beat
- **待处理**: 微信OAuth域名风控、数据源接入方案

---

## 🔴 高优先级

### 微信/LinkedIn OAuth 集成
- [x] 后端OAuth框架实现
- [x] 前端连接账户UI
- [x] OAuth回调处理
- [x] 微信测试号配置
- [x] ngrok内网穿透配置
- [x] 域名验证文件部署
- [ ] **微信网页授权域名被风控，需使用已备案域名**

### AI 内容生成
- [x] MiniMax API 接入
- [x] 内容生成API开发
- [x] 提示词模板管理
- [x] 前端AI生成界面 ✅ 2026-02-19
- [x] 动态平台选项（根据已绑定账户）✅ 2026-02-19
- [x] 修复保存到内容库功能 ✅ 2026-02-19

### 定时发布
- [x] Redis 任务队列搭建 ✅ 2026-02-19
- [x] Celery 定时任务配置 ✅ 2026-02-19
- [x] 发布失败重试机制 ✅ 2026-02-19
- [ ] Celery Worker/Beat 启动（服务已重启，需手动启动）

### 基础设施
- [ ] 磁盘清理（/var/log/journal 占 2.6G）
- [ ] docker-compose 段错误问题排查

---

## 🟡 中优先级

### 用户体验优化
- [x] 加载状态优化 (骨架屏) ✅ 2026-02-19
- [x] 错误边界处理 ✅ 2026-02-19
- [x] 空状态提示 ✅ 2026-02-19
- [x] 修复前端组件导入错误 (Statistic) ✅ 2026-02-19
- [x] 修复调度列表/内容列表数据格式 ✅ 2026-02-19
- [x] 修复数据库 retry_count 字段 ✅ 2026-02-19
- [ ] 移动端响应式适配
- [ ] 主题切换功能

### 数据分析
- [x] 图表可视化完善 ✅ 2026-02-19
- [ ] 导出报告功能
- [ ] 数据实时更新
- [ ] 数据源接入（GA/Mixpanel/GrowingIO 待曹总决策）

### 测试覆盖
- [x] 后端单元测试补充 ✅ 2026-02-19 (现有65个测试)
- [x] 前端组件测试 ✅ 2026-02-19
- [ ] E2E测试用例

---

## 🟢 低优先级

### 生产部署
- [ ] Docker 镜像优化
- [ ] Nginx 配置
- [ ] SSL/HTTPS 配置
- [ ] 日志收集系统

### 新平台接入
- [ ] 钉钉机器人 ✅ 代码框架已完成
- [ ] 企业微信机器人 ✅ 代码框架已完成
- [ ] 微博开放平台（待申请）
- [ ] B站开放平台（待申请）
- [ ] 抖音开放平台（待申请）
- [ ] 快手开放平台（待申请）

### 功能扩展
- [ ] 多语言支持
- [ ] 团队协作功能
- [ ] Webhook 集成

---

## 🚀 V2.0 MVP 迭代计划（下一版）

### 热点资讯监控功能（已规划）

基于竞品分析，决定将**热点监控**作为V2.0的核心增值功能：

#### 功能规划
- [ ] 热点话题聚合（基于关键词/行业）
- [ ] 热度趋势图表
- [ ] AI内容推荐（根据热点生成内容）
- [ ] 一键生成+发布工作流

#### 技术调研
- [x] situation-monitor 项目分析 ✅ 2026-02-19
- [x] worldmonitor 竞品分析 ✅ 2026-02-19
- [ ] 新闻API调研（NewsAPI/GNews）
- [ ] 数据存储方案设计

#### 用户调研
- [ ] 目标用户需求访谈
- [ ] 付费意愿验证
- [ ] 功能优先级排序

---

## 📝 微信 OAuth 配置步骤

详细文档: `docs/WECHAT_OAUTH_SETUP.md`

### 当前问题

ngrok免费域名被微信风控，解决方案：

1. **方案A**：申请恢复访问（临时方案）
2. **方案B**：使用已备案域名（长期方案）
   - 购买中国大陆服务器
   - 提交备案申请（20个工作日）
   - 配置正式域名

### 相关文件

- `api/routers/social_accounts.py` - OAuth处理逻辑
- `frontend/src/pages/Accounts.jsx` - 连接界面
- `docs/WECHAT_OAUTH_SETUP.md` - 详细配置指南

---

## 📊 平台重启检查清单 (2026-04-29)

重启平台时的标准操作：

1. [x] Docker 服务启动
   ```bash
   docker start socialai-postgres-dev socialai-redis-dev
   ```
2. [x] 数据库初始化（role + database）
3. [x] 后端启动
   ```bash
   cd api && DATABASE_URL=... REDIS_URL=... python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. [x] 前端启动
   ```bash
   cd frontend && npm run dev
   ```
5. [ ] Celery Worker 启动（未执行）
   ```bash
   cd api && celery -A tasks.publish.celery_app worker --loglevel=info &
   ```
6. [ ] Celery Beat 启动（未执行）
   ```bash
   cd api && celery -A tasks.publish.celery_app beat --loglevel=info &
   ```
