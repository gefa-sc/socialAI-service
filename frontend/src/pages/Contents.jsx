/**
 * SocialAI Service - 内容管理页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, Form, Input, Select, message, Popconfirm, Empty } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { contentsAPI } from '../api';

const { TextArea } = Input;
const { Option } = Select;

export default function Contents() {
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingContent, setEditingContent] = useState(null);
  const [aiGenerating, setAiGenerating] = useState(false);
  const [form] = Form.useForm();
  const [isMounted, setIsMounted] = useState(true);

  // 加载内容列表
  const loadContents = async () => {
    if (!isMounted) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      console.log('[Contents] Token exists:', !!token);
      const response = await contentsAPI.list();
      console.log('[Contents] Response:', response.data);
      if (isMounted) {
        setContents(response.data || []);
      }
    } catch (error) {
      console.error('[Contents] Load error:', error);
      console.error('[Contents] Error response:', error.response?.data);
      if (isMounted) {
        message.error('加载内容列表失败: ' + (error.response?.data?.detail || error.message));
      }
    } finally {
      if (isMounted) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    setIsMounted(true);
    loadContents();
    return () => setIsMounted(false);
  }, []);

  // 创建/编辑内容
  const handleSubmit = async (values) => {
    try {
      if (editingContent) {
        await contentsAPI.update(editingContent.id, values);
        message.success('更新成功');
      } else {
        await contentsAPI.create(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      form.resetFields();
      setEditingContent(null);
      loadContents();
    } catch (error) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  // 删除内容
  const handleDelete = async (id) => {
    try {
      await contentsAPI.delete(id);
      message.success('删除成功');
      loadContents();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // AI生成内容
  const handleAIGenerate = async () => {
    const prompt = form.getFieldValue('ai_prompt');
    if (!prompt) {
      message.warning('请输入生成提示词');
      return;
    }
    
    setAiGenerating(true);
    try {
      const response = await contentsAPI.generate(prompt, form.getFieldValue('content_type') || 'article');
      form.setFieldsValue({
        body: response.data.body,
        title: response.data.title,
      });
      message.success('AI生成成功');
    } catch (error) {
      message.error('AI生成失败');
    } finally {
      setAiGenerating(false);
    }
  };

  // 打开编辑弹窗
  const openEditModal = (record) => {
    setEditingContent(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  // 打开创建弹窗
  const openCreateModal = () => {
    setEditingContent(null);
    form.resetFields();
    setModalVisible(true);
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      render: (text) => text || '无标题',
    },
    {
      title: '类型',
      dataIndex: 'content_type',
      key: 'content_type',
      width: 100,
      render: (type) => {
        const map = {
          article: { label: '文章', color: 'blue' },
          tweet: { label: '推文', color: 'green' },
          post: { label: '帖子', color: 'orange' },
          caption: { label: '文案', color: 'purple' },
        };
        const item = map[type] || { label: type, color: 'default' };
        return <Tag color={item.color}>{item.label}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const map = {
          draft: { label: '草稿', color: 'default' },
          scheduled: { label: '已定时', color: 'blue' },
          published: { label: '已发布', color: 'success' },
          failed: { label: '失败', color: 'error' },
        };
        const item = map[status] || { label: status, color: 'default' };
        return <Tag color={item.color}>{item.label}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={() => openEditModal(record)}>
            编辑
          </Button>
          <Popconfirm title="确定删除?" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1>内容管理</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreateModal}>
          创建内容
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={contents}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 20 }}
        locale={{
          emptyText: loading ? '加载中...' : <Empty description="暂无内容，请先创建内容或使用AI生成" />
        }}
      />

      <Modal
        title={editingContent ? '编辑内容' : '创建内容'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="title" label="标题">
            <Input placeholder="请输入标题" />
          </Form.Item>

          <Form.Item name="content_type" label="内容类型" initialValue="article">
            <Select>
              <Option value="article">文章</Option>
              <Option value="tweet">推文</Option>
              <Option value="post">帖子</Option>
              <Option value="caption">文案</Option>
            </Select>
          </Form.Item>

          <Form.Item name="ai_prompt" label="AI生成提示词">
            <Input.Search
              placeholder="输入提示词，让AI帮你生成内容"
              enterButton={<><ThunderboltOutlined /> AI生成</>}
              onSearch={handleAIGenerate}
              loading={aiGenerating}
            />
          </Form.Item>

          <Form.Item name="body" label="内容正文" rules={[{ required: true, message: '请输入内容' }]}>
            <TextArea rows={8} placeholder="请输入内容正文" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingContent ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
