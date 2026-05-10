/**
 * SocialAI Service - 数据分析页面
 */
import { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Select, DatePicker, Table, Tabs, Spin, Empty } from 'antd';
import { EyeOutlined, LikeOutlined, MessageOutlined, ShareAltOutlined, RiseOutlined } from '@ant-design/icons';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { analyticsAPI } from '../api';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { TabPane } = Tabs;

export default function Analytics() {
  const [loading, setLoading] = useState(false);
  const [overview, setOverview] = useState(null);
  const [trends, setTrends] = useState([]);
  const [accountsAnalytics, setAccountsAnalytics] = useState([]);
  const [period, setPeriod] = useState('daily');
  const [days, setDays] = useState(30);

  // 加载概览数据
  const loadOverview = async () => {
    setLoading(true);
    try {
      const response = await analyticsAPI.getOverview(days);
      setOverview(response.data);
    } catch (error) {
      console.error('加载概览失败', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载趋势数据
  const loadTrends = async () => {
    try {
      const response = await analyticsAPI.getTrends(period, days);
      setTrends(response.data.data || []);
    } catch (error) {
      console.error('加载趋势失败', error);
    }
  };

  // 加载账户分析
  const loadAccountsAnalytics = async () => {
    try {
      const response = await analyticsAPI.getAccountsAnalytics();
      setAccountsAnalytics(response.data || []);
    } catch (error) {
      console.error('加载账户分析失败', error);
    }
  };

  useEffect(() => {
    loadOverview();
    loadTrends();
    loadAccountsAnalytics();
  }, [days, period]);

  const accountColumns = [
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform) => {
        const map = {
          wechat: '微信',
          linkedin: 'LinkedIn',
        };
        return map[platform] || platform;
      },
    },
    {
      title: '账户名称',
      dataIndex: 'account_name',
      key: 'account_name',
    },
    {
      title: '发布数',
      dataIndex: 'total_published',
      key: 'total_published',
    },
    {
      title: '曝光量',
      dataIndex: 'total_impressions',
      key: 'total_impressions',
    },
    {
      title: '互动量',
      dataIndex: 'total_engagements',
      key: 'total_engagements',
    },
    {
      title: '互动率',
      dataIndex: 'avg_engagement_rate',
      key: 'avg_engagement_rate',
      render: (val) => `${val}%`,
    },
  ];

  const trendColumns = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: '发布数',
      dataIndex: 'published_count',
      key: 'published_count',
    },
    {
      title: '曝光量',
      dataIndex: 'impressions',
      key: 'impressions',
    },
    {
      title: '互动量',
      dataIndex: 'engagements',
      key: 'engagements',
    },
  ];

  return (
    <Spin spinning={loading}>
      <div>
        <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h1>数据分析</h1>
          <Select value={days} onChange={setDays} style={{ width: 120 }}>
            <Option value={7}>最近7天</Option>
            <Option value={30}>最近30天</Option>
            <Option value={90}>最近90天</Option>
          </Select>
        </div>

        {/* 概览卡片 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总内容数"
                value={overview?.total_contents || 0}
                prefix={<EyeOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="已发布"
                value={overview?.total_published || 0}
                prefix={<ShareAltOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总曝光量"
                value={overview?.total_impressions || 0}
                prefix={<EyeOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总互动量"
                value={overview?.total_engagements || 0}
                prefix={<LikeOutlined />}
                suffix={`(${overview?.engagement_rate || 0}%)`}
              />
            </Card>
          </Col>
        </Row>

        {/* Tab切换 */}
        <Card>
          <Tabs defaultActiveKey="trends" onChange={(key) => {
            if (key === 'trends') loadTrends();
            if (key === 'accounts') loadAccountsAnalytics();
          }}>
            <TabPane tab="趋势分析" key="trends">
              <div style={{ marginBottom: 16 }}>
                <Select value={period} onChange={setPeriod} style={{ width: 120 }}>
                  <Option value="daily">按天</Option>
                  <Option value="weekly">按周</Option>
                  <Option value="monthly">按月</Option>
                </Select>
              </div>
              
              {/* 趋势图表 */}
              {trends.length > 0 ? (
                <>
                  <Card title="发布趋势" style={{ marginBottom: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={trends}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="published_count" name="发布数" stroke="#1890ff" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </Card>
                  
                  <Card title="互动趋势" style={{ marginBottom: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={trends}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="impressions" name="曝光量" fill="#52c41a" />
                        <Bar dataKey="engagements" name="互动量" fill="#faad14" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>
                </>
              ) : (
                <Empty description="暂无趋势数据，请先创建内容并发布" />
              )}
              
              <h3>趋势明细</h3>
              <Table
                columns={trendColumns}
                dataSource={trends}
                rowKey="date"
                pagination={false}
                size="small"
              />
            </TabPane>
            <TabPane tab="账户分析" key="accounts">
              {accountsAnalytics.length > 0 ? (
                <Card title="各平台发布统计" style={{ marginBottom: 16 }}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={accountsAnalytics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="platform" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="total_published" name="发布数" fill="#1890ff" />
                      <Bar dataKey="total_impressions" name="曝光量" fill="#52c41a" />
                      <Bar dataKey="total_engagements" name="互动量" fill="#faad14" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              ) : (
                <Empty description="暂无账户数据，请先绑定社交账户" />
              )}
              
              <h3>账户明细</h3>
              <Table
                columns={accountColumns}
                dataSource={accountsAnalytics}
                rowKey="account_id"
                pagination={false}
                size="small"
              />
            </TabPane>
          </Tabs>
        </Card>
      </div>
    </Spin>
  );
}
