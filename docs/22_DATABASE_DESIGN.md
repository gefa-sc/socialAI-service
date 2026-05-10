# SocialAI Service - 数据库设计

**项目**: SocialAI Service  
**版本**: V1.0  
**编制日期**: 2026-02-14

## 概述

本设计基于PostgreSQL数据库，用于支持SocialAI Service的核心功能。

## 实体关系图 (ERD)

### 用户表 (users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    avatar_url TEXT,
    subscription_tier VARCHAR(20) DEFAULT 'free', -- free, pro, enterprise
    subscription_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 社交媒体账户表 (social_accounts)
```sql
CREATE TABLE social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- twitter, linkedin, facebook, instagram
    account_name VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 内容表 (contents)
```sql
CREATE TABLE contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    body TEXT NOT NULL,
    content_type VARCHAR(50), -- article, tweet, post, caption
    status VARCHAR(20) DEFAULT 'draft', -- draft, scheduled, published, failed
    ai_prompt_used TEXT,
    platform_specific JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 发布计划表 (schedules)
```sql
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES contents(id) ON DELETE CASCADE,
    social_account_id UUID REFERENCES social_accounts(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP NOT NULL,
    published_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- pending, published, failed
    platform_post_id TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 分析数据表 (analytics)
```sql
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID REFERENCES schedules(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    impressions INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 用户订阅表 (subscriptions)
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tier VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    auto_renew BOOLEAN DEFAULT true,
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 索引设计
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_social_accounts_user ON social_accounts(user_id);
CREATE INDEX idx_contents_user ON contents(user_id);
CREATE INDEX idx_schedules_content ON schedules(content_id);
CREATE INDEX idx_schedules_scheduled_at ON schedules(scheduled_at);
CREATE INDEX idx_analytics_schedule ON analytics(schedule_id);
```

## 关系说明
- 1个用户可以有多个社交账户
- 1个内容可以对应多个发布计划（多平台发布）
- 1个发布计划对应1个社交账户
- 1个发布计划可以有多个分析数据记录