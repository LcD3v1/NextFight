# API

## Convenções

- Base: `/api/v1`.
- JSON.
- Datas ISO 8601 em UTC.
- Paginação por cursor quando necessário.
- Erros no formato Problem Details.
- `X-Request-ID` em todas as respostas.

## Endpoints iniciais

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`

### User

- `GET /me`
- `PATCH /me`
- `GET /me/devices`
- `POST /me/devices`
- `DELETE /me/devices/{device_id}`

### Events

- `GET /events`
- `GET /events/{event_id}`
- `GET /events/{event_id}/fights`
- `GET /events/{event_id}/timeline`

### Fights

- `GET /fights/{fight_id}`
- `GET /fights/{fight_id}/prediction`

### Alerts

- `GET /me/alerts`
- `POST /me/alerts`
- `PATCH /me/alerts/{alert_id}`
- `DELETE /me/alerts/{alert_id}`

### Favorites

- `GET /me/favorites`
- `POST /me/favorites`
- `DELETE /me/favorites/{favorite_id}`

### Admin

- `POST /admin/events`
- `PATCH /admin/events/{event_id}`
- `PATCH /admin/fights/{fight_id}`
- `POST /admin/events/{event_id}/state`
- `POST /admin/fights/{fight_id}/state`
- `POST /admin/alerts/dispatch`
- `GET /admin/audit-logs`

## WebSocket

Endpoint: `/ws`

Tópicos:

- `event:{event_id}`
- `fight:{fight_id}`
- `user:{user_id}`

Eventos:

- `event.updated`
- `card.reordered`
- `fight.started`
- `fight.updated`
- `fight.completed`
- `prediction.updated`
- `alert.triggered`
