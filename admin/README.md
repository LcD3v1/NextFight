# Admin

Painel operacional NextFight em React, TypeScript estrito, Vite, Tailwind CSS e componentes no padrão shadcn/ui.

## Fundação

Inclui shell responsivo e acessível, navegação operacional, TanStack Query, React Hook Form, Zod, Vitest e Playwright. As páginas atuais delimitam áreas administrativas sem dados falsos nem autenticação simulada.

## Execução

```powershell
npm install
npm run dev
```

## Qualidade

```powershell
npm run lint
npm run typecheck
npm run test
npm run build
```

Configure `VITE_API_BASE_URL` e `VITE_APP_ENV` por ambiente. Valores externos são validados com Zod antes do uso.
