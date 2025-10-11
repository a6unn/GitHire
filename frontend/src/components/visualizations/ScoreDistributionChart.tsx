import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Card } from '../ui/Card';

export interface ScoreDistributionChartProps {
  scores: number[];
  className?: string;
}

export const ScoreDistributionChart: React.FC<ScoreDistributionChartProps> = ({
  scores,
  className,
}) => {
  // Create distribution buckets
  const buckets = [
    { range: '0-20', min: 0, max: 20, count: 0, color: '#ef4444' },
    { range: '21-40', min: 21, max: 40, count: 0, color: '#f97316' },
    { range: '41-60', min: 41, max: 60, count: 0, color: '#eab308' },
    { range: '61-80', min: 61, max: 80, count: 0, color: '#22c55e' },
    { range: '81-100', min: 81, max: 100, count: 0, color: '#10b981' },
  ];

  // Distribute scores into buckets
  scores.forEach((score) => {
    const bucket = buckets.find((b) => score >= b.min && score <= b.max);
    if (bucket) bucket.count++;
  });

  const data = buckets.map((bucket) => ({
    name: bucket.range,
    count: bucket.count,
    color: bucket.color,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-3 py-2 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-medium text-gray-900">
            Score Range: {payload[0].payload.name}
          </p>
          <p className="text-sm text-gray-600">
            Candidates: {payload[0].value}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card variant="elevated" padding="lg" className={className}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Score Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="name"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#e5e7eb' }}
          />
          <YAxis
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#e5e7eb' }}
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99, 102, 241, 0.1)' }} />
          <Bar dataKey="count" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default ScoreDistributionChart;
