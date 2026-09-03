# Quickstart: Validation & E2E Testing

## Prerequisites
- Local development environment running Reflex (`reflex run`).
- PostgreSQL database accessible. Ejecutar `psql -f tests/seed.sql` para generar credenciales (admin/admin).
- Setup de entorno: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && reflex init`.

## Test Scenario 1: Standard Navigation (SC-001)
**Goal**: Verify smooth transitions between modules post-login.
1. Authenticate in the application and land on the Dashboard.
2. Click on the "Personas" menu link.
3. **Expected**: The URL changes to `/personas` immediately. A loading spinner (`rx.spinner`) is visible momentarily. The page renders fully (Data table populated, no White Screen of Death, no React Hydration errors in browser console) without reloading the Dashboard.

## Test Scenario 2: Rapid Navigation / Concurrency (EC-003)
**Goal**: Verify that rapid clicks do not corrupt the global state.
1. Authenticate and land on the Dashboard.
2. Click "Personas", and within `< 500ms`, immediately click "Alertas".
3. **Expected**: The system should discard the asynchronous payload from the "Personas" fetch because the generation timestamp has advanced. The final rendered view must be "Alertas" completely intact. No data from "Personas" should leak. QA MUST verify this by checking the terminal running reflex run for the explicit log: `[DROP] Mutación caducada (Generación mismatch)`.

## Test Scenario 3: Graceful Rollback (CHK002/CHK020)
**Goal**: Verify error handling if a background task fails.
1. Authenticate and land on the Dashboard.
2. Simular fallo de backend (Timeouts/Desconexión) usando Chrome DevTools -> Network -> Offline. Esto probará la resiliencia del frontend ante desconexiones.
3. Click on "Personas".
4. **Expected**: The loading spinner appears, the task fails, and the system automatically redirects the user back to the Dashboard while displaying a `rx.toast` (color: yellow/warning) with exact text: "Error de conexión. Redirigiendo al Dashboard".

## Test Scenario 4: Token Validation & Preservation (CHK007/CHK008)
**Goal**: Verify AuthState handles rapid transitions and token invalidation properly.
1. Authenticate and navigate between modules rapidly (as in Scenario 2).
2. **Expected 1**: The user should remain logged in. Token preservation must be seamless across route transitions without causing redundant database auth checks that block the UI.
3. Simulate token expiration (e.g., delete token cookie via DevTools).
4. Click on any module.
5. **Expected 2**: The backend AuthState background task should detect the invalid token and immediately redirect the user to /login without leaking any protected view data.
