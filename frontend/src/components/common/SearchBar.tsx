'use client';

import { useRouter } from 'next/navigation';
import { useState, type FormEvent } from 'react';

export function SearchBar() {
  const router = useRouter();
  const [query, setQuery] = useState('');

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/vulnerabilities?search=${encodeURIComponent(query.trim())}`);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <input
        type="search"
        placeholder="Search CVE ID…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-56 rounded-lg border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
      />
      <button
        type="submit"
        className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
      >
        Search
      </button>
    </form>
  );
}
