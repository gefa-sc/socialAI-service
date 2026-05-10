# 微信 OAuth 集成指南

## 概述

本文档说明如何在 SocialAI Service 中集成微信公众号/企业微信 OAuth 认证。

## 前提条件

1. **微信开放平台账号**: https://open.weixin.qq.com
2. **已认证的微信小程序或公众号**
3. **已配置授权回调域名**

## 配置步骤

### 1. 获取微信开放平台配置

1. 登录 [微信开放平台](https://open.weixin.qq.com)
2. 创建应用或使用已有公众号/小程序
3. 获取以下信息：
   - `AppID` (应用ID)
   - `AppSecret` (应用密钥)

### 2. 配置授权回调域名

1. 在微信公众平台/开放平台设置中
2. 添加授权回调域名：`localhost:8000` (开发环境)
3. 生产环境需配置正式域名

### 3. 配置环境变量

编辑 `api/.env` 文件：

```bash
# 微信配置
WECHAT_APP_ID=your_actual_app_id
WECHAT_APP_SECRET=your_actual_app_secret
WECHAT_TOKEN=your_wechat_token
```

### 4. 配置前端回调地址

开发环境无需修改。

生产环境需修改 `api/routers/social_accounts.py` 中的回调地址：

```python
WECHAT_REDIRECT_URI = "https://your-domain.com/api/accounts/callback/wechat"
```

## OAuth 流程

```
用户点击"连接微信"
    ↓
前端调用 accountsAPI.getOAuthUrl('wechat')
    ↓
获取微信授权URL并返回给前端
    ↓
前端打开新窗口引导用户授权
    ↓
用户授权后微信重定向到回调地址
    ↓
后端接收code，换取access_token
    ↓
获取用户信息，保存到数据库
    ↓
前端轮询或手动刷新账户列表
```

## 测试方法

### 本地测试

1. 启动后端服务：`make dev` 或 `python -m uvicorn main:app`
2. 启动前端服务：`cd frontend && npm run dev`
3. 登录账号
4. 进入"社交账户"页面
5. 点击"连接账户"按钮
6. 选择"微信"平台
7. 完成授权流程

### 使用测试公众号

如果没有正式公众号，可以使用微信公众平台提供的测试账号：

1. 登录公众平台测试账号：https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login
2. 获取测试用的 AppID 和 AppSecret
3. 配置扫码关注测试账号
4. 使用测试账号进行 OAuth 测试

## 权限说明

| 权限 | 说明 | 适用场景 |
|------|------|----------|
| snsapi_base | 静默授权 | 仅获取用户openid |
| snsapi_userinfo | 需要用户确认 | 获取用户昵称、头像等 |

当前实现使用 `snsapi_base`，如需获取用户详细信息需改为 `snsapi_userinfo`。

## 常见问题

### 1. 授权失败提示 "redirect_uri 参数错误"

**原因**: 回调域名未在微信平台配置

**解决**: 
- 开发环境：在微信公众平台添加 `localhost` 到 JS安全域名和授权回调域名
- 生产环境：配置正式的域名

### 2. 授权成功但获取用户信息失败

**原因**: access_token 已过期或权限不足

**解决**: 检查 AppSecret 是否正确，确认应用权限

### 3. 前端无法打开授权页面

**原因**: 浏览器弹出窗口被拦截

**解决**: 提示用户允许弹出窗口

## LinkedIn OAuth

LinkedIn OAuth 配置类似，配置以下环境变量：

```bash
LINKEDIN_API_KEY=your_linkedin_client_id
LINKEDIN_API_SECRET=your_linkedin_client_secret
```

回调地址：`http://localhost:8000/api/accounts/callback/linkedin`

## 相关代码

- 后端实现：`api/routers/social_accounts.py`
- 前端UI：`frontend/src/pages/Accounts.jsx`
- API调用：`frontend/src/api/index.js` (accountsAPI)
