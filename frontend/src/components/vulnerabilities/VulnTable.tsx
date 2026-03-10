import Link from 'next/link';
import { SeverityBadge } from './SeverityBadge';
import { formatDate, formatScore } from '@/lib/utils';
import type { Vulnerability } from '@/types/vulnerability';

interface VulnTableProps {
  items: Vulnerability[];
}

export function VulnTable({ items }: VulnTableProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-lg bg-white py-12 text-center ring-1 ring-slate-200">
        <p className="text-sm text-slate-400">No vulnerabilities found.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-slate-200">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            {['CVE ID', 'Severity', 'CVSS', 'EPSS', 'Source', 'KEV', 'Exploit', 'Published'].map(
              (h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500"
                >
                  {h}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((v) => (
            <tr key={v.id} className="hover:bg-slate-50">
              <td className="px-4 py-3">
                <Link
                  href={`/vulnerabilities/${v.cve_id}`}
                  className="text-sm font-medium text-blue-700 hover:underline"
                >
                  {v.cve_id}
                </Link>
              </td>
              <td className="px-4 py-3">
                <SeverityBadge severity={v.severity} compact />
              </td>
              <td className="px-4 py-3 text-sm tabular-nums">{formatScore(v.cvss_score)}</td>
              <td className="px-4 py-3 text-sm tabular-nums">
                {v.epss_score !== null
                  ? `${(v.epss_score * 100).toFixed(1)}%`
                  : '—'}
              </td>
              <td className="px-4 py-3 text-xs text-slate-500">{v.source}</td>
              <td className="px-4 py-3">
                {v.cisa_kev ? (
                  <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs text-red-700">
                    KEV
                  </span>
                ) : (
                  <span className="text-slate-300">—</span>
                )}
              </td>
              <td className="px-4 py-3 text-sm">
                {v.exploit_available ? (
                  <span className="text-orange-600">⚠ Yes</span>
                ) : (
                  <span className="text-slate-400">No</span>
                )}
              </td>
              <td className="px-4 py-3 text-sm text-slate-500">
                {formatDate(v.published_date)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
