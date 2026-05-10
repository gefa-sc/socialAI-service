/**
 * SocialAI Service - 社交账户页面
 */
import { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message, Popconfirm, Card, Row, Col, Statistic } from 'antd';
import { PlusOutlined, SyncOutlined, DisconnectOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { accountsAPI } from '../api';

export default function Accounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [connectModalVisible, setConnectModalVisible] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [platform, setPlatform] = useState('wechat');
  const [isMounted, setIsMounted] = useState(true);

  // 加载账户列表
  const loadAccounts = async () => {
    if (!isMounted) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      console.log('[Accounts] Token exists:', !!token);
      const response = await accountsAPI.list();
      console.log('[Accounts] Response:', response.data);
      if (isMounted) {
        setAccounts(response.data || []);
      }
    } catch (error) {
      console.error('[Accounts] Load error:', error);
      if (isMounted) {
        message.error('加载账户列表失败: ' + (error.response?.data?.detail || error.message));
      }
    } finally {
      if (isMounted) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    setIsMounted(true);
    loadAccounts();
    return () => setIsMounted(false);
  }, []);

  // 连接账户
  const handleConnect = async () => {
    setConnecting(true);
    try {
      // 获取OAuth URL
      const response = await accountsAPI.getOAuthUrl(platform);
      const { url } = response.data;
      
      // 打开OAuth授权页面
      window.open(url, '_blank', 'width=600,height=700');
      
      message.success('请在新窗口中完成授权');
      setConnectModalVisible(false);
      
      // 授权完成后刷新列表
      setTimeout(() => {
        loadAccounts();
      }, 3000);
    } catch (error) {
      message.error('获取授权链接失败');
    } finally {
      setConnecting(false);
    }
  };

  // 断开账户
  const handleDisconnect = async (id) => {
    try {
      await accountsAPI.disconnect(id);
      message.success('已断开连接');
      loadAccounts();
    } catch (error) {
      message.error('断开失败');
    }
  };

  // 刷新Token
  const handleRefresh = async (id) => {
    try {
      await accountsAPI.refreshToken(id);
      message.success('刷新成功');
      loadAccounts();
    } catch (error) {
      message.error('刷新失败，请重新连接');
    }
  };

  // 测试连接
  const handleTest = async (id) => {
    try {
      const response = await accountsAPI.testConnection(id);
      if (response.data.is_connected) {
        message.success('连接正常');
      } else {
        message.warning('连接异常，请重新授权');
      }
    } catch (error) {
      message.error('测试失败');
    }
  };

  const columns = [
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      width: 120,
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
      title: '账户名称',
      dataIndex: 'account_name',
      key: 'account_name',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (active) => (
        <Tag color={active ? 'success' : 'default'}>
          {active ? '已连接' : '未连接'}
        </Tag>
      ),
    },
    {
      title: '连接时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<SyncOutlined />} onClick={() => handleRefresh(record.id)}>
            刷新
          </Button>
          <Button type="link" size="small" onClick={() => handleTest(record.id)}>
            测试
          </Button>
          <Popconfirm title="确定断开此账户?" onConfirm={() => handleDisconnect(record.id)}>
            <Button type="link" size="small" danger>断开</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 统计信息
  const stats = {
    total: accounts.length,
    active: accounts.filter(a => a.is_active).length,
    wechat: accounts.filter(a => a.platform === 'wechat').length,
    linkedin: accounts.filter(a => a.platform === 'linkedin').length,
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1>社交账户</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setConnectModalVisible(true)}>
          连接账户
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总账户数" value={stats.total} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="已连接" value={stats.active} prefix={<CheckCircleOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="微信账户" value={stats.wechat} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="LinkedIn账户" value={stats.linkedin} />
          </Card>
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={accounts}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 20 }}
      />

      {/* 连接账户弹窗 */}
      <Modal
        title="连接社交账户"
        open={connectModalVisible}
        onCancel={() => setConnectModalVisible(false)}
        footer={null}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <p style={{ marginBottom: 20 }}>选择要连接的平台</p>
          <Space>
            <Button 
              type={platform === 'wechat' ? 'primary' : 'default'} 
              onClick={() => setPlatform('wechat')}
              size="large"
            >
              微信
            </Button>
            <Button 
              type={platform === 'linkedin' ? 'primary' : 'default'} 
              onClick={() => setPlatform('linkedin')}
              size="large"
            >
              LinkedIn
            </Button>
          </Space>
          <div style={{ marginTop: 24 }}>
            <Button type="primary" size="large" onClick={handleConnect} loading={connecting}>
              授权连接
            </Button>
          </div>
          <p style={{ marginTop: 16, color: '#888', fontSize: 12 }}>
            点击"授权连接"后，将打开对应平台的授权页面
          </p>
        </div>
      </Modal>
    </div>
  );
}
