import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { apiRequest } from '../../shared/api/client'
import { ErrorState, LoadingState, Page } from '../../shared/ui/Page'

interface Organization { readonly id: string; readonly name: string }
interface EventItem { readonly id: string; readonly name: string; readonly status: string; readonly scheduled_start_at: string; readonly organization: { readonly name: string } }
interface EventList { readonly items: readonly EventItem[] }
export function EventsPage() {
  const client = useQueryClient(); const [showForm, setShowForm] = useState(false)
  const events = useQuery({ queryKey: ['events'], queryFn: () => apiRequest<EventList>('/events?limit=100&statuses=scheduled&statuses=live&statuses=delayed') })
  const organizations = useQuery({ queryKey: ['organizations'], queryFn: () => apiRequest<readonly Organization[]>('/admin/organizations') })
  const create = useMutation({ mutationFn: (body: object) => apiRequest('/admin/events', { method: 'POST', body: JSON.stringify(body) }), onSuccess: async () => { setShowForm(false); await client.invalidateQueries({ queryKey: ['events'] }) } })
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const data = new FormData(event.currentTarget); create.mutate({ organization_id: data.get('organization_id'), name: data.get('name'), slug: data.get('slug'), scheduled_start_at: new Date(String(data.get('scheduled_start_at'))).toISOString() }) }
  if (events.isPending || organizations.isPending) return <LoadingState />
  if (events.error || organizations.error) return <ErrorState error={(events.error ?? organizations.error)!} />
  return <Page title="Events" eyebrow="Catalog" actions={<button className="rounded-lg bg-red-600 px-4 py-2 font-semibold" onClick={() => setShowForm(value => !value)}>{showForm ? 'Close' : 'Create event'}</button>}>{showForm && <form onSubmit={submit} className="mb-6 grid gap-4 rounded-xl border border-zinc-800 bg-zinc-900 p-5 md:grid-cols-2"><label className="text-sm">Organization<select required name="organization_id" className="mt-1 w-full rounded bg-zinc-950 p-3">{organizations.data.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><label className="text-sm">Name<input required name="name" className="mt-1 w-full rounded bg-zinc-950 p-3" /></label><label className="text-sm">Slug<input required name="slug" pattern="[a-z0-9]+(?:-[a-z0-9]+)*" className="mt-1 w-full rounded bg-zinc-950 p-3" /></label><label className="text-sm">Start time<input required name="scheduled_start_at" type="datetime-local" className="mt-1 w-full rounded bg-zinc-950 p-3" /></label>{create.error && <p role="alert" className="text-red-300">{create.error.message}</p>}<button disabled={create.isPending} className="rounded bg-red-600 px-4 py-3 font-semibold md:col-span-2">{create.isPending ? 'Creating…' : 'Create event'}</button></form>}<div className="overflow-x-auto rounded-xl border border-zinc-800"><table className="w-full text-left text-sm"><thead className="bg-zinc-900 text-zinc-400"><tr><th className="p-4">Event</th><th className="p-4">Organization</th><th className="p-4">Start</th><th className="p-4">Status</th></tr></thead><tbody>{events.data.items.map(item => <tr key={item.id} className="border-t border-zinc-800"><td className="p-4 font-medium">{item.name}</td><td className="p-4">{item.organization.name}</td><td className="p-4">{new Date(item.scheduled_start_at).toLocaleString()}</td><td className="p-4"><span className="rounded-full bg-zinc-800 px-2 py-1">{item.status}</span></td></tr>)}</tbody></table></div></Page>
}
