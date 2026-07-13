import type { ReactNode } from 'react'

export function Page({ title, eyebrow, actions, children }: { readonly title: string; readonly eyebrow?: string; readonly actions?: ReactNode; readonly children: ReactNode }) {
  return <section aria-labelledby="page-title"><div className="flex flex-wrap items-end justify-between gap-4"><div>{eyebrow && <p className="mb-2 text-xs font-semibold uppercase tracking-[.2em] text-red-500">{eyebrow}</p>}<h1 id="page-title" className="text-3xl font-bold">{title}</h1></div>{actions}</div><div className="mt-8">{children}</div></section>
}

export function LoadingState() { return <div role="status" className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-8 text-zinc-400">Loading operational data…</div> }
export function ErrorState({ error }: { readonly error: Error }) { return <div role="alert" className="rounded-xl border border-red-900 bg-red-950/30 p-6 text-red-200">{error.message}</div> }
