import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = ['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b',
                '#ef4444','#ec4899','#84cc16','#f97316','#14b8a6'];

export default function ChartMessage({ chartData }) {
  const { type, title, data, xKey = 'name', yKey = 'value' } = chartData;

  if (!data || data.length === 0) return null;

  const renderChart = () => {
    if (type === 'pie') {
      return (
        <PieChart>
          <Pie data={data} dataKey={yKey} nameKey={xKey}
               cx="50%" cy="50%" outerRadius={100} label={({name, percent}) =>
                 `${name} ${(percent*100).toFixed(0)}%`}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v) => v.toLocaleString()} />
          <Legend />
        </PieChart>
      );
    }
    if (type === 'line') {
      return (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }}
                 tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
          <Tooltip formatter={(v) => v.toLocaleString()} />
          <Legend />
          <Line type="monotone" dataKey={yKey} stroke="#6366f1"
                strokeWidth={2} dot={{ r: 4 }} />
        </LineChart>
      );
    }
    // default: bar
    return (
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11 }}
               angle={data.length > 6 ? -30 : 0}
               textAnchor={data.length > 6 ? 'end' : 'middle'}
               height={data.length > 6 ? 60 : 30} />
        <YAxis tick={{ fontSize: 12 }}
               tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
        <Tooltip formatter={(v) => v.toLocaleString()} />
        <Legend />
        <Bar dataKey={yKey} radius={[4,4,0,0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    );
  };

  return (
    <div className="mt-3 bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
      {title && (
        <h3 className="text-sm font-semibold text-gray-700 mb-3">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={280}>
        {renderChart()}
      </ResponsiveContainer>
    </div>
  );
}