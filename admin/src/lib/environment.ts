import { z } from 'zod'

const environmentSchema = z.object({ VITE_API_BASE_URL: z.url().default('http://localhost:8000/api/v1'), VITE_APP_ENV: z.enum(['local', 'development', 'staging', 'production']).default('local') })
export const environment = environmentSchema.parse(import.meta.env)
