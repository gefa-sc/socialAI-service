# 微信OAuth集成配置指南

## 概述

本文档记录 SocialAI Service 项目中集成微信OAuth网页授权的配置流程。

---

## 一、配置前准备

### 1.1 所需账号
- 微信公众平台测试号：https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login

### 1.2 所需工具
- ngrok 内网穿透（免费版）
- 代码运行服务器（本地或云服务器）

---

## 二、配置步骤

### 2.1 启动后端服务

```bash
cd /home/gefa/.openclaw/workspace/SocialAI-Service/api
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2.2 启动ngrok

```bash
ngrok http 8000
```

获取公网URL：`https://xxx.ngrok-free.dev`

### 2.3 配置环境变量

编辑 `api/.env`：

```bash
# 微信测试号配置
WECHAT_APP_ID=wxf37bcf043708a278
WECHAT_APP_SECRET=c107f614f1daebc9ed7a547811e27087
```

### 2.4 修改代码配置

编辑 `api/routers/social_accounts.py`：

```python
from config import settings

WECHAT_APP_ID = settings.WECHAT_APP_ID or "your_app_id"
WECHAT_APP_SECRET = settings.WECHAT_APP_SECRET or "your_app_secret"
WECHAT_REDIRECT_URI = "https://你的ngrok域名/api/accounts/callback/wechat"
```

### 2.5 添加验证接口

在 `api/main.py` 中添加微信域名验证接口：

```python
# 微信域名验证文件
@app.get("/MP_verify_4eqvvZHaC5df9Ana.txt")
async def wechat_verify_file():
    return PlainTextResponse(content="4eqvvZHaC5df9Ana")

@app.get("/88e3cdc1664ea9c3f26b9ec1c6c940c3.txt")
async def wechat_verify_file2():
    return PlainTextResponse(content="8699186fc2480cff55eb81f081d384129bd34140")
```

### 2.6 微信后台配置

1. 登录微信公众平台测试号
2. **接口配置信息**（可选，用于消息推送）：
   - URL: `https://你的域名/api/accounts/callback/wechat`
   - Token: `wechat_token`

3. **接口安全域名**：
   - 添加你的ngrok域名

4. **网页授权域名**：
   - 添加你的ngrok域名
   - 需要验证域名所有权（部署验证文件）

---

## 三、OAuth流程测试

### 3.1 获取授权链接

```bash
# 登录获取token
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=test4@example.com&password=test123456"

# 获取OAuth URL
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/accounts/oauth/wechat
```

### 3.2 用户授权

1. 在手机微信中打开返回的OAuth链接
2. 用户同意授权
3. 微信会回调到 `redirect_uri`，携带code参数
4. 后端使用code换取用户信息

---

## 四、常见问题

### 4.1 URL格式不合法

**问题**：接口配置信息提示"URL格式不合法"

**解决**：微信要求URL必须是公网域名，localhost不支持。需使用ngrok等内网穿透工具。

### 4.2 redirect_uri域名与后台配置不一致 (错误码10003)

**问题**：网页授权提示域名不一致

**解决**：
1. 确保"网页授权域名"已配置
2. 确保OAuth链接中的redirect_uri与配置的域名一致

### 4.3 域名存在安全风险

**问题**：ngrok免费域名被微信风控

**解决**：
1. 申请恢复访问（填写申请理由）
2. 或使用已备案的正式域名

### 4.4 验证文件部署

微信会要求部署验证文件以证明域名所有权：
- 在API中添加对应的验证接口
- 确保可通过 `https://域名/验证文件名.txt` 访问

---

## 五、正式备案域名

### 5.1 备案要求

| 要求 | 说明 |
|------|------|
| 服务器 | 必须中国大陆（阿里云、腾讯云等） |
| 域名 | 已完成实名认证 |
| 审核时间 | 约20个工作日 |

### 5.2 备案流程

1. 购买中国大陆服务器
2. 在服务器提供商提交备案申请
3. 填写网站信息
4. 等待审核（需配合电话验证）
5. 审核通过后配置域名解析

---

## 六、代码文件清单

| 文件 | 说明 |
|------|------|
| `api/.env` | 环境变量配置 |
| `api/main.py` | 主入口，验证接口 |
| `api/routers/social_accounts.py` | OAuth处理逻辑 |
| `api/config.py` | 配置管理 |
| `frontend/src/pages/Accounts.jsx` | 前端账户页面 |

---

## 七、相关链接

- 微信公众平台：https://mp.weixin.qq.com/
- 微信开放文档：https://developers.weixin.qq.com/doc/
- ngrok：https://ngrok.com/
- 阿里云备案：https://beian.aliyun.com/
- 腾讯云备案：https://cloud.tencent.com/product/ba

---

## 八、注意事项

1. **ngrok免费域名限制**：免费域名可能被微信风控，付费版有更好体验
2. **测试号权限**：测试号部分接口权限受限
3. **Token安全**：微信access_token必须保存在服务端，不可暴露
4. **域名有效性**：每次ngrok重启会改变域名，需更新配置

---

最后更新：2026-02-18
