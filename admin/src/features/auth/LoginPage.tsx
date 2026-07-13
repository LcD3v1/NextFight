import { LogIn } from 'lucide-react'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../../shared/api/client'

export function LoginPage() {
  const navigate = useNavigate()
  const [error, setError] = useState<string>()
  const [pending, setPending] = useState(false)
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setPending(true); setError(undefined)
    const data = new FormData(event.currentTarget)
    try { await login(String(data.get('email')), String(data.get('password'))); await navigate('/') }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to sign in.') }
    finally { setPending(false) }
  }
  return <main className="grid min-h-screen place-items-center bg-zinc-950 p-6 text-zinc-100"><section className="w-full max-w-md rounded-2xl border border-zinc-800 bg-zinc-900 p-8 shadow-2xl" aria-labelledby="login-title"><p className="text-sm font-semibold uppercase tracking-[.22em] text-red-500">NextFight operations</p><h1 id="login-title" className="mt-3 text-3xl font-bold">Sign in securely</h1><p className="mt-2 text-sm text-zinc-400">Restricted to authorized operators and administrators.</p><form className="mt-8 space-y-5" onSubmit={submit}><label className="block text-sm font-medium">Email<input required name="email" type="email" autoComplete="username" className="mt-2 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-3" /></label><label className="block text-sm font-medium">Password<input required name="password" type="password" autoComplete="current-password" className="mt-2 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-3" /></label>{error && <div role="alert" className="rounded-lg border border-red-800 bg-red-950/40 p-3 text-sm text-red-200">{error}</div>}<button disabled={pending} className="flex w-full min-h-11 items-center justify-center gap-2 rounded-lg bg-red-600 font-semibold hover:bg-red-500 disabled:opacity-50"><LogIn size={18} />{pending ? 'Signing in…' : 'Sign in'}</button></form></section></main>
}
