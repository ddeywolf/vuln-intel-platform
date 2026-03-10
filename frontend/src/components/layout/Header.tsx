import Link from 'next/link';
import { SearchBar } from '@/components/common/SearchBar';

export function Header() {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
      <SearchBar />
      <Link
        href="/login"
        className="rounded-lg px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100"
      >
        Sign In
      </Link>
    </header>
  );
}
