import { cn } from '@/lib/utils';

type Color = 'blue' | 'red' | 'orange' | 'yellow' | 'green' | 'purple';

const COLOR_MAP: Record<Color, string> = {
  blue: 'bg-blue-50 text-blue-700 ring-blue-200',
  red: 'bg-red-50 text-red-700 ring-red-200',
  orange: 'bg-orange-50 text-orange-700 ring-orange-200',
  yellow: 'bg-yellow-50 text-yellow-700 ring-yellow-200',
  green: 'bg-green-50 text-green-700 ring-green-200',
  purple: 'bg-purple-50 text-purple-700 ring-purple-200',
};

interface StatsCardProps {
  title: string;
  value: number | string;
  color?: Color;
  subtitle?: string;
}

export function StatsCard({ title, value, color = 'blue', subtitle }: StatsCardProps) {
  return (
    <div className={cn('rounded-xl p-4 ring-1', COLOR_MAP[color])}>
      <p className="text-xs font-medium opacity-70">{title}</p>
      <p className="mt-1 text-3xl font-bold">{value.toLocaleString()}</p>
      {subtitle && <p className="mt-0.5 text-xs opacity-60">{subtitle}</p>}
    </div>
  );
}
