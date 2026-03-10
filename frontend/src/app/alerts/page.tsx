'use client';

import { useEffect, useState, useCallback } from 'react';
import { api, type PaginatedResponse } from '@/lib/api';
import { Pagination } from '@/components/common/Pagination';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { formatDate } from '@/lib/utils';
import type { Alert } from '@/types/alert';

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: 'bg-red-100 text-red-700',
  HIGH: 'bg-orange-100 text-orange-700',
  MEDIUM: 'bg-yellow-100 text-yellow-700',
  LOW: 'bg-green-100 text-green-700',
};

export default function AlertsPage() {
  const [data, setData] = useState<PaginatedResponse<Alert> | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.get<PaginatedResponse<Alert>>('/api/v1/alerts', {
        page,
        page_size: 25,
      });
      setData(result);
    } catch (err) {
      setError('Failed to load alerts.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-900">Alert Rules</h1>
      <p className="text-sm text-slate-500">
        Configure rules to be notified when new vulnerabilities match your criteria.
      </p>

      {loading && <LoadingSpinner />}
      {error && <p className="rounded bg-red-50 p-4 text-red-700">{error}</p>}

      {!loading && data && (
        <>
          <p className="text-sm text-slate-500">{data.total} alert rules</p>

          <div className="space-y-3">
            {data.items.length === 0 ? (
              <div className="rounded-lg bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
                <p className="text-slate-400">No alert rules configured yet. Create one via the API.</p>
              </div>
            ) : (
              data.items.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center justify-between rounded-lg bg-white p-4 shadow-sm ring-1 ring-slate-200"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900">{alert.name}</span>
                      {alert.severity_threshold && (
                        <span
                          className={`rounded px-2 py-0.5 text-xs font-medium ${
                            SEVERITY_COLORS[alert.severity_threshold] ?? 'bg-gray-100 text-gray-600'
                          }`}
                        >
                          {alert.severity_threshold}+
                        </span>
                      )}
                      <span
                        className={`rounded px-2 py-0.5 text-xs ${
                          alert.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        {alert.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    {alert.description && (
                      <p className="mt-1 text-sm text-slate-500">{alert.description}</p>
                    )}
                    <p className="mt-1 text-xs text-slate-400">
                      Channel: {alert.notification_channel}
                      {alert.last_triggered_at &&
                        ` · Last triggered: ${formatDate(alert.last_triggered_at)}`}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>

          <Pagination
            currentPage={data.page}
            totalPages={data.total_pages}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
