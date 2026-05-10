/**
 * 前端测试配置文件
 */
import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// Mock window.matchMedia for Antd
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// 每个测试后清理
afterEach(() => {
  cleanup()
})

// 全局 expect 扩展
expect.extend({
  // 可以添加自定义 matchers
})
