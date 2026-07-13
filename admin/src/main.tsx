import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { AppLayout, FoundationPage } from './App'
import './index.css'

const pages = ['events', 'live', 'fights', 'users', 'alerts', 'audit-logs'] as const
const router = createBrowserRouter([{ path: '/', element: <AppLayout />, children: [{ index: true, element: <FoundationPage title="Dashboard" /> }, ...pages.map((path) => ({ path, element: <FoundationPage title={path.split('-').map((word) => word[0]?.toUpperCase() + word.slice(1)).join(' ')} /> }))] }])
const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 2, refetchOnWindowFocus: false } } })

createRoot(document.getElementById('root')!).render(<StrictMode><QueryClientProvider client={queryClient}><RouterProvider router={router} /></QueryClientProvider></StrictMode>)
