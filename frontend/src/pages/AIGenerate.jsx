/**
 * SocialAI Service - AI生成页面
 */
import { useState, useEffect } from 'react';
import { Card, Form, Input, Select, Button, Space, Result, message, Tag, Alert } from 'antd';
import { RobotOutlined, CopyOutlined, PlusOutlined } from '@ant-design/icons';
import { contentsAPI, accountsAPI } from '../api';

const { TextArea } = Input;
const { Option } = Select;

// 平台配置
const PLATFORM_CONFIG = {
  wechat: { name: '微信', icon: '💬', enabled: true },
  linkedin: { name: 'LinkedIn', icon: '💼', enabled: false },
  twitter: { name: 'Twitter', icon: '🐦', enabled: false },
  xiaohongshu: { name: '小红书', icon: '📕', enabled: false },
};

export default function AIGenerate() {
  const [loading, setLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState('');
  const [form] = Form.useForm();
  const [connectedPlatforms, setConnectedPlatforms] = useState([]); // 初始为空，等待加载

  // 加载已绑定的平台
  useEffect(() => {
    const loadPlatforms = async () => {
      try {
        const response = await accountsAPI.list();
        const accounts = response.data || [];
        // 从已连接账户提取平台
        const platforms = accounts.map(acc => acc.platform).filter(Boolean);
        if (platforms.length > 0) {
          setConnectedPlatforms(platforms);
        }
      } catch (error) {
        console.error('加载平台失败:', error);
      }
    };
    loadPlatforms();
  }, []);

  // 生成内容
  const handleGenerate = async (values) => {
    setLoading(true);
    setGeneratedContent('');
    
    try {
      // 调用AI生成接口
      const response = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(values)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setGeneratedContent(data.content);
        message.success('内容生成成功！');
      } else {
        message.error(data.detail || '生成失败');
      }
    } catch (error) {
      console.error('生成错误:', error);
      message.error('生成失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 复制内容
  const handleCopy = () => {
    if (generatedContent) {
      navigator.clipboard.writeText(generatedContent);
      message.success('已复制到剪贴板');
    }
  };

  // 保存为内容
  const handleSave = async () => {
    if (!generatedContent) return;
    
    try {
      await contentsAPI.create({
        title: form.getFieldValue('prompt')?.substring(0, 50) || 'AI生成内容',
        body: generatedContent,
        content_type: 'article',
        status: 'draft'
      });
      message.success('已保存到内容管理');
    } catch (error) {
      message.error('保存失败');
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '24px' }}>
        <RobotOutlined style={{ marginRight: 8 }} />
        AI 内容生成
      </h1>
      
      <Card>
        {connectedPlatforms.length === 0 && (
          <Alert
            message="暂无绑定的社交账户"
            description="请先在「社交账户」页面绑定微信或其他平台，以便生成针对性的内容。"
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}
        
        <Form
          form={form}
          layout="vertical"
          onFinish={handleGenerate}
          initialValues={{
            content_type: 'article',
            tone: 'professional',
            length: 'medium',
            platform: 'wechat'
          }}
        >
          <Form.Item
            name="prompt"
            label="生成提示词"
            rules={[{ required: true, message: '请输入生成提示词' }]}
          >
            <TextArea
              rows={4}
              placeholder="描述你想要生成的内容，例如：关于人工智能发展趋势的文章"
            />
          </Form.Item>
          
          <Space size="large" wrap>
            <Form.Item
              name="platform"
              label="目标平台"
            >
              <Select 
                style={{ width: 160 }} 
                disabled={connectedPlatforms.length === 0}
              >
                {connectedPlatforms.length === 0 ? (
                  <Option value="" disabled>请先绑定社交账户</Option>
                ) : (
                  connectedPlatforms.map(platform => (
                    <Option key={platform} value={platform}>
                      {PLATFORM_CONFIG[platform]?.name || platform}
                    </Option>
                  ))
                )}
              </Select>
            </Form.Item>
            
            <Form.Item
              name="content_type"
              label="内容类型"
            >
              <Select style={{ width: 140 }}>
                <Option value="article">文章</Option>
                <Option value="post">帖子</Option>
                <Option value="caption">文案</Option>
                <Option value="hashtag">话题标签</Option>
              </Select>
            </Form.Item>
            
            <Form.Item
              name="tone"
              label="语气风格"
            >
              <Select style={{ width: 120 }}>
                <Option value="professional">专业</Option>
                <Option value="friendly">友好</Option>
                <Option value="humorous">幽默</Option>
              </Select>
            </Form.Item>
            
            <Form.Item
              name="length"
              label="长度"
            >
              <Select style={{ width: 100 }}>
                <Option value="short">短</Option>
                <Option value="medium">中</Option>
                <Option value="long">长</Option>
              </Select>
            </Form.Item>
          </Space>
          
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={<RobotOutlined />}
              size="large"
            >
              {loading ? '生成中...' : 'AI生成'}
            </Button>
          </Form.Item>
        </Form>
        
        {generatedContent && (
          <div style={{ marginTop: '24px', borderTop: '1px solid #f0f0f0', paddingTop: '24px' }}>
            <Space style={{ marginBottom: 16 }}>
              <Tag color="green">生成完成</Tag>
              <Button icon={<CopyOutlined />} onClick={handleCopy}>
                复制
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleSave}>
                保存到内容库
              </Button>
            </Space>
            
            <div
              style={{
                background: '#fafafa',
                padding: '16px',
                borderRadius: '8px',
                whiteSpace: 'pre-wrap',
                lineHeight: '1.8'
              }}
            >
              {generatedContent}
            </div>
          </div>
        )}
      </Card>
      
      <Card style={{ marginTop: '16px' }}>
        <h3>使用说明</h3>
        <ul>
          <li><strong>文章</strong>：生成完整的公众号文章</li>
          <li><strong>帖子</strong>：生成适合社交媒体发布的短内容</li>
          <li><strong>文案</strong>：生成吸引人的广告文案</li>
          <li><strong>话题标签</strong>：生成热门话题标签</li>
        </ul>
      </Card>
    </div>
  );
}
