/**
 * SocialAI Service - 轻量级趋势图表组件
 * 不依赖第三方图表库，使用纯 CSS/SVG 实现
 */
import { useMemo } from 'react';
import './TrendChart.css';

export function TrendChart({ 
  data = [], 
  dataKey = 'value',
  height = 300,
  color = '#1890ff',
  showArea = true,
  showDot = true,
  formatValue = (v) => v,
}) {
  // 计算图表数据
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return null;
    
    const values = data.map(d => d[dataKey] || 0);
    const max = Math.max(...values, 1);
    const min = Math.min(...values, 0);
    const range = max - min || 1;
    
    // 生成路径点
    const points = data.map((d, i) => {
      const x = (i / (data.length - 1)) * 100;
      const y = 100 - ((d[dataKey] || 0) - min) / range * 100;
      return { x, y, ...d };
    });
    
    // 生成折线路径
    const linePath = points.map((p, i) => 
      `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
    ).join(' ');
    
    // 生成区域路径
    const areaPath = showArea 
      ? `${linePath} L 100 100 L 0 100 Z`
      : '';
    
    return { points, linePath, areaPath, max, min };
  }, [data, dataKey, showArea]);

  if (!chartData || data.length === 0) {
    return (
      <div 
        style={{ 
          height, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: '#999' 
        }}
      >
        暂无数据
      </div>
    );
  }

  return (
    <div className="trend-chart" style={{ height }}>
      {/* Y轴标签 */}
      <div className="chart-y-axis">
        <span>{formatValue(chartData.max)}</span>
        <span>{formatValue((chartData.max + chartData.min) / 2)}</span>
        <span>{formatValue(chartData.min)}</span>
      </div>
      
      {/* 图表区域 */}
      <div className="chart-content">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none">
          {/* 区域填充 */}
          {showArea && (
            <path 
              d={chartData.areaPath} 
              fill={color} 
              fillOpacity="0.1"
            />
          )}
          
          {/* 折线 */}
          <path 
            d={chartData.linePath} 
            fill="none" 
            stroke={color}
            strokeWidth="0.5"
            vectorEffect="non-scaling-stroke"
          />
          
          {/* 数据点 */}
          {showDot && chartData.points.map((p, i) => (
            <circle
              key={i}
              cx={p.x}
              cy={p.y}
              r="1"
              fill={color}
            />
          ))}
        </svg>
        
        {/* X轴标签 */}
        <div className="chart-x-axis">
          {data.map((d, i) => (
            <span key={i}>
              {d.date || d.label || d.name || i}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

// 简化折线图组件
export function SimpleLineChart({ 
  data = [], 
  height = 200,
  color = '#1890ff',
  title,
  valueKey = 'value',
  labelKey = 'label',
}) {
  const chartData = useMemo(() => {
    if (!data.length) return null;
    const values = data.map(d => d[valueKey] || 0);
    const max = Math.max(...values, 1);
    return { max, data: data.map((d, i) => ({
      ...d,
      percent: (d[valueKey] || 0) / max * 100
    }))};
  }, [data, valueKey]);

  if (!chartData) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>暂无数据</div>;
  }

  return (
    <div style={{ height }}>
      {title && <div style={{ marginBottom: 8, fontWeight: 500 }}>{title}</div>}
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: height - 30 }}>
        {chartData.data.map((item, i) => (
          <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div 
              style={{ 
                width: '80%', 
                height: `${item.percent}%`, 
                minHeight: 4,
                background: color, 
                borderRadius: 2,
                transition: 'height 0.3s'
              }} 
              title={`${item[labelKey]}: ${item[valueKey]}`}
            />
            <div style={{ fontSize: 10, marginTop: 4, color: '#666' }}>
              {item[labelKey]}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TrendChart;
