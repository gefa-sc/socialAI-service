# SocialAI Service - 数据字典

**文档版本**: V1.0  
**项目名称**: SocialAI Service  
**编制日期**: 2026-02-15  
**数据库**: PostgreSQL

---

## 目录

1. [概述](#1-概述)
2. [用户表 (users)](#2-用户表-users)
3. [社交账户表 (social_accounts)](#3-社交账户表-social_accounts)
4. [内容表 (contents)](#4-内容表-contents)
5. [调度表 (schedules)](#5-调度表-schedules)
6. [分析表 (analytics)](#6-分析表-analytics)
7. [枚举值定义](#7-枚举值定义)
8. [ER图](#8-er图)

---

## 1. 概述

### 1.1 数据库信息

| 属性 | 值 |
|------|------|
| 数据库类型 | PostgreSQL |
| 数据库版本 | 15+ |
| 字符集 | UTF-8 |
| 存储引擎 | InnoDB |

### 1.2 数据表清单

| 表名 | 说明 | 记录数（预估） |
|------|------|----------------|
| users | 用户表 | 1000+ |
| social_accounts | 社交账户表 | 5000+ |
| contents | 内容表 | 50000+ |
| schedules | 调度表 | 100000+ |
| analytics | 分析数据表 | 200000+ |

---

## 2. 用户表 (users)

### 2.1 表结构

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PK | 用户ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱地址 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| name | VARCHAR(100) | NULL | 用户昵称 |
| avatar_url | TEXT | NULL | 头像URL |
| subscription_tier | VARCHAR(20) | DEFAULT 'free' | 订阅等级 |
| subscription_status | VARCHAR(20) | DEFAULT 'active' | 订阅状态 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

### 2.2 字段详细说明

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | UUID | 主键，使用UUID生成策略，格式：550e8400-e29b-41d4-a716-446655440000 |
| email | VARCHAR(255) | 用户邮箱，用于登录验证，必须唯一 |
| password_hash | VARCHAR(255) | 使用bcrypt加密存储的密码哈希 |
| naNot Just AIme | VARCHAR(100) | 用户显示名称，可选 |
| avatar_url | TEXT | 用户头像URL，支持外部图片链接 |
| subscription_tier | VARCHAR(20) | 订阅等级：free/professional/enterprise |
| subscription_status | VARCHAR(20) | 订阅状态：active/cancelled/expired |
| created_at | TIMESTAMP | 账户创建时间，UTC时区 |
| updated_at | TIMESTAMP | 最后更新时间，UTC时区 |

---

## 3. 社交账户表 (social_accounts)

### 3.1 表结构

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PK | 账户ID |
| user_id | UUID | FK, NOT NULL | 所属用户ID |
| platform | VARCHAR(50) | NOT NULL | 平台类型 |
| account_name | VARCHAR(255) | NOT NULL | 账户名称 |
| access_token | TEXT | NOT NULL | 访问令牌 |
| refresh_token | TEXT | NULL | 刷新令牌 |
| token_expires_at | TIMESTAMP | NULL | Token过期时间 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

### 3.2 字段详细说明

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | UUID | 主键，社交账户唯一标识 |
| user_id | UUID | 外键，关联users表 |
| platform | VARCHAR(50) | 社交平台标识：wechat/linkedin/twitter/facebook |
| account_name | VARCHAR(255) | 在平台上显示的名称 |
| access_token | TEXT | 平台OAuth access_token |
| refresh_token | TEXT | 平台OAuth refresh_token（用于Token刷新） |
| token_expires_at | TIMESTAMP | access_token过期时间 |
| is_active | BOOLEAN | 账户是否处于连接状态，false表示已断开 |
| created_at | TIMESTAMP | 账户连接时间，UTC时区 |

---

## 4. 内容表 (contents)

### 4.1 表结构

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PK | 内容ID |
| user_id | UUID | FK, NOT NULL | 所属用户ID |
| title | VARCHAR(255) | NULL | 标题 |
| body | TEXT | NOT NULL | 正文内容 |
| content_type | VARCHAR(50) | NULL | 内容类型 |
| status | VARCHAR(20) | DEFAULT 'draft' | 状态 |
| ai_prompt_used | TEXT | NULL | AI生成提示词 |
| platform_specific | JSONB | NULL | 平台特定配置 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

### 4.2 字段详细说明

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | UUID | 主键，内容唯一标识 |
| user_id | UUID | 外键，关联users表 |
| title | VARCHAR(255) | 内容标题，最长255字符 |
| body | TEXT | 内容正文，最长10000字符 |
| content_type | VARCHAR(50) | 内容类型：article/tweet/post/caption |
| status | VARCHAR(20) | 内容状态：draft/scheduled/published/failed |
| ai_prompt_used | TEXT | AI生成时使用的提示词，用于追溯AI贡献 |
| platform_specific | JSONB | 平台特定的内容配置，如微信的图片、视频等 |
| created_at | TIMESTAMP | 内容创建时间，UTC时区 |
| updated_at | TIMESTAMP | 内容最后更新时间，UTC时区 |

---

## 5. 调度表 (schedules)

### 5.1 表结构

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PK | 调度ID |
| content_id | UUID | FK, NOT NULL | 内容ID |
| social_account_id | UUID | FK, NOT NULL | 社交账户ID |
| scheduled_at | TIMESTAMP | NOT NULL | 计划发布时间 |
| published_at | TIMESTAMP | NULL | 实际发布时间 |
| status | VARCHAR(20) | DEFAULT 'pending' | 发布状态 |
| platform_post_id | TEXT | NULL | 平台发布ID |
| error_message | TEXT | NULL | 错误信息 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

### 5.2 字段详细说明

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | UUID | 主键，调度任务唯一标识 |
| content_id | UUID | 外键，关联contents表 |
| social_account_id | UUID | 外键，关联social_accounts表 |
| scheduled_at | TIMESTAMP | 计划发布时间，用户指定 |
| published_at | TIMESTAMP | 实际发布时间，系统记录 |
| status | VARCHAR(20) | 发布状态：pending/published/failed/cancelled |
| platform_post_id | TEXT | 发布到平台后返回的ID，用于追溯 |
| error_message | TEXT | 发布失败时的错误信息 |
| created_at | TIMESTAMP | 调度任务创建时间，UTC时区 |

---

## 6. 分析表 (analytics)

### 6.1 表结构

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PK | 分析ID |
| schedule_id | UUID | FK, NOT NULL | 调度ID |
| platform | VARCHAR(50) | NOT NULL | 平台类型 |
| impressions | INTEGER | DEFAULT 0 | 曝光量 |
| likes | INTEGER | DEFAULT 0 | 点赞数 |
| shares | INTEGER | DEFAULT 0 | 分享数 |
| comments | INTEGER | DEFAULT 0 | 评论数 |
| clicks | INTEGER | DEFAULT 0 | 点击数 |
| collected_at | TIMESTAMP | DEFAULT NOW() | 收集时间 |

### 6.2 字段详细说明

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | UUID | 主键，分析数据唯一标识 |
| schedule_id | UUID | 外键，关联schedules表 |
| platform | VARCHAR(50) | 社交平台标识 |
| impressions | INTEGER | 内容曝光次数 |
| likes | INTEGER | 内容点赞数 |
| shares | INTEGER | 内容分享/转发数 |
| comments | INTEGER | 内容评论数 |
| clicks | INTEGER | 内容链接点击数 |
| collected_at | TIMESTAMP | 数据收集时间，用于历史追踪 |

---

## 7. 枚举值定义

### 7.1 subscription_tier (订阅等级)

| 值 | 说明 | 账户数限制 |
|------|------|-----------|
| free | 免费版 | 1个账户 |
| professional | 专业版 | 5个账户 |
| enterprise | 企业版 | 无限账户 |

### 7.2 subscription_status (订阅状态)

| 值 | 说明 |
|------|------|
| active | 有效 |
| cancelled | 已取消 |
| expired | 已过期 |

### 7.3 platform (平台类型)

| 值 | 说明 |
|------|------|
| wechat | 微信服务号 |
| linkedin | LinkedIn |
| twitter | Twitter/X |
| facebook | Facebook |
| instagram | Instagram |

### 7.4 content_type (内容类型)

| 值 | 说明 | 典型长度 |
|------|------|----------|
| article | 文章 | 长篇内容 |
| tweet | 推文 | 短内容 |
| post | 帖子 | 中等内容 |
| caption | 标题/摘要 | 简短文本 |

### 7.5 content_status (内容状态)

| 值 | 说明 |
|------|------|
| draft | 草稿 |
| scheduled | 已排期 |
| published | 已发布 |
| failed | 发布失败 |

### 7.6 schedule_status (调度状态)

| 值 | 说明 |
|------|------|
| pending | 待发布 |
| published | 已发布 |
| failed | 发布失败 |
| cancelled | 已取消 |

---

## 8. ER图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ER Diagram                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌──────────┐           ┌──────────────────┐          ┌──────────┐   │
│    │  users   │           │  social_accounts │          │ contents │   │
│    ├──────────┤           ├──────────────────┤          ├──────────┤   │
│    │ id (PK)  │◄──┐      │ id (PK)          │     ┌───►│ id (PK)  │   │
│    │ email    │   │      │ user_id (FK)     │◄────┘    │ user_id  │   │
│    │ name     │   │      │ platform         │          │ title    │   │
│    │ password_│   │      │ account_name     │          │ body     │   │
│    │  hash    │   │      │ access_token     │          │ type     │   │
│    │ sub_tier │   │      │ is_active        │          │ status   │   │
│    └──────────┘   │      └──────────────────┘          └────┬─────┘   │
│                   │                                            │         │
│                   │                                            │         │
│                   │           ┌──────────────────┐              │         │
│                   │           │   schedules     │              │         │
│                   │           ├──────────────────┤              │         │
│                   │           │ id (PK)          │              │         │
│                   └──────────►│ content_id (FK)  │◄─────────────┘         │
│                               │ social_account_id│                          │
│                               │ scheduled_at     │                          │
│                               │ published_at     │                          │
│                               │ status           │                          │
│                               └────────┬─────────┘                          │
│                                        │                                   │
│                                        │                                   │
│                               ┌────────▼─────────┐                        │
│                               │   analytics      │                        │
│                               ├──────────────────┤                        │
│                               │ id (PK)          │                        │
│                               │ schedule_id (FK) │◄─┐                     │
│                               │ platform         │   │                     │
│                               │ impressions       │   │                     │
│                               │ likes            │   │                     │
│                               │ shares           │   │                     │
│                               │ comments         │   │                     │
│                               │ clicks           │   │                     │
│                               │ collected_at     │   │                     │
│                               └──────────────────┘   │                     │
│                                                    │                     │
└────────────────────────────────────────────────────┴─────────────────────┘
```

---

### 表关系说明

| 关系 | 类型 | 说明 |
|------|------|------|
| users -> social_accounts | 1:N | 一个用户可以有多个社交账户 |
| users -> contents | 1:N | 一个用户可以创建多条内容 |
| users -> schedules | 1:N | 一个用户可以有多个调度任务 |
| social_accounts -> schedules | 1:N | 一个社交账户可以有多个调度 |
| contents -> schedules | 1:N | 一条内容可以有多个调度 |
| schedules -> analytics | 1:N | 每次发布可以有多条分析数据 |

---

**文档结束**

*本数据字典定义了SocialAI Service的数据库结构，是开发、测试和数据迁移的重要参考文档。*
