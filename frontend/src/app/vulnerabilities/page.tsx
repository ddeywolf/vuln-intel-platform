'use client';

import { useEffect, useState, useCallback } from 'react';
import { VulnTable } from '@/components/vulnerabilities/VulnTable';
import { VulnFilters } from '@/components/vulnerabilities/VulnFilters';
import { Pagination } from '@/components/common/Pagination';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { api, type PaginatedResponse } from '@/lib/api';
import type { Vulnerability, VulnerabilityFilters } from '@/types/vulnerability';

export default function VulnerabilitiesPage() {
  const [data, setData] = useState<PaginatedResponse<Vulnerability> | null>(null);
  const [filters, setFilters] = useState<VulnerabilityFilters>({ page: 1, page_size: 25 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVulnerabilities = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.get<PaginatedResponse<Vulnerability>>(
        '/api/v1/vulnerabilities',
        filters as Record<string, string | number | boolean | undefined | null>,
      );
      setData(result);
    } catch (err) {
      setError('Failed to load vulnerabilities. Is the backend running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchVulnerabilities();
  }, [fetchVulnerabilities]);

  function handleFilterChange(newFilters: VulnerabilityFilters) {
    setFilters({ ...newFilters, page: 1 });
  }

  function handlePageChange(page: number) {
    setFilters((prev) => ({ ...prev, page }));
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-900">Vulnerabilities</h1>

      <VulnFilters filters={filters} onChange={handleFilterChange} />

      {loading && <LoadingSpinner />}
      {error && <p className="rounded bg-red-50 p-4 text-red-700">{error}</p>}

      {!loading && data && (
        <>
          <p className="text-sm text-slate-500">{data.total} total results</p>
          <VulnTable items={data.items} />
          <Pagination
            currentPage={data.page}
            totalPages={data.total_pages}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  );
}
