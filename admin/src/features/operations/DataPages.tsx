import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { apiRequest } from '../../shared/api/client'
import { ErrorState, LoadingState, Page } from '../../shared/ui/Page'

interface UserRow { readonly id: string; readonly email: string; readonly display_name: string; readonly locale: string; readonly status: string; readonly role: string; readonly created_at: string }
interface DeliveryRow { readonly id: string; readonly status: string; readonly attempts: number; readonly error_code: string | null; readonly attempted_at: string | null; readonly created_at: string }
interface AuditRow { readonly id: string; readonly action: string; readonly entity_type: string; readonly actor_user_id: string; readonly created_at: string }
interface DispatchResult { readonly queued: number }

function DataTable({ headers, rows }: { readonly headers: readonly string[]; readonly rows: readonly (readonly ReactNode[])[] }) {
  return <div className="overflow-x-auto rounded-xl border border-zinc-800"><table className="w-full text-left text-sm"><thead className="bg-zinc-900 text-zinc-400"><tr>{headers.map(item => <th key={item} className="p-4">{item}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index} className="border-t border-zinc-800">{row.map((cell, cellIndex) => <td key={cellIndex} className="p-4">{cell}</td>)}</tr>)}</tbody></table></div>
}

export function UsersPage() {
  const query = useQuery({ queryKey: ['admin-users'], queryFn: () => apiRequest<readonly UserRow[]>('/admin/users') })
  if (query.isPending) return <LoadingState />
  if (query.error) return <ErrorState error={query.error} />
  return <Page title="Users" eyebrow="Operations"><DataTable headers={['Name', 'Email', 'Locale', 'Role', 'Status']} rows={query.data.map(item => [item.display_name, item.email, item.locale, item.role, item.status])} /></Page>
}

export function DeliveriesPage() {
  const client = useQueryClient()
  const [showDispatch, setShowDispatch] = useState(false)
  const query = useQuery({ queryKey: ['deliveries'], queryFn: () => apiRequest<readonly DeliveryRow[]>('/admin/deliveries') })
  const dispatch = useMutation({
    mutationFn: (body: object) => apiRequest<DispatchResult>('/admin/alerts/dispatch', { method: 'POST', body: JSON.stringify(body) }),
    onSuccess: async () => { await client.invalidateQueries({ queryKey: ['deliveries'] }) },
  })
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    dispatch.mutate({ alert_id: data.get('alert_id'), idempotency_key: crypto.randomUUID(), title: data.get('title'), body: data.get('body') })
  }
  if (query.isPending) return <LoadingState />
  if (query.error) return <ErrorState error={query.error} />
  return <Page title="Alert deliveries" eyebrow="Push health" actions={<button className="rounded-lg bg-red-600 px-4 py-2 font-semibold" onClick={() => setShowDispatch(value => !value)}>{showDispatch ? 'Close' : 'Manual dispatch'}</button>}>
    {showDispatch && <form onSubmit={submit} className="mb-6 grid gap-4 rounded-xl border border-zinc-800 bg-zinc-900 p-5">
      <label className="text-sm">Alert ID<input required name="alert_id" pattern="[0-9a-fA-F-]{36}" className="mt-1 w-full rounded bg-zinc-950 p-3" /></label>
      <label className="text-sm">Title<input required maxLength={180} name="title" className="mt-1 w-full rounded bg-zinc-950 p-3" /></label>
      <label className="text-sm">Message<textarea required maxLength={500} name="body" rows={3} className="mt-1 w-full rounded bg-zinc-950 p-3" /></label>
      {dispatch.error && <p role="alert" className="text-red-300">{dispatch.error.message}</p>}
      {dispatch.data && <p role="status" className="text-emerald-300">Queued for {dispatch.data.queued} enabled device(s).</p>}
      <button disabled={dispatch.isPending} className="rounded bg-red-600 px-4 py-3 font-semibold">{dispatch.isPending ? 'Queuing...' : 'Queue alert'}</button>
    </form>}
    <DataTable headers={['Created', 'Status', 'Attempts', 'Error']} rows={query.data.map(item => [new Date(item.created_at).toLocaleString(), item.status, String(item.attempts), item.error_code ?? '—'])} />
  </Page>
}

export function AuditLogsPage() {
  const query = useQuery({ queryKey: ['audit'], queryFn: () => apiRequest<readonly AuditRow[]>('/admin/audit-logs?limit=100') })
  if (query.isPending) return <LoadingState />
  if (query.error) return <ErrorState error={query.error} />
  return <Page title="Audit logs" eyebrow="Security"><DataTable headers={['Time', 'Action', 'Entity', 'Actor']} rows={query.data.map(item => [new Date(item.created_at).toLocaleString(), item.action, item.entity_type, item.actor_user_id])} /></Page>
}
