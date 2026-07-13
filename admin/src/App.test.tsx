import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AppLayout, FoundationPage } from './App'

describe('admin shell', () => { it('renders accessible navigation and content', () => { render(<MemoryRouter><Routes><Route element={<AppLayout />}><Route index element={<FoundationPage title="Dashboard" />} /></Route></Routes></MemoryRouter>); expect(screen.getByRole('complementary', { name: /primary/i })).toBeInTheDocument(); expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument() }) })
