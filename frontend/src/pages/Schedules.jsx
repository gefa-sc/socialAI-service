/**
 * SocialAI Service - 发布调度页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, Form, Select, DatePicker, message, Popconfirm, Empty } from 'antd';
import { PlusOutlined, SendOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { schedulesAPI, contentsAPI, accountsAPI } from '../api';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;

export default function Schedules() {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [contents, setContents] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [form] = Form.useForm();
  const [isMounted, setIsMounted] = useState(true);

  // 加载调度列表
  const loadSchedules = async () => {
    if (!isMounted) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      console.log('[Schedules] Token exists:', !!token);
      const response = await schedulesAPI.list({ page: 1, page_size: 100 });
      console.log('[Schedules] Response:', response.data);
      if (isMounted) {
        setSchedules(response.data.items || []);
      }
    } catch (error) {
      console.error('[Schedules] Load error:', error);
      if (isMounted) {
        message.error('加载调度列表失败: ' + (error.response?.data?.detail || error.message));
      }
    } finally {
      if (isMounted) {
        setLoading(false);
      }
    }
  };

  // 加载可选内容
  const loadContents = async () => {
    if (!isMounted) return;
    try {
      const response = await contentsAPI.list({ status: 'draft' });
      if (isMounted) {
        setContents(response.data || []);
      }
    } catch (error) {
      console.error('加载内容失败', error);
    }
  };

  // 加载可选账户
  const loadAccounts = async () => {
    if (!isMounted) return;
    try {
      const response = await accountsAPI.list({ is_active: true });
      if (isMounted) {
        setAccounts(response.data || []);
      }
    } catch (error) {
      console.error('加载账户失败', error);
    }
  };

  useEffect(() => {
    setIsMounted(true);
    loadSchedules();
    loadContents();
    loadAccounts();
    return () => setIsMounted(false);
  }, []);

  // 创建调度
  const handleSubmit = async (values) => {
    try {
      const data = {
        content_id: values.content_id,
        social_account_id: values.social_account_id,
        scheduled_at: values.scheduled_at.toISOString(),
      };
      await schedulesAPI.create(data);
      message.success('创建成功');
      setModalVisible(false);
      form.resetFields();
      loadSchedules();
    } catch (error) {
      message.error(error.response?.data?.detail || '创建失败');
    }
  };

  // 取消调度
  const handleCancel = async (id) => {
    try {
      await schedulesAPI.cancel(id);
      message.success('取消成功');
      loadSchedules();
    } catch (error) {
      message.error('取消失败');
    }
  };

  // 立即发布
  const handlePublishNow = async (id) => {
    try {
      await schedulesAPI.publishNow(id);
      message.success('发布成功');
      loadSchedules();
    } catch (error) {
      message.error('发布失败');
    }
  };

  // 删除调度
  const handleDelete = async (id) => {
    try {
      await schedulesAPI.delete(id);
      message.success('删除成功');
      loadSchedules();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const columns = [
    {
      title: '内容标题',
      dataIndex: ['content', 'title'],
      key: 'content_title',
      render: (text, record) => record.content?.title || '未知内容',
    },
    {
      title: '平台',
      dataIndex: ['account', 'platform'],
      key: 'platform',
      width: 100,
      render: (platform) => {
        const map = {
          wechat: { label: '微信', color: 'green' },
          linkedin: { label: 'LinkedIn', color: 'blue' },
        };
        const item = map[platform] || { label: platform, color: 'default' };
        return <Tag color={item.color}>{item.label}</Tag>;
      },
    },
    {
      title: '计划发布时间',
      dataIndex: 'scheduled_at',
      key: 'scheduled_at',
      width: 180,
      render: (text) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const map = {
          pending: { label: '待发布', color: 'processing' },
          published: { label: '已发布', color: 'success' },
          failed: { label: '失败', color: 'error' },
          cancelled: { label: '已取消', color: 'default' },
        };
        const item = map[status] || { label: status, color: 'default' };
        return <Tag color={item.color}>{item.label}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          {record.status === 'pending' && (
            <>
              <Button type="link" size="small" icon={<SendOutlined />} onClick={() => handlePublishNow(record.id)}>
                立即发布
              </Button>
              <Button type="link" size="small" danger icon={<CloseCircleOutlined />} onClick={() => handleCancel(record.id)}>
                取消
              </Button>
            </>
          )}
          {record.status !== 'cancelled' && record.status !== 'published' && (
            <Popconfirm title="确定删除?" onConfirm={() => handleDelete(record.id)}>
              <Button type="link" size="small" danger>删除</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1>发布调度</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          创建调度
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={schedules}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 20 }}
        locale={{
          emptyText: loading ? '加载中...' : <Empty description="暂无调度任务，请先创建内容并绑定社交账户" />
        }}
      />

      <Modal
        title="创建调度"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="content_id" label="选择内容" rules={[{ required: true, message: '请选择内容' }]}>
            <Select placeholder="请选择要发布的内容">
              {contents.map((item) => (
                <Option key={item.id} value={item.id}>
                  {item.title || item.body?.substring(0, 30) || '无标题'}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="social_account_id" label="选择平台" rules={[{ required: true, message: '请选择平台' }]}>
            <Select placeholder="请选择发布平台">
              {accounts.map((item) => (
                <Option key={item.id} value={item.id}>
                  {item.platform === 'wechat' ? '微信' : 'LinkedIn'} - {item.account_name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="scheduled_at" label="发布时间" rules={[{ required: true, message: '请选择时间' }]}>
            <DatePicker 
              showTime 
              format="YYYY-MM-DD HH:mm" 
              placeholder="选择发布时间"
              disabledDate={(current) => current && current < dayjs().startOf('day')}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">创建</Button>
              <Button onClick={() => setModalVisible(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
