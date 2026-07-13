# Admin

Painel operacional NextFight em React, TypeScript estrito, Vite, Tailwind CSS, TanStack Query, React Hook Form e Zod.

## Recursos

Inclui autenticação real com RBAC, dashboard, eventos, monitor ao vivo, usuários, entregas, auditoria e disparo manual idempotente de alertas. O shell é responsivo e acessível e não usa dados simulados.

## Execução

```powershell
npm install
npm run dev
```

Configure `VITE_API_BASE_URL` e `VITE_APP_ENV`. Com Docker, execute `docker compose up -d --build` na raiz e acesse `http://localhost:5173`.

## Qualidade

```powershell
npm run lint
npm run typecheck
npm run test -- --run
npm run build
```

O Dockerfile usa build reproduzível com `npm ci` e publica os arquivos estáticos em Nginx não privilegiado com headers de segurança e fallback para as rotas da SPA.
