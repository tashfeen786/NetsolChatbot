import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = [
  '#6366f1', '#8b5cf6', '#06b6d4', '#10b981',
  '#f59e0b', '#ef4444', '#ec4899', '#84cc16',
  '#f97316', '#14b8a6',
];

const formatValue = (v) => {
  if (typeof v !== 'number') return v;
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000)     return `${(v / 1_000).toFixed(0)}K`;
  return v.toLocaleString();
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-3 py-2 text-sm">
      <p className="font-semibold text-gray-700 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }} className="text-xs">
          {p.name}: <span className="font-medium">{p.value?.toLocaleString()}</span>
        </p>
      ))}
    </div>
  );
};

export default function ChartMessage({ chartData }) {
  const { type = 'bar', title, data, xKey = 'name', yKey = 'value' } = chartData;
  if (!data || data.length === 0) return null;

  // Dynamic height based on data size
  const chartHeight = type === 'pie' ? 320 : Math.max(280, Math.min(380, data.length * 40));
  // Extra bottom margin for long labels
  const xAxisHeight = data.some(d => String(d[xKey]).length > 8) ? 70 : 40;

  const renderChart = () => {
    if (type === 'pie') {
      return (
        <PieChart>
          <Pie
            data={data}
            dataKey={yKey}
            nameKey={xKey}
            cx="50%"
            cy="50%"
            outerRadius={110}
            innerRadius={50}
            paddingAngle={3}
            label={({ name, percent }) =>
              percent > 0.05 ? `${(percent * 100).toFixed(0)}%` : ''
            }
            labelLine={false}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(v) => v.toLocaleString()}
            contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
          />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span className="text-xs text-gray-600">{value}</span>
            )}
          />
        </PieChart>
      );
    }

    if (type === 'line') {
      return (
        <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: xAxisHeight }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 11, fill: '#6b7280' }}
            angle={-35}
            textAnchor="end"
            height={xAxisHeight}
            interval={0}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6b7280' }}
            tickFormatter={formatValue}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ paddingTop: '12px' }} />
          <Line
            type="monotone"
            dataKey={yKey}
            stroke="#6366f1"
            strokeWidth={2.5}
            dot={{ r: 4, fill: '#6366f1', strokeWidth: 2, stroke: '#fff' }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      );
    }

    // Bar chart (default)
    return (
      <BarChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: xAxisHeight }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={{ fontSize: 11, fill: '#6b7280' }}
          angle={data.length > 5 ? -35 : 0}
          textAnchor={data.length > 5 ? 'end' : 'middle'}
          height={xAxisHeight}
          interval={0}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 11, fill: '#6b7280' }}
          tickFormatter={formatValue}
          width={60}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f3f4f6' }} />
        <Bar dataKey={yKey} radius={[6, 6, 0, 0]} maxBarSize={56}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    );
  };

  return (
    <div className="mt-4 bg-white border border-gray-100 rounded-2xl p-5 shadow-sm w-full">
      {title && (
        <h3 className="text-sm font-semibold text-gray-800 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={chartHeight}>
        {renderChart()}
      </ResponsiveContainer>
    </div>
  );
}