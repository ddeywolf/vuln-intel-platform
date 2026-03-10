'use client';

import type { VulnerabilityFilters } from '@/types/vulnerability';

interface VulnFiltersProps {
  filters: VulnerabilityFilters;
  onChange: (filters: VulnerabilityFilters) => void;
}

const SEVERITIES = ['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
const SOURCES = ['', 'nvd', 'github', 'osv', 'cisa', 'epss'];

export function VulnFilters({ filters, onChange }: VulnFiltersProps) {
  function update(patch: Partial<VulnerabilityFilters>) {
    onChange({ ...filters, ...patch });
  }

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg bg-white p-3 ring-1 ring-slate-200">
      {/* Search */}
      <input
        type="text"
        placeholder="Search CVE ID or description…"
        value={filters.search ?? ''}
        onChange={(e) => update({ search: e.target.value || undefined })}
        className="flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
      />

      {/* Severity */}
      <select
        value={filters.severity ?? ''}
        onChange={(e) => update({ severity: e.target.value || undefined })}
        className="rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-blue-500 focus:outline-none"
      >
        {SEVERITIES.map((s) => (
          <option key={s} value={s}>
            {s || 'All Severities'}
          </option>
        ))}
      </select>

      {/* Source */}
      <select
        value={filters.source ?? ''}
        onChange={(e) => update({ source: e.target.value || undefined })}
        className="rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-blue-500 focus:outline-none"
      >
        {SOURCES.map((s) => (
          <option key={s} value={s}>
            {s || 'All Sources'}
          </option>
        ))}
      </select>

      {/* KEV toggle */}
      <label className="flex items-center gap-1.5 text-sm text-slate-600">
        <input
          type="checkbox"
          checked={filters.cisa_kev ?? false}
          onChange={(e) => update({ cisa_kev: e.target.checked || undefined })}
          className="rounded"
        />
        CISA KEV only
      </label>

      {/* Exploit toggle */}
      <label className="flex items-center gap-1.5 text-sm text-slate-600">
        <input
          type="checkbox"
          checked={filters.exploit_available ?? false}
          onChange={(e) => update({ exploit_available: e.target.checked || undefined })}
          className="rounded"
        />
        Exploit available
      </label>
    </div>
  );
}
