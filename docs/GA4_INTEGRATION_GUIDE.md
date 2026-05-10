# Google Analytics 4 接入操作手册

**编制日期**: 2026-04-29  
**版本**: v1.0  
**适用范围**: SocialAI Manager MVP阶段

---

## 一、概述

本手册指导将Google Analytics 4 (GA4) 接入SocialAI Manager前端，记录用户行为、追踪D7留存、评估投放ROI。

**前置条件**:
- Google账号
- 可访问Google Analytics (需翻墙)
- React 18+ 前端项目

---

## 二、GA4账号创建

### 2.1 创建GA4媒体资源

1. **访问**: https://analytics.google.com
2. **登录**: 使用Google账号登录
3. **创建账号**:
   - 点击 "开始测量" (Start measuring)
   - 填写账号名称: `SocialAI`
   - 配置数据共享: 按需勾选
   - 点击 "下一步"

4. **创建媒体资源**:
   - 填写属性名称: `SocialAI Manager`
   - 选择时区: Asia/Hong_Kong
   - 选择币种: CNY
   - 点击 "下一步"

5. **业务详情**:
   - 选择业务规模: 中小型
   - 选择行业: 互联网/软件
   - 点击 "创建"

6. **接受服务条款**: 勾选确认 → 点击 "创建"

### 2.2 获取Measurement ID

创建完成后，GA会生成Measurement ID，格式为 `G-XXXXXXXXXX`

**查看位置**:
- 管理 → 媒体资源 → 数据流 → Web数据流 → Measurement ID

### 2.3 配置数据流

1. **添加Web数据流**:
   - 管理 → 媒体资源 → 数据流 → 添加数据流 → Web

2. **填写网站信息**:
   - 网站URL: `http://localhost:5173` (开发) / `https://your-domain.com` (生产)
   - 数据流名称: `SocialAI Manager Web`

3. **获取数据流详情**:
   - Measurement ID (如 G-XXXXXXXXXX)
   - API密钥 (用于服务端)

---

## 三、前端集成

### 3.1 安装SDK

```bash
cd /home/gefa/Projects/SocialAI-Service/frontend
npm install react-ga4
```

### 3.2 初始化配置

编辑 `src/main.jsx`:

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import ReactGA from 'react-ga4'

// GA4初始化 - 替换为你的Measurement ID
ReactGA.initialize('G-XXXXXXXXXX', {
  // 可选: 测试模式（不发送到真实GA）
  // testMode: true,
  
  // 可选: 标准化维度
  gaOptions: {
    appName: 'SocialAI Manager',
    appVersion: '1.0.0'
  }
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### 3.3 环境变量管理

创建 `.env.local` (避免提交到Git):

```bash
# .env.local
VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
```

修改 `main.jsx`:

```jsx
import ReactGA from 'react-ga4'

// 从环境变量读取
const GA_ID = import.meta.env.VITE_GA4_MEASUREMENT_ID || 'G-XXXXXXXXXX'
ReactGA.initialize(GA_ID)
```

### 3.4 基础事件追踪

#### 3.4.1 页面浏览 (自动)

```jsx
import { useEffect } from 'react'
import ReactGA from 'react-ga4'

function usePageView() {
  useEffect(() => {
    ReactGA.send({
      hitType: 'pageview',
      page: window.location.pathname,
      title: document.title
    })
  }, [])
}

export default usePageView
```

在 `App.jsx` 中使用:

```jsx
import { useEffect } from 'react'
import ReactGA from 'react-ga4'

function App() {
  useEffect(() => {
    ReactGA.send({
      hitType: 'pageview',
      page: window.location.pathname,
      title: document.title
    })
  }, [])
  
  return (/* ... */)
}
```

---

## 四、核心事件定义

### 4.1 SocialAI特定事件

在 `src/utils/analytics.js` 中定义:

```javascript
// src/utils/analytics.js

import ReactGA from 'react-ga4'

// ===== 用户相关事件 =====

/**
 * 用户注册
 */
export function trackUserRegister(method) {
  ReactGA.event({
    category: 'User',
    action: 'Register',
    label: method // 'email' | 'google' | 'wechat'
  })
}

/**
 * 用户登录
 */
export function trackUserLogin(method) {
  ReactGA.event({
    category: 'User',
    action: 'Login',
    label: method
  })
}

/**
 * 用户登出
 */
export function trackUserLogout() {
  ReactGA.event({
    category: 'User',
    action: 'Logout'
  })
}

// ===== 内容相关事件 =====

/**
 * 内容生成
 */
export function trackContentGenerate(platform, model) {
  ReactGA.event({
    category: 'Content',
    action: 'Generate',
    label: platform, // 'wechat' | 'linkedin'
    value: 1
  })
}

/**
 * 内容发布
 */
export function trackContentPublish(platform, scheduleType) {
  ReactGA.event({
    category: 'Content',
    action: 'Publish',
    label: platform,
    value: 1
  })
}

/**
 * 内容保存到草稿
 */
export function trackContentSaveDraft(platform) {
  ReactGA.event({
    category: 'Content',
    action: 'SaveDraft',
    label: platform
  })
}

// ===== 社交账号相关事件 =====

/**
 * 绑定社交账号
 */
export function trackAccountBind(platform) {
  ReactGA.event({
    category: 'Account',
    action: 'Bind',
    label: platform
  })
}

/**
 * 解绑社交账号
 */
export function trackAccountUnbind(platform) {
  ReactGA.event({
    category: 'Account',
    action: 'Unbind',
    label: platform
  })
}

// ===== 调度相关事件 =====

/**
 * 创建调度
 */
export function trackScheduleCreate(platform, scheduledTime) {
  ReactGA.event({
    category: 'Schedule',
    action: 'Create',
    label: platform,
    value: 1
  })
}

/**
 * 调度发布成功
 */
export function trackSchedulePublishSuccess(scheduleId, platform) {
  ReactGA.event({
    category: 'Schedule',
    action: 'PublishSuccess',
    label: platform,
    value: 1
  })
}

/**
 * 调度发布失败
 */
export function trackSchedulePublishFailed(scheduleId, platform, error) {
  ReactGA.event({
    category: 'Schedule',
    action: 'PublishFailed',
    label: platform,
    value: 0
  })
}

// ===== 漏斗相关事件 =====

/**
 * D7留存追踪 - 用户活跃
 */
export function trackUserActive(userId, day) {
  ReactGA.event({
    category: 'Retention',
    action: `D${day}`,
    label: 'Active',
    value: day
  })
}

/**
 * 新用户注册
 */
export function trackNewUser(userId) {
  ReactGA.event({
    category: 'Acquisition',
    action: 'NewUser',
    label: 'signup',
    value: 1
  })
}
```

---

## 五、组件集成示例

### 5.1 注册页面集成

编辑 `src/pages/Register.jsx`:

```jsx
import { trackUserRegister } from '../utils/analytics'

function Register() {
  const handleRegister = async (method) => {
    // 注册逻辑...
    
    // 注册成功后追踪
    trackUserRegister(method)
  }
  
  return (/* ... */)
}
```

### 5.2 内容生成页面集成

编辑 `src/pages/AIGenerate.jsx`:

```jsx
import { trackContentGenerate } from '../utils/analytics'

function AIGenerate() {
  const handleGenerate = async (platform, model) => {
    // AI生成逻辑...
    
    // 生成完成后追踪
    trackContentGenerate(platform, model)
  }
  
  return (/* ... */)
}
```

### 5.3 调度页面集成

编辑 `src/pages/Schedules.jsx`:

```jsx
import { trackScheduleCreate, trackSchedulePublishSuccess } from '../utils/analytics'

function Schedules() {
  const handleCreateSchedule = async (platform, scheduledTime) => {
    // 创建调度逻辑...
    
    trackScheduleCreate(platform, scheduledTime)
  }
  
  const handlePublishSuccess = (scheduleId, platform) => {
    trackSchedulePublishSuccess(scheduleId, platform)
  }
  
  return (/* ... */)
}
```

---

## 六、用户ID追踪 (User ID)

### 6.1 登录后设置User ID

```jsx
import ReactGA from 'react-ga4'

function setUserId(userId) {
  ReactGA.set({ userId: userId })
}

function clearUserId() {
  ReactGA.reset()
}
```

在用户登录成功后调用:

```jsx
import { setUserId } from '../utils/analytics'

function Login() {
  const handleLogin = async (user) => {
    // 登录逻辑...
    
    // 设置GA User ID
    if (user.id) {
      setUserId(user.id)
    }
  }
  
  return (/* ... */)
}
```

### 6.2 跨设备追踪

通过设置User ID，GA可关联同一用户在不同设备/平台的行为:

```javascript
// 微信OAuth登录后
setUserId(wechatOpenId)

// LinkedIn OAuth登录后
setUserId(linkedInMemberId)
```

---

## 七、D7留存追踪配置

### 7.1 新用户首次活跃

在用户完成注册时:

```javascript
// 用户注册/首次登录时
ReactGA.event({
  category: 'Acquisition',
  action: 'FirstActive',
  label: 'D0',
  value: 0
})
```

### 7.2 每日活跃检测

创建每日Cron任务或在用户活跃时:

```javascript
// 用户活跃时（每次打开App/刷新页面）
ReactGA.event({
  category: 'Retention',
  action: `D${daysSinceRegistration}`,
  label: 'Active',
  value: daysSinceRegistration
})
```

### 7.3 GA4留存报告

GA4内置留存报告:
- 管理 → 媒体资源 → 报告 → 留存

自动记录:
- 第0天新用户数
- 第1-30天留存率
- 用户群组对比

---

## 八、服务端API集成 (可选)

### 8.1 安装Google API客户端

```bash
pip install google-analytics-data
```

### 8.2 服务端报表API

创建 `api/services/ga4_service.py`:

```python
"""
SocialAI - GA4 服务端集成
"""
from google.analytics.data import BetaAnalyticsDataClient
from google.analytics.data_v1beta.properties import RunReportRequest
import os

class GA4Service:
    def __init__(self):
        self.property_id = os.getenv('GA4_PROPERTY_ID')
        self.credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
    def get_d7_retention(self, start_date, end_date):
        """
        获取D7留存数据
        """
        client = BetaAnalyticsDataClient()
        
        response = client.run_report({
            'property': f'properties/{self.property_id}',
            'date_ranges': [{
                'start_date': start_date,
                'end_date': end_date
            }],
            'dimensions': [{'name': 'date'}],
            'metrics': [
                {'name': 'activeUsers'},           # 活跃用户
                {'name': 'newUsers'},               # 新用户
                {'name': 'eventCount'}             # 事件数
            ]
        })
        
        return response
    
    def get_content_performance(self, start_date, end_date):
        """
        获取内容表现数据
        """
        client = BetaAnalyticsDataClient()
        
        response = client.run_report({
            'property': f'properties/{self.property_id}',
            'date_ranges': [{
                'start_date': start_date,
                'end_date': end_date
            }],
            'dimensions': [
                {'name': 'eventName'},
                {'name': 'pageTitle'}
            ],
            'metrics': [
                {'name': 'eventCount'},
                {'name': 'totalUsers'}
            ],
            'dimension_filter': {
                'filter': {
                    'field_name': 'eventName',
                    'in_list_filter': {
                        'values': ['Content_Generate', 'Content_Publish', 'Content_SaveDraft']
                    }
                }
            }
        })
        
        return response
```

### 8.3 环境变量配置

```bash
# .env
GA4_PROPERTY_ID=123456789
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

---

## 九、事件调试

### 9.1 GA4 Debug模式

```javascript
import ReactGA from 'react-ga4'

// 启用Debug模式 - 事件发送到测试环境
ReactGA.initialize('G-XXXXXXXXXX', {
  debug: true,
  gaOptions: {
    sendHitTask: false // 不发送到GA（仅控制台输出）
  }
})
```

### 9.2 GA Debugger扩展

1. 安装Chrome扩展: GA Debugger
2. 打开开发者工具 → Network → 筛选 `google-analytics`
3. 操作页面，查看事件是否正确发送

### 9.3 实时事件查看

GA4 → 报告 → 实时 (Realtime)

可实时看到:
- 当前在线用户
- 活跃事件
- 热门页面

---

## 十、验证清单

完成接入后，逐项验证:

| # | 检查项 | 验证方法 |
|---|-------|----------|
| 1 | SDK安装成功 | `npm list react-ga4` |
| 2 | Measurement ID配置 | 检查 `.env.local` |
| 3 | 页面浏览追踪 | 访问页面 → GA4实时报告显示 |
| 4 | 用户注册事件 | 完成注册 → GA4事件报告 |
| 5 | 内容生成事件 | 生成内容 → GA4事件报告 |
| 6 | User ID设置 | 登录后 → 查看用户数据关联 |
| 7 | D7留存数据 | 7天后 → 留存报告出现数据 |
| 8 | 服务端API (可选) | 调用API → 返回数据 |

---

## 十一、常见问题

### Q1: 事件未显示在GA4中

**原因**: 
- Measurement ID错误
- 跨域追踪问题
- 代码未执行

**解决**:
1. 检查Measurement ID是否正确
2. 启用Debug模式查看错误
3. 确认代码已正确引入

### Q2: 本地开发如何测试

**方案**: 使用测试Measurement ID
```javascript
// .env.development
VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX_TEST
```

### Q3: 如何追踪已登录用户

**方案**: 设置User ID
```javascript
ReactGA.set({ userId: user.id })
```

### Q4: 隐私合规 (GDPR/CCPA)

**必须动作**:
1. 添加隐私政策页面
2. 获取用户Cookie同意
3. 配置数据保留期限

---

## 十二、相关文档

| 文档 | 说明 |
|------|------|
| `docs/DATA_SOURCE_INTEGRATION.md` | 数据源接入方案分析 |
| `docs/21_TECHNICAL_ARCHITECTURE.md` | 技术架构 |
| `docs/51_USER_MANUAL.md` | 用户操作手册 |

---

## 附录: 完整文件结构

```
SocialAI-Service/frontend/
├── src/
│   ├── main.jsx                    # GA4初始化
│   ├── utils/
│   │   └── analytics.js            # 事件追踪函数
│   ├── pages/
│   │   ├── Register.jsx           # 注册页面集成
│   │   ├── Login.jsx              # 登录页面集成
│   │   ├── AIGenerate.jsx         # AI生成页面集成
│   │   ├── Schedules.jsx          # 调度页面集成
│   │   └── Dashboard.jsx          # 仪表板
│   └── App.jsx                     # 全局页面追踪
├── .env.local                      # GA4 Measurement ID
└── package.json                     # react-ga4依赖

SocialAI-Service/api/
├── services/
│   └── ga4_service.py              # 服务端GA4 API (可选)
└── .env                             # GA4_PROPERTY_ID
```

---

*手册完成 | 2026-04-29*
*适用版本: SocialAI Manager v1.0 MVP*