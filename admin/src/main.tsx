import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { AppLayout } from './App'
import { LoginPage } from './features/auth/LoginPage'
import { DashboardPage } from './features/dashboard/DashboardPage'
import { EventsPage } from './features/events/EventsPage'
import { LiveMonitorPage } from './features/live/LiveMonitorPage'
import { AuditLogsPage, DeliveriesPage, UsersPage } from './features/operations/DataPages'
import './index.css'

const router = createBrowserRouter([{ path: '/login', element: <LoginPage /> }, { path: '/', element: <AppLayout />, children: [{ index: true, element: <DashboardPage /> }, { path: 'events', element: <EventsPage /> }, { path: 'live', element: <LiveMonitorPage /> }, { path: 'users', element: <UsersPage /> }, { path: 'alerts', element: <DeliveriesPage /> }, { path: 'audit-logs', element: <AuditLogsPage /> }] }])
const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 2, refetchOnWindowFocus: false } } })

createRoot(document.getElementById('root')!).render(<StrictMode><QueryClientProvider client={queryClient}><RouterProvider router={router} /></QueryClientProvider></StrictMode>)
