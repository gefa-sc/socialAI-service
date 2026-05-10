import { Card, Form, Input, Button, Avatar } from 'antd'
import { UserOutlined } from '@ant-design/icons'

export default function Settings() {
  return (
    <div>
      <div className="page-header">
        <h1>账户设置</h1>
      </div>
      <Card title="基本信息" style={{ maxWidth: 600 }}>
        <Form layout="vertical">
          <Form.Item label="头像">
            <Avatar size={64} icon={<UserOutlined />} />
          </Form.Item>
          <Form.Item label="昵称">
            <Input placeholder="请输入昵称" />
          </Form.Item>
          <Form.Item label="邮箱">
            <Input disabled placeholder="邮箱" />
          </Form.Item>
          <Form.Item>
            <Button type="primary">保存</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
