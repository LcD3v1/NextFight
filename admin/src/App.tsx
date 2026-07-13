import { Activity, Bell, CalendarDays, Gauge, Menu, ScrollText, Swords, Users, X } from 'lucide-react'
import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

const navigation = [
  { label: 'Dashboard', to: '/', icon: Gauge },
  { label: 'Events', to: '/events', icon: CalendarDays },
  { label: 'Live monitor', to: '/live', icon: Activity },
  { label: 'Fights', to: '/fights', icon: Swords },
  { label: 'Users', to: '/users', icon: Users },
  { label: 'Alerts', to: '/alerts', icon: Bell },
  { label: 'Audit logs', to: '/audit-logs', icon: ScrollText },
]

export function AppLayout() {
  const [open, setOpen] = useState(false)
  return <div className="min-h-screen bg-zinc-950 text-zinc-100">
    <a href="#content" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-red-600 focus:p-3">Skip to content</a>
    <header className="sticky top-0 z-30 flex h-16 items-center border-b border-zinc-800 bg-zinc-950/95 px-4 backdrop-blur lg:pl-72">
      <button type="button" className="rounded p-2 lg:hidden" aria-label="Open navigation" onClick={() => setOpen(true)}><Menu /></button>
      <div className="ml-auto text-sm text-zinc-400">Operational console</div>
    </header>
    <aside className={`${open ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-40 w-64 border-r border-zinc-800 bg-zinc-950 p-4 transition-transform lg:translate-x-0`} aria-label="Primary navigation">
      <div className="mb-8 flex items-center justify-between"><strong className="text-xl">Next<span className="text-red-500">Fight</span></strong><button type="button" className="p-2 lg:hidden" aria-label="Close navigation" onClick={() => setOpen(false)}><X /></button></div>
      <nav className="space-y-1">{navigation.map(({ label, to, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} onClick={() => setOpen(false)} className={({ isActive }) => `flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm ${isActive ? 'bg-red-600 text-white' : 'text-zinc-400 hover:bg-zinc-900 hover:text-white'}`}><Icon size={18} aria-hidden="true" />{label}</NavLink>)}</nav>
    </aside>
    <main id="content" className="p-6 lg:ml-64 lg:p-8"><Outlet /></main>
  </div>
}

export function FoundationPage({ title }: { readonly title: string }) {
  return <section aria-labelledby="page-title"><p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-red-500">Foundation</p><h1 id="page-title" className="text-3xl font-bold">{title}</h1><div className="mt-8 rounded-xl border border-zinc-800 bg-zinc-900/50 p-8 text-zinc-400">This area is ready for API integration. No production data is available yet.</div></section>
}
