'use client';

import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: '#dc2626',
  HIGH: '#ea580c',
  MEDIUM: '#d97706',
  LOW: '#65a30d',
  NONE: '#6b7280',
  UNKNOWN: '#94a3b8',
};

interface SeverityChartProps {
  distribution: Record<string, number>;
}

export function SeverityChart({ distribution }: SeverityChartProps) {
  const data = Object.entries(distribution).map(([name, value]) => ({ name, value }));

  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl bg-white ring-1 ring-slate-200">
        <p className="text-sm text-slate-400">No data available</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl bg-white p-4 ring-1 ring-slate-200">
      <h2 className="mb-4 font-semibold text-slate-700">Severity Distribution</h2>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((entry) => (
              <Cell
                key={entry.name}
                fill={SEVERITY_COLORS[entry.name] ?? '#94a3b8'}
              />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => value.toLocaleString()} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
