# Banco de Dados

## Banco principal

PostgreSQL.

## Entidades principais

### users
- id UUID
- email
- password_hash
- display_name
- locale
- timezone
- status
- created_at
- updated_at

### devices
- id UUID
- user_id
- platform
- push_token
- app_version
- notifications_enabled
- last_seen_at

### organizations
- id UUID
- name
- slug
- logo_url
- active

### athletes
- id UUID
- name
- nickname
- country_code
- image_url
- external_ids JSONB

### events
- id UUID
- organization_id
- name
- slug
- venue
- city
- country_code
- scheduled_start_at
- actual_start_at
- status
- provider_payload JSONB
- version

### fights
- id UUID
- event_id
- red_athlete_id
- blue_athlete_id
- weight_class
- bout_type
- scheduled_order
- current_order
- rounds_scheduled
- status
- actual_start_at
- actual_end_at
- result_method
- winner_athlete_id
- provider_payload JSONB
- version

### fight_state_events
- id UUID
- fight_id
- event_id
- state
- round_number
- clock_seconds
- source
- payload JSONB
- occurred_at
- created_at

### alerts
- id UUID
- user_id
- fight_id
- trigger_type
- lead_minutes
- status
- created_at
- cancelled_at

### alert_deliveries
- id UUID
- alert_id
- device_id
- channel
- idempotency_key
- status
- provider_message_id
- attempted_at
- delivered_at
- error_code

### predictions
- id UUID
- fight_id
- predicted_start_at
- earliest_start_at
- latest_start_at
- confidence_score
- model_version
- factors JSONB
- created_at

### event_changes
- id UUID
- event_id
- entity_type
- entity_id
- action
- before_data JSONB
- after_data JSONB
- source
- actor_user_id
- created_at

### subscriptions
- id UUID
- user_id
- provider
- plan
- status
- current_period_end
- external_customer_id
- external_subscription_id

## Regras

- Usar `timestamptz`.
- IDs públicos devem ser UUID.
- Soft delete apenas quando houver necessidade de auditoria.
- Índices em status, datas, chaves estrangeiras e consultas de alertas.
- Mudanças de card nunca devem apagar o histórico anterior.
