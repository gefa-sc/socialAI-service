/**
 * SocialAI Service - 通用加载骨架屏组件
 */
import { Skeleton, Table } from 'antd';

// 表格骨架屏列配置
export const tableSkeletonColumns = (count = 4) => 
  Array.from({ length: count }, (_, i) => ({
    key: `skeleton-${i}`,
    render: () => <Skeleton.Input active style={{ width: '100%' }} />,
  }));

// 表格骨架屏数据
export const tableSkeletonData = (rows = 5, cols = 4) =>
  Array.from({ length: rows }, (_, i) => ({
    key: `skeleton-row-${i}`,
    ...Array.from({ length: cols }, (_, j) => ({ [`col-${j}`]: null })),
  }));

// 带骨架屏的表格组件
export function SkeletonTable({ 
  loading, 
  columns, 
  dataSource, 
  rowKey = 'id',
  ...props 
}) {
  // 如果正在加载，显示骨架屏
  if (loading) {
    const skeletonColumns = columns.map((col, i) => ({
      ...col,
      render: () => <Skeleton.Input active style={{ width: col.width || '80%' }} />,
    }));
    
    return (
      <Table
        columns={skeletonColumns}
        dataSource={Array.from({ length: 5 }, (_, i) => ({ key: i }))}
        rowKey="key"
        pagination={false}
        {...props}
      />
    );
  }
  
  // 正常显示
  return (
    <Table
      columns={columns}
      dataSource={dataSource}
      rowKey={rowKey}
      {...props}
    />
  );
}

export default SkeletonTable;
