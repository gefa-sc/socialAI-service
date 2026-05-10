/**
 * SocialAI Manager - API请求模块
 * 封装所有后端API调用
 */

import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',  // 通过Vite代理转发到后端
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 自动添加Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除本地存储
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==================== 认证模块 ====================

export const authAPI = {
  // 用户注册
  register: (data) => api.post('/auth/register', data),
  
  // 用户登录 - 使用FormData格式
  login: (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 获取当前用户信息
  getCurrentUser: () => api.get('/auth/me'),
  
  // 退出登录
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

// ==================== 内容管理模块 ====================

export const contentsAPI = {
  // 获取内容列表
  list: (params) => api.get('/contents/', { params }),
  
  // 获取内容详情
  get: (id) => api.get(`/contents/${id}/`),
  
  // 创建内容
  create: (data) => api.post('/contents/', data),
  
  // 更新内容
  update: (id, data) => api.put(`/contents/${id}/`, data),
  
  // 删除内容
  delete: (id) => api.delete(`/contents/${id}/`),
  
  // AI生成内容
  generate: (prompt, contentType = 'article', options = {}) => 
    api.post('/ai/generate/', { prompt, content_type: contentType, ...options }),
  
  // 内容优化
  optimize: (content, instruction) =>
    api.post('/ai/optimize/', { content, instruction }),
  
  // 内容翻译
  translate: (content, targetLang) =>
    api.post('/ai/translate/', { content, target_lang: targetLang }),
  
  // 获取模板
  getTemplates: () => api.get('/ai/templates/'),
};

// ==================== 社交账户模块 ====================

export const accountsAPI = {
  // 获取账户列表
  list: (params) => api.get('/accounts/', { params }),
  
  // 获取账户详情
  get: (id) => api.get(`/accounts/${id}/`),
  
  // 连接新账户
  connect: (platform, code) => 
    api.post('/accounts/connect/', { platform, code }),
  
  // 断开账户
  disconnect: (id) => api.delete(`/accounts/${id}/`),
  
  // 获取OAuth URL
  getOAuthUrl: (platform) => api.get(`/accounts/oauth/${platform}/`),
  
  // 刷新Token
  refreshToken: (id) => api.post(`/accounts/${id}/refresh/`),
  
  // 测试连接
  testConnection: (id) => api.get(`/accounts/${id}/test/`),
};

// ==================== 发布调度模块 ====================

export const schedulesAPI = {
  // 获取调度列表
  list: (params) => api.get('/schedules/', { params }),
  
  // 获取调度详情
  get: (id) => api.get(`/schedules/${id}/`),
  
  // 创建调度
  create: (data) => api.post('/schedules/', data),
  
  // 更新调度
  update: (id, data) => api.put(`/schedules/${id}/`, data),
  
  // 删除调度
  delete: (id) => api.delete(`/schedules/${id}/`),
  
  // 取消调度
  cancel: (id) => api.post(`/schedules/${id}/cancel/`),
  
  // 立即发布
  publishNow: (id) => api.post(`/schedules/${id}/publish-now/`),
  
  // 获取状态
  getStatus: (id) => api.get(`/schedules/${id}/status/`),
  
  // 获取发布队列
  getQueue: (limit = 10) => api.get('/schedules/queue/', { params: { limit } }),
};

// ==================== 数据分析模块 ====================

export const analyticsAPI = {
  // 获取数据概览
  getOverview: (days = 30) => api.get('/analytics/overview/', { params: { days } }),
  
  // 获取内容分析
  getContentAnalytics: (contentId) => api.get(`/analytics/content/${contentId}/`),
  
  // 获取账户分析
  getAccountsAnalytics: (platform) => 
    api.get('/analytics/accounts/', { params: { platform } }),
  
  // 获取趋势数据
  getTrends: (period = 'daily', days = 30) => 
    api.get('/analytics/trends/', { params: { period, days } }),
  
  // 生成报告
  generateReport: (period = 'weekly', startDate, endDate) => 
    api.get('/analytics/report/', { params: { period, start_date: startDate, end_date: endDate } }),
  
  // 实时统计
  getRealtime: () => api.get('/analytics/realtime/'),
  
  // 平台对比
  comparePlatforms: (days = 30) => api.get('/analytics/comparison/', { params: { days } }),
};

// ==================== 工具函数 ====================

export const storage = {
  // 保存Token
  setToken: (token) => localStorage.setItem('token', token),
  
  // 获取Token
  getToken: () => localStorage.getItem('token'),
  
  // 保存用户信息
  setUser: (user) => localStorage.setItem('user', JSON.stringify(user)),
  
  // 获取用户信息
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  
  // 清除所有存储
  clear: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

export default api;
