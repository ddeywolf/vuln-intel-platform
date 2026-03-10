import Link from 'next/link';
import { SeverityBadge } from '@/components/vulnerabilities/SeverityBadge';
import { formatDate } from '@/lib/utils';

interface RecentVuln {
  id: number;
  cve_id: string;
  description: string;
  severity: string | null;
  cvss_score: number | null;
  published_date: string | null;
  cisa_kev: boolean;
}

interface RecentVulnsProps {
  items: RecentVuln[];
}

export function RecentVulns({ items }: RecentVulnsProps) {
  return (
    <div className="rounded-xl bg-white p-4 ring-1 ring-slate-200">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold text-slate-700">Recent Vulnerabilities</h2>
        <Link href="/vulnerabilities" className="text-xs text-blue-600 hover:underline">
          View all →
        </Link>
      </div>

      {items.length === 0 ? (
        <p className="py-4 text-center text-sm text-slate-400">No vulnerabilities ingested yet.</p>
      ) : (
        <ul className="space-y-3">
          {items.map((v) => (
            <li key={v.id} className="flex items-start gap-3">
              <SeverityBadge severity={v.severity} compact />
              <div className="min-w-0 flex-1">
                <Link
                  href={`/vulnerabilities/${v.cve_id}`}
                  className="text-sm font-medium text-blue-700 hover:underline"
                >
                  {v.cve_id}
                </Link>
                {v.cisa_kev && (
                  <span className="ml-2 rounded bg-red-100 px-1 py-0.5 text-xs text-red-700">
                    KEV
                  </span>
                )}
                <p className="truncate text-xs text-slate-500">{v.description}</p>
              </div>
              <span className="shrink-0 text-xs text-slate-400">
                {formatDate(v.published_date)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
