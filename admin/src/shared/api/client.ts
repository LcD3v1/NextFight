import { environment } from '../../lib/environment'

export interface TokenResponse {
  readonly access_token: string
  readonly refresh_token: string
  readonly expires_in: number
  readonly user: { readonly id: string; readonly email: string; readonly display_name: string; readonly role: string }
}

export class ApiError extends Error {
  readonly status: number
  constructor(status: number, message: string) { super(message); this.name = 'ApiError'; this.status = status }
}

const ACCESS_KEY = 'nextfight.admin.access'
const REFRESH_KEY = 'nextfight.admin.refresh'

export const sessionStore = {
  access: () => sessionStorage.getItem(ACCESS_KEY),
  refresh: () => sessionStorage.getItem(REFRESH_KEY),
  save: (tokens: TokenResponse) => { sessionStorage.setItem(ACCESS_KEY, tokens.access_token); sessionStorage.setItem(REFRESH_KEY, tokens.refresh_token) },
  clear: () => { sessionStorage.removeItem(ACCESS_KEY); sessionStorage.removeItem(REFRESH_KEY) },
}

async function parseError(response: Response): Promise<ApiError> {
  const body = await response.json().catch(() => ({})) as { detail?: string }
  return new ApiError(response.status, body.detail ?? `Request failed (${response.status})`)
}

async function refreshSession(): Promise<boolean> {
  const refreshToken = sessionStore.refresh()
  if (!refreshToken) return false
  const response = await fetch(`${environment.VITE_API_BASE_URL}/auth/refresh`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh_token: refreshToken }) })
  if (!response.ok) { sessionStore.clear(); return false }
  sessionStore.save(await response.json() as TokenResponse)
  return true
}

export async function apiRequest<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (init.body) headers.set('Content-Type', 'application/json')
  const access = sessionStore.access()
  if (access) headers.set('Authorization', `Bearer ${access}`)
  const response = await fetch(`${environment.VITE_API_BASE_URL}${path}`, { ...init, headers })
  if (response.status === 401 && retry && await refreshSession()) return apiRequest<T>(path, init, false)
  if (!response.ok) throw await parseError(response)
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const response = await fetch(`${environment.VITE_API_BASE_URL}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
  if (!response.ok) throw await parseError(response)
  const tokens = await response.json() as TokenResponse
  if (!['admin', 'operator'].includes(tokens.user.role)) throw new ApiError(403, 'This account cannot access the operational console.')
  sessionStore.save(tokens)
  return tokens
}
