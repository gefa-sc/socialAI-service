"""
SocialAI Service - 前端页面组件测试
"""
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';

// 测试 Login 页面
describe('Login Page', () => {
  test('renders login form', () => {
    render(<Login />);
    expect(screen.getByPlaceholderText(/邮箱/)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/密码/)).toBeInTheDocument();
  });
  
  test('shows error for empty fields', async () => {
    render(<Login />);
    await userEvent.click(screen.getByText(/登录/));
    expect(screen.getByText(/请输入邮箱/)).toBeInTheDocument();
  });
  
  test('validates email format', async () => {
    render(<Login />);
    await userEvent.type(screen.getByPlaceholderText(/邮箱/), 'invalid');
    await userEvent.click(screen.getByText(/登录/));
    expect(screen.getByText(/请输入有效的邮箱/)).toBeInTheDocument();
  });
});

// 测试 Register 页面
describe('Register Page', () => {
  test('renders registration form', () => {
    render(<Register />);
    expect(screen.getByPlaceholderText(/邮箱/)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/密码/)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/确认密码/)).toBeInTheDocument();
  });
  
  test('validates password match', async () => {
    render(<Register />);
    await userEvent.type(screen.getByPlaceholderText(/密码/), 'password123');
    await userEvent.type(screen.getByPlaceholderText(/确认密码/), 'different');
    await userEvent.click(screen.getByText(/注册/));
    expect(screen.getByText(/两次密码不一致/)).toBeInTheDocument();
  });
});

// 测试 AIGenerate 页面
describe('AIGenerate Page', () => {
  test('renders AI generate form', () => {
    render(<AIGenerate />);
    expect(screen.getByText(/AI 内容生成/)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/生成提示词/)).toBeInTheDocument();
  });
  
  test('shows platform selector', () => {
    render(<AIGenerate />);
    expect(screen.getByText(/目标平台/)).toBeInTheDocument();
  });
  
  test('shows content type selector', () => {
    render(<AIGenerate />);
    expect(screen.getByText(/内容类型/)).toBeInTheDocument();
  });
});

// 测试 ErrorBoundary 组件
describe('ErrorBoundary', () => {
  test('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>正常内容</div>
      </ErrorBoundary>
    );
    expect(screen.getByText(/正常内容/)).toBeInTheDocument();
  });
  
  test('shows error UI when error occurs', () => {
    const ThrowError = () => {
      throw new Error('测试错误');
    };
    
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    
    expect(screen.getByText(/出现问题/)).toBeInTheDocument();
    expect(screen.getByText(/刷新页面/)).toBeInTheDocument();
  });
});
