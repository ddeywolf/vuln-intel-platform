import { notFound } from 'next/navigation';
import { SeverityBadge } from '@/components/vulnerabilities/SeverityBadge';
import { formatDate, formatScore, formatEpss } from '@/lib/utils';
import type { Vulnerability } from '@/types/vulnerability';

interface Props {
  params: Promise<{ id: string }>;
}

async function getVulnerability(cveId: string): Promise<Vulnerability | null> {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    const res = await fetch(`${baseUrl}/api/v1/vulnerabilities/${cveId}`, {
      next: { revalidate: 300 },
    });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    return null;
  }
}

export default async function VulnerabilityDetailPage({ params }: Props) {
  const { id } = await params;
  const vuln = await getVulnerability(id);
  if (!vuln) notFound();

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{vuln.cve_id}</h1>
          <p className="mt-1 text-sm text-slate-500">Source: {vuln.source.toUpperCase()}</p>
        </div>
        <SeverityBadge severity={vuln.severity} />
      </div>

      {/* Description */}
      {vuln.description && (
        <div className="rounded-lg bg-white p-4 shadow-sm ring-1 ring-slate-200">
          <h2 className="mb-2 font-semibold text-slate-700">Description</h2>
          <p className="text-sm text-slate-600">{vuln.description}</p>
        </div>
      )}

      {/* Scores */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <ScoreCard label="CVSS Score" value={formatScore(vuln.cvss_score)} />
        <ScoreCard label="EPSS Score" value={formatEpss(vuln.epss_score)} />
        <ScoreCard label="Risk Score" value={formatScore(vuln.risk_score)} />
        <ScoreCard
          label="Exploit Available"
          value={vuln.exploit_available ? 'Yes' : 'No'}
          highlight={vuln.exploit_available}
        />
      </div>

      {/* KEV status */}
      {vuln.cisa_kev && (
        <div className="rounded-lg bg-red-50 p-4 ring-1 ring-red-200">
          <p className="font-semibold text-red-700">
            ⚠️ CISA Known Exploited Vulnerability
            {vuln.cisa_kev_date_added && ` — Added ${formatDate(vuln.cisa_kev_date_added)}`}
          </p>
        </div>
      )}

      {/* Dates */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-slate-400">Published</p>
          <p className="text-sm font-medium">{formatDate(vuln.published_date)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-400">Last Modified</p>
          <p className="text-sm font-medium">{formatDate(vuln.modified_date)}</p>
        </div>
      </div>

      {/* Affected Products */}
      {vuln.affected_products && vuln.affected_products.length > 0 && (
        <div className="rounded-lg bg-white p-4 shadow-sm ring-1 ring-slate-200">
          <h2 className="mb-3 font-semibold text-slate-700">Affected Products</h2>
          <ul className="space-y-1">
            {vuln.affected_products.map((p, i) => (
              <li key={i} className="text-sm text-slate-600">
                {p.package && <span className="font-mono">{p.package}</span>}
                {p.ecosystem && <span className="text-slate-400"> ({p.ecosystem})</span>}
                {p.vulnerable_range && (
                  <span className="ml-2 text-xs text-slate-400">{p.vulnerable_range}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* References */}
      {vuln.references && vuln.references.length > 0 && (
        <div className="rounded-lg bg-white p-4 shadow-sm ring-1 ring-slate-200">
          <h2 className="mb-3 font-semibold text-slate-700">References</h2>
          <ul className="space-y-1">
            {vuln.references.slice(0, 15).map((ref, i) => (
              <li key={i}>
                <a
                  href={ref.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                >
                  {ref.url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ScoreCard({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-lg p-3 shadow-sm ring-1 ${
        highlight ? 'bg-red-50 ring-red-200' : 'bg-white ring-slate-200'
      }`}
    >
      <p className="text-xs text-slate-400">{label}</p>
      <p className={`text-lg font-bold ${highlight ? 'text-red-700' : 'text-slate-900'}`}>
        {value}
      </p>
    </div>
  );
}
