'use client';

import { useEffect, useState, useCallback } from 'react';
import { api, type PaginatedResponse } from '@/lib/api';
import { Pagination } from '@/components/common/Pagination';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { formatDate } from '@/lib/utils';
import type { Asset } from '@/types/asset';

export default function AssetsPage() {
  const [data, setData] = useState<PaginatedResponse<Asset> | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAssets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.get<PaginatedResponse<Asset>>('/api/v1/assets', {
        page,
        page_size: 25,
      });
      setData(result);
    } catch (err) {
      setError('Failed to load assets.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-900">Asset Inventory</h1>
      <p className="text-sm text-slate-500">
        Track your software inventory and map known vulnerabilities to assets.
      </p>

      {loading && <LoadingSpinner />}
      {error && <p className="rounded bg-red-50 p-4 text-red-700">{error}</p>}

      {!loading && data && (
        <>
          <p className="text-sm text-slate-500">{data.total} assets</p>

          <div className="overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-slate-200">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  {['Name', 'Vendor', 'Version', 'Type', 'CPE', 'Added'].map((h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-sm text-slate-400">
                      No assets found. Add assets via the API.
                    </td>
                  </tr>
                ) : (
                  data.items.map((asset) => (
                    <tr key={asset.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 text-sm font-medium text-slate-900">{asset.name}</td>
                      <td className="px-4 py-3 text-sm text-slate-600">{asset.vendor ?? '—'}</td>
                      <td className="px-4 py-3 text-sm font-mono text-slate-600">
                        {asset.version ?? '—'}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">{asset.asset_type}</td>
                      <td className="max-w-xs truncate px-4 py-3 font-mono text-xs text-slate-400">
                        {asset.cpe ?? '—'}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-500">
                        {formatDate(asset.created_at)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
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
