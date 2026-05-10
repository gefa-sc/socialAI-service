/**
 * SocialAI Service - 空状态组件
 * 数据为空时显示友好提示
 */
import { Empty, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

export function EmptyState({ 
  title = "暂无数据", 
  description, 
  actionText, 
  onAction,
  icon 
}) {
  return (
    <Empty
      image={icon || Empty.PRESENTED_IMAGE_SIMPLE}
      description={
        <div>
          <div style={{ fontSize: 14, color: '#666', marginBottom: 4 }}>
            {title}
          </div>
          {description && (
            <div style={{ fontSize: 12, color: '#999' }}>
              {description}
            </div>
          )}
        </div>
      }
    >
      {actionText && onAction && (
        <Button type="primary" icon={<PlusOutlined />} onClick={onAction}>
          {actionText}
        </Button>
      )}
    </Empty>
  );
}

export default EmptyState;
