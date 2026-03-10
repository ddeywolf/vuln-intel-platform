import { StatsCard } from '@/components/dashboard/StatsCard';
import { RecentVulns } from '@/components/dashboard/RecentVulns';
import { SeverityChart } from '@/components/dashboard/SeverityChart';

interface DashboardStats {
  total_vulnerabilities: number;
  critical_count: number;
  high_count: number;
  cisa_kev_count: number;
  exploit_available_count: number;
  assets_monitored: number;
  active_alerts: number;
  severity_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  recent_vulnerabilities: Array<{
    id: number;
    cve_id: string;
    description: string;
    severity: string | null;
    cvss_score: number | null;
    published_date: string | null;
    cisa_kev: boolean;
  }>;
}

async function getDashboardStats(): Promise<DashboardStats | null> {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    const res = await fetch(`${baseUrl}/api/v1/dashboard/stats`, {
      next: { revalidate: 60 }, // revalidate every 60s
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function DashboardPage() {
  const stats = await getDashboardStats();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        <StatsCard
          title="Total Vulnerabilities"
          value={stats?.total_vulnerabilities ?? '—'}
          color="blue"
        />
        <StatsCard
          title="Critical"
          value={stats?.critical_count ?? '—'}
          color="red"
        />
        <StatsCard
          title="High"
          value={stats?.high_count ?? '—'}
          color="orange"
        />
        <StatsCard
          title="CISA KEV"
          value={stats?.cisa_kev_count ?? '—'}
          color="purple"
        />
        <StatsCard
          title="Exploits Known"
          value={stats?.exploit_available_count ?? '—'}
          color="red"
        />
        <StatsCard
          title="Assets Monitored"
          value={stats?.assets_monitored ?? '—'}
          color="green"
        />
        <StatsCard
          title="Active Alerts"
          value={stats?.active_alerts ?? '—'}
          color="yellow"
        />
      </div>

      {/* Charts + recent vulns */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <SeverityChart distribution={stats?.severity_distribution ?? {}} />
        <RecentVulns items={stats?.recent_vulnerabilities ?? []} />
      </div>
    </div>
  );
}
