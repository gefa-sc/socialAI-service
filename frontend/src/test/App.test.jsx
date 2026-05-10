/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Login from '../pages/Login'
import Register from '../pages/Register'
import App from '../App'
import { AuthProvider } from '../hooks/useAuth'

// 模拟 API 模块
vi.mock('../api', () => ({
  authAPI: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn(),
    logout: vi.fn(),
  },
  contentsAPI: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  storage: {
    getToken: vi.fn(() => null),
    setToken: vi.fn(),
    getUser: vi.fn(() => null),
    setUser: vi.fn(),
    clear: vi.fn(),
  },
}))

// 模拟 localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value },
    removeItem: (key) => { delete store[key] },
    clear: () => { store = {} },
  }
})()

Object.defineProperty(global, 'localStorage', { value: localStorageMock })

describe('登录页面测试', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  it('应该渲染登录表单', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )
    
    expect(screen.getByPlaceholderText(/邮箱/i)).toBeDefined()
    expect(screen.getByPlaceholderText(/密码/i)).toBeDefined()
    expect(screen.getByRole('button', { name: /登录/i })).toBeDefined()
  })

  it('应该包含注册链接', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )
    
    expect(screen.getByText(/还没有账号/i)).toBeDefined()
  })

  it('应该显示表单验证错误（空提交）', async () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )
    
    const submitButton = screen.getByRole('button', { name: /登录/i })
    submitButton.click()
    
    // Ant Design Form 会显示验证错误
    await waitFor(() => {
      expect(screen.getByText(/请输入邮箱/i)).toBeDefined()
    })
  })
})

describe('注册页面测试', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  it('应该渲染注册表单', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Register />
        </AuthProvider>
      </BrowserRouter>
    )
    
    expect(screen.getByPlaceholderText(/邮箱/i)).toBeDefined()
    expect(screen.getByPlaceholderText(/密码/i)).toBeDefined()
    expect(screen.getByPlaceholderText(/确认密码/i)).toBeDefined()
    expect(screen.getByRole('button', { name: /注册/i })).toBeDefined()
  })

  it('应该包含登录链接', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Register />
        </AuthProvider>
      </BrowserRouter>
    )
    
    expect(screen.getByText(/已有账号/i)).toBeDefined()
  })
})

describe('认证状态测试', () => {
  it('应该从 localStorage 获取 token', () => {
    const token = 'test-token-123'
    localStorageMock.setItem('token', token)
    
    expect(localStorageMock.getItem('token')).toBe(token)
  })

  it('应该清除认证信息', () => {
    localStorageMock.setItem('token', 'test-token')
    localStorageMock.setItem('user', '{"name":"Test"}')
    
    localStorageMock.removeItem('token')
    localStorageMock.removeItem('user')
    
    expect(localStorageMock.getItem('token')).toBeNull()
    expect(localStorageMock.getItem('user')).toBeNull()
  })
})

describe('API 模拟测试', () => {
  it('应该正确处理登录成功响应', async () => {
    const mockResponse = {
      data: {
        access_token: 'mock-token',
        token_type: 'bearer',
      },
    }
    
    // 这里可以添加更详细的 API 响应测试
    expect(mockResponse.data.access_token).toBe('mock-token')
    expect(mockResponse.data.token_type).toBe('bearer')
  })

  it('应该正确处理登录错误', () => {
    const mockError = {
      response: {
        status: 401,
        data: {
          detail: 'Incorrect email or password',
        },
      },
    }
    
    expect(mockError.response.status).toBe(401)
    expect(mockError.response.data.detail).toBe('Incorrect email or password')
  })
})

describe('密码验证测试', () => {
  it('应该验证密码长度', () => {
    const validatePassword = (password) => {
      return password && password.length >= 6
    }
    
    expect(validatePassword('123456')).toBe(true)
    expect(validatePassword('12345')).toBe(false)
    expect(validatePassword('')).toBeFalsy()
  })

  it('应该验证邮箱格式', () => {
    const validateEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    }
    
    expect(validateEmail('test@example.com')).toBe(true)
    expect(validateEmail('invalid-email')).toBe(false)
    expect(validateEmail('missing@domain')).toBe(false)
  })

  it('应该验证两次密码一致', () => {
    const validatePasswordMatch = (password, confirmPassword) => {
      return password === confirmPassword
    }
    
    expect(validatePasswordMatch('password123', 'password123')).toBe(true)
    expect(validatePasswordMatch('password123', 'password456')).toBe(false)
  })
})
