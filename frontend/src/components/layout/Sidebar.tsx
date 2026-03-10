'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/vulnerabilities', label: 'Vulnerabilities', icon: '🔍' },
  { href: '/assets', label: 'Assets', icon: '📦' },
  { href: '/alerts', label: 'Alerts', icon: '🔔' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-56 flex-col bg-slate-900 text-slate-100">
      {/* Brand */}
      <div className="flex items-center gap-2 px-4 py-5 font-bold">
        <span className="text-xl">🛡️</span>
        <span className="text-sm leading-tight">
          Vuln Intel
          <br />
          <span className="text-xs font-normal text-slate-400">Platform</span>
        </span>
      </div>

      <nav className="flex-1 space-y-1 px-2 pb-4">
        {NAV_ITEMS.map(({ href, label, icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                active
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white',
              )}
            >
              <span>{icon}</span>
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-slate-700 px-4 py-3 text-xs text-slate-500">v1.0.0</div>
    </aside>
  );
}
