/**
 * SocialAI Service - 错误边界组件
 * 捕获子组件的错误并显示友好界面
 */
import { Component } from 'react';
import { Result, Button } from 'antd';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <Result
          status="error"
          title="出现问题"
          subTitle={this.state.error?.message || '应用程序发生了错误，请尝试刷新页面'}
          extra={[
            <Button type="primary" key="refresh" onClick={() => window.location.reload()}>
              刷新页面
            </Button>,
            <Button key="retry" onClick={this.handleRetry}>
              重试
            </Button>,
          ]}
        />
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
