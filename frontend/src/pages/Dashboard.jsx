import { Card, Row, Col, Statistic } from 'antd'

export default function Dashboard() {
  return (
    <div>
      <div className="page-header">
        <h1>数据概览</h1>
      </div>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic title="总内容数" value={0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="已发布" value={0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="总曝光量" value={0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="总互动量" value={0} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
