import { cn, severityColor } from '@/lib/utils';

interface SeverityBadgeProps {
  severity: string | null | undefined;
  compact?: boolean;
}

export function SeverityBadge({ severity, compact = false }: SeverityBadgeProps) {
  const label = severity ?? 'UNKNOWN';
  return (
    <span
      className={cn(
        'inline-block rounded font-medium uppercase',
        compact ? 'px-1.5 py-0.5 text-xs' : 'px-2.5 py-1 text-sm',
        severityColor(severity),
      )}
    >
      {label}
    </span>
  );
}
