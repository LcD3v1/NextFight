import { useQuery } from '@tanstack/react-query'
import { Activity, BellRing, CircleAlert, Users } from 'lucide-react'
import { apiRequest } from '../../shared/api/client'
import { ErrorState, LoadingState, Page } from '../../shared/ui/Page'

interface Dashboard { readonly live_events: number; readonly active_users: number; readonly pending_deliveries: number; readonly failed_deliveries: number }
export function DashboardPage() {
  const query = useQuery({ queryKey: ['dashboard'], queryFn: () => apiRequest<Dashboard>('/admin/dashboard'), refetchInterval: 15_000 })
  if (query.isPending) return <LoadingState />
  if (query.error) return <ErrorState error={query.error} />
  const cards = [{ label: 'Live events', value: query.data.live_events, icon: Activity }, { label: 'Active users', value: query.data.active_users, icon: Users }, { label: 'Pending pushes', value: query.data.pending_deliveries, icon: BellRing }, { label: 'Failed pushes', value: query.data.failed_deliveries, icon: CircleAlert }]
  return <Page title="Operational overview" eyebrow="Live system"><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{cards.map(({ label, value, icon: Icon }) => <article key={label} className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-5"><div className="flex items-center justify-between text-zinc-400"><span className="text-sm">{label}</span><Icon size={20} aria-hidden /></div><strong className="mt-4 block text-4xl tabular-nums">{value}</strong></article>)}</div></Page>
}
