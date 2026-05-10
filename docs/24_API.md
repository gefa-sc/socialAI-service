# SocialAI Service - API接口文档

**文档版本**: V1.0  
**项目名称**: SocialAI Service  
**编制日期**: 2026-02-15  
**接口版本**: v1

---

## 目录

1. [概述](#1-概述)
2. [认证](#2-认证)
3. [用户接口](#3-用户接口)
4. [内容管理接口](#4-内容管理接口)
5. [社交账户接口](#5-社交账户接口)
6. [发布调度接口](#6-发布调度接口)
7. [数据分析接口](#7-数据分析接口)
8. [公共接口](#8-公共接口)
9. [错误代码](#9-错误代码)

---

## 1. 概述

### 1.1 API说明

- **Base URL**: `/api`
- **认证方式**: Bearer Token (JWT)
- **请求格式**: JSON
- **响应格式**: JSON

### 1.2 请求头

| Header | 说明 | 示例 |
|--------|------|------|
| Authorization | 访问令牌 | `Bearer {access_token}` |
| Content-Type | 请求内容类型 | `application/json` |

### 1.3 通用响应格式

```json
// 成功响应
{
  "code": 200,
  "message": "success",
  "data": {}
}

// 错误响应
{
  "code": 400,
  "message": "错误信息",
  "detail": "详细错误信息"
}
```

---

## 2. 认证

### 2.1 用户注册

**接口**: `POST /api/auth/register`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码（至少6位） |
| name | string | 否 | 用户名 |

**请求示例**:
```json
{
  "email": "user@example.com",
  "password": "123456",
  "name": "张三"
}
```

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "张三",
  "subscription_tier": "free"
}
```

---

### 2.2 用户登录

**接口**: `POST /api/auth/login`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 邮箱地址 |
| password | string | 是 | 密码 |

**请求示例**:
```
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=123456
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 2.3 获取当前用户信息

**接口**: `GET /api/auth/me`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "张三",
  "subscription_tier": "free"
}
```

---

## 3. 用户接口

### 3.1 获取用户资料

**接口**: `GET /api/users/profile`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "张三",
  "avatar_url": "https://example.com/avatar.jpg",
  "subscription_tier": "free",
  "subscription_status": "active",
  "created_at": "2026-02-14T10:00:00Z"
}
```

---

### 3.2 更新用户资料

**接口**: `PUT /api/users/profile`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 用户名 |
| avatar_url | string | 否 | 头像URL |

**请求示例**:
```json
{
  "name": "新名字",
  "avatar_url": "https://example.com/new_avatar.jpg"
}
```

---

### 3.3 修改密码

**接口**: `PUT /api/users/password`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 原密码 |
| new_password | string | 是 | 新密码 |

**请求示例**:
```json
{
  "old_password": "123456",
  "new_password": "654321"
}
```

---

## 4. 内容管理接口

### 4.1 获取内容列表

**接口**: `GET /api/contents`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | int | 否 | 跳过条数（默认0） |
| limit | int | 否 | 返回条数（默认100） |
| content_type | string | 否 | 内容类型筛选 |
| status | string | 否 | 状态筛选 |

**响应示例**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "测试文章",
    "body": "这是文章内容",
    "content_type": "article",
    "status": "draft",
    "created_at": "2026-02-14T10:00:00Z"
  }
]
```

---

### 4.2 创建内容

**接口**: `POST /api/contents`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 标题 |
| body | string | 是 | 正文内容 |
| content_type | string | 否 | 内容类型（article/tweet/post） |
| ai_prompt_used | string | 否 | AI生成时使用的提示词 |

**请求示例**:
```json
{
  "title": "春节促销文案",
  "body": "新年大促，全场5折！",
  "content_type": "tweet"
}
```

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "春节促销文案",
  "body": "新年大促，全场5折！",
  "content_type": "tweet",
  "status": "draft",
  "created_at": "2026-02-14T10:00:00Z"
}
```

---

### 4.3 获取内容详情

**接口**: `GET /api/contents/{content_id}`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "春节促销文案",
  "body": "新年大促，全场5折！",
  "content_type": "tweet",
  "status": "draft",
  "created_at": "2026-02-14T10:00:00Z",
  "updated_at": "2026-02-14T10:00:00Z"
}
```

---

### 4.4 更新内容

**接口**: `PUT /api/contents/{content_id}`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 标题 |
| body | string | 否 | 正文内容 |
| content_type | string | 否 | 内容类型 |
| status | string | 否 | 状态 |

**请求示例**:
```json
{
  "title": "更新的标题",
  "status": "published"
}
```

---

### 4.5 删除内容

**接口**: `DELETE /api/contents/{content_id}`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "message": "Content deleted successfully"
}
```

---

### 4.6 AI生成内容

**接口**: `POST /api/contents/ai-generate`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 生成提示词 |
| content_type | string | 否 | 内容类型 |

**请求示例**:
```json
{
  "prompt": "帮我写一篇关于春季新品上市的促销文案",
  "content_type": "article"
}
```

**响应示例**:
```json
{
  "title": "春季新品上市，全场8折优惠！",
  "body": "尊敬的顾客，春天来了，我们的新品也上市了...",
  "ai_generated": true
}
```

---

## 5. 社交账户接口

### 5.1 获取账户列表

**接口**: `GET /api/accounts`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | string | 否 | 平台筛选（wechat/linkedin） |
| is_active | bool | 否 | 激活状态筛选 |

**响应示例**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "platform": "wechat",
    "account_name": "我的微信公众号",
    "is_active": true,
    "created_at": "2026-02-14T10:00:00Z"
  }
]
```

---

### 5.2 获取OAuth授权URL

**接口**: `GET /api/accounts/oauth/{platform}`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 说明 |
|------|------|
| platform | 平台类型（wechat/linkedin） |

**响应示例**:
```json
{
  "url": "https://open.weixin.qq.com/connect/oauth2/authorize?...",
  "state": "random_state_string"
}
```

---

### 5.3 连接社交账户

**接口**: `POST /api/accounts/connect`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | string | 是 | 平台类型 |
| code | string | 是 | OAuth授权码 |

**请求示例**:
```json
{
  "platform": "wechat",
  "code": "微信授权码"
}
```

---

### 5.4 获取账户详情

**接口**: `GET /api/accounts/{account_id}`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "platform": "wechat",
  "account_name": "我的微信公众号",
  "is_active": true,
  "created_at": "2026-02-14T10:00:00Z"
}
```

---

### 5.5 断开社交账户

**接口**: `DELETE /api/accounts/{account_id}`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "message": "wechat 账户已断开连接"
}
```

---

### 5.6 刷新账户Token

**接口**: `POST /api/accounts/{account_id}/refresh`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "message": "Token刷新成功"
}
```

---

### 5.7 测试账户连接

**接口**: `GET /api/accounts/{account_id}/test`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440002",
  "platform": "wechat",
  "is_connected": true,
  "account_name": "我的微信公众号"
}
```

---

## 6. 发布调度接口

### 6.1 获取调度列表

**接口**: `GET /api/schedules`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | int | 否 | 跳过条数 |
| limit | int | 否 | 返回条数 |
| status | string | 否 | 状态筛选 |

**响应示例**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "content_id": "550e8400-e29b-41d4-a716-446655440001",
    "content_title": "春节促销文案",
    "social_account_id": "550e8400-e29b-41d4-a716-446655440002",
    "platform": "wechat",
    "scheduled_at": "2026-02-15T10:00:00Z",
    "status": "pending"
  }
]
```

---

### 6.2 创建调度

**接口**: `POST /api/schedules`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content_id | string | 是 | 内容ID |
| social_account_id | string | 是 | 社交账户ID |
| scheduled_at | string | 是 | 计划发布时间（ISO8601格式） |

**请求示例**:
```json
{
  "content_id": "550e8400-e29b-41d4-a716-446655440001",
  "social_account_id": "550e8400-e29b-41d4-a716-446655440002",
  "scheduled_at": "2026-02-15T14:00:00Z"
}
```

---

### 6.3 获取调度详情

**接口**: `GET /api/schedules/{schedule_id}`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "content_id": "550e8400-e29b-41d4-a716-446655440001",
  "content_title": "春节促销文案",
  "social_account_id": "550e8400-e29b-41d4-a716-446655440002",
  "platform": "wechat",
  "scheduled_at": "2026-02-15T10:00:00Z",
  "status": "pending"
}
```

---

### 6.4 更新调度

**接口**: `PUT /api/schedules/{schedule_id}`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scheduled_at | string | 否 | 新的计划发布时间 |
| status | string | 否 | 状态 |

---

### 6.5 取消调度

**接口**: `DELETE /api/schedules/{schedule_id}`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "message": "Schedule cancelled successfully"
}
```

---

### 6.6 获取最佳发布时间

**接口**: `GET /api/schedules/recommended-time`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | string | 是 | 平台类型 |

**响应示例**:
```json
{
  "platform": "wechat",
  "recommended_times": [
    "2026-02-15T09:00:00Z",
    "2026-02-15T12:00:00Z",
    "2026-02-15T18:00:00Z"
  ]
}
```

---

## 7. 数据分析接口

### 7.1 获取数据概览

**接口**: `GET /api/analytics/overview`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| days | int | 否 | 查询天数（默认7） |

**响应示例**:
```json
{
  "total_posts": 156,
  "ai_generated_posts": 89,
  "total_impressions": 23456,
  "total_engagements": 1234,
  "active_users": 45,
  "period_comparison": {
    "posts_change": 12,
    "impressions_change": 8.5,
    "engagements_change": 15.2
  }
}
```

---

### 7.2 获取趋势数据

**接口**: `GET /api/analytics/trends`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| metric | string | 否 | 指标类型（impressions/engagements/posts） |
| days | int | 否 | 查询天数（默认30） |

**响应示例**:
```json
{
  "metric": "impressions",
  "data": [
    {"date": "2026-02-01", "value": 1200},
    {"date": "2026-02-02", "value": 1350},
    {"date": "2026-02-03", "value": 1100}
  ]
}
```

---

### 7.3 获取内容效果数据

**接口**: `GET /api/analytics/content/{content_id}`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "content_id": "550e8400-e29b-41d4-a716-446655440001",
  "impressions": 5234,
  "likes": 234,
  "comments": 56,
  "shares": 78,
  "clicks": 123,
  "engagement_rate": 7.2
}
```

---

### 7.4 获取平台对比数据

**接口**: `GET /api/analytics/platform-comparison`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "platforms": [
    {
      "name": "wechat",
      "posts": 100,
      "impressions": 15000,
      "engagements": 800
    },
    {
      "name": "linkedin",
      "posts": 56,
      "impressions": 8456,
      "engagements": 434
    }
  ]
}
```

---

### 7.5 生成数据报告

**接口**: `POST /api/analytics/report`

**请求头**: `Authorization: Bearer {token}`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | 是 | 开始日期 |
| end_date | string | 是 | 结束日期 |
| format | string | 否 | 报告格式（json/excel/pdf） |

**请求示例**:
```json
{
  "start_date": "2026-01-01",
  "end_date": "2026-01-31",
  "format": "excel"
}
```

**响应示例**:
```json
{
  "report_url": "https://example.com/reports/202601.xlsx"
}
```

---

## 8. 公共接口

### 8.1 健康检查

**接口**: `GET /api/health`

**响应示例**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### 8.2 获取系统配置

**接口**: `GET /api/config`

**响应示例**:
```json
{
  "supported_platforms": ["wechat", "linkedin"],
  "max_content_length": 10000,
  "subscription_tiers": ["free", "professional", "enterprise"]
}
```

---

## 9. 错误代码

| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 200 | success | 成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或Token无效 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 422 | Validation Error | 数据验证失败 |
| 429 | Too Many Requests | 请求频率超限 |
| 500 | Internal Server Error | 服务器内部错误 |

### 错误响应示例

```json
{
  "code": 401,
  "detail": "Could not validate credentials"
}
```

---

**文档结束**

*本API接口文档定义了SocialAI Service的所有接口规范，是前后端开发和第三方集成的重要参考文档。*
