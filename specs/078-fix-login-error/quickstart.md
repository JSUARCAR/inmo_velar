# Quickstart: Validación de la corrección del error tras el login (TypeError en protección de rutas)

**Fecha**: 2026-09-23 · **Feature**: [spec](spec.md)

Guía de validación de extremo a extremo. Detalles de implementación en `tasks.md` (`/speckit.tasks`).
Contratos: [proteccion_rutas.md](contracts/proteccion_rutas.md). Modelo: [data-model.md](data-model.md).

## Prerequisitos

- Entorno local: `reflex==0.8.28.post1`, Python 3.11+, PostgreSQL o `DB_MODE=sqlite` para dev.
- `.env` con `TEST_USER`/`TEST_PASSWORD` (credenciales de prueba activas) y `DATABASE_URL` (dev o desplegado).
- `node` + Playwright (`npm install`, `package.json` ya incluye `playwright@^1.60`) para la parte E2E.
- Acceso a los logs del entorno desplegado (`inmovelar-production.up.railway.app`) — bloqueante (Clarificación Q4).

## Confirmación del `TypeError` (antes de la corrección; FR-001/SC-002 estado 1)

1. Iniciar local: `reflex run --env dev` (constitución §6) o revisar logs desplegado.
2. Loggear con un usuario activo y navegar a una ruta protegida.
3. Registrar en los logs del backend la excepción:
   `TypeError: NavigationGenerationMixin.end_navigation_generation() takes 1 positional argument but 2 were given`
   en `require_login_background` (`auth_state.py:215`). Capturar evidencias "antes".

## Corrección y blindaje (TDD; FR-008/SC-006)

1. Test que falle primero (método REAL, sin mockear `end_navigation_generation`) cubriendo los **tres
   caminos terminales**: (1) acceso permitido, (2) acceso denegado → `/login`, (3) generación obsoleta
   (DROP, sin invocar `end_navigation_generation`) — todos sin `TypeError` e `is_loading == False`.
2. Applicar el fix: `self.end_navigation_generation()` (sin argumento) en `auth_state.py:215`.
3. Actualizar aserciones de los tests que codificaban la firma errónea (`tests/unit/test_proteccion_rutas.py`
   `assert_called_with("test-gen-N")` → `assert_called_once_with()`; des-mockear el patch en
   `tests/integration/test_auth_login.py` — acción determinista, FR-010).
4. Añadir el log seguro de desenlace (FR-009): acceso permitido (`info`) / denegado (`warning`), sin credenciales.

## Matriz de validación obligatoria

| # | Escenario | Método | Resultado esperado | Criterio |
|---|-----------|--------|--------------------|----------|
| 1 | Login válido → panel sin error | E2E navegador | `/dashboard` sin "An error occurred..." | SC-001 |
| 2 | Toda ruta protegida carga sin error (+ recarga) | E2E sobre inventario (18 rutas, contrato §4) con `page.reload()` tras cada visita | Cero `TypeError` y cero error genérico en carga y recarga | SC-003 |
| 3 | Logs de producción durante 24 h / 100 logins | **búsqueda activa** del patrón `TypeError` + líneas FR-009 en logs Railway | 0 ocurrencias del `TypeError`; log de desenlace presente | SC-002 |
| 4 | Guardia de regresión (FR-008) | pytest | Test dedicado (3 caminos terminales) en verde en toda la suite | SC-006 |
| 5 | `is_loading` en `False` tras navegación | unit + DOM (carga y `page.reload()`) | Sin spinner atascado en rutas protegidas | SC-005 |
| 6 | Matriz de autenticación 077 (10 puntos) | E2E + integración | login válido/inválido, logout, sesión expirada, RBAC, rate limiting en verde | SC-004 |
| 7 | Sesión expirada → `/login` + mensaje | E2E | Redirección con "Sesión expirada. Por favor, inicie sesión nuevamente." sin `TypeError` | FR-005/US3 |

> El inventario de rutas y la matriz 077 completa se reutilizan de `specs/077-fix-login-spinner/quickstart.md`
> (puntos 1-10) — no se reabre el flujo de login (Assumptions).

## Comandos de verificación

```bash
# Unit / integración (TDD)
pytest tests/unit/test_proteccion_rutas.py tests/unit/test_regresion_firma_proteccion.py -q
pytest tests/integration/test_auth_login.py -q

# Lint / tipo / formato (pre-commit, constitución §5)
ruff check src/presentacion_reflex/state/auth_state.py tests/unit/test_proteccion_rutas.py
black --check src/presentacion_reflex/state/auth_state.py
mypy src/presentacion_reflex/state/auth_state.py

# E2E navegador (SC-003): inventario con recarga (tras habilitar harness, T011/T042)
npm install
node tests/e2e/navegacion_rutas_protegidas.spec.mjs   # 18 rutas + page.reload() (SC-003/SC-005)
node tests/e2e/login_valido.spec.mjs                  # smoken del harness (SC-001)

# Verificación en vivo
reflex run --env dev   # DOM/Consola/Red limpios + logs de desenlace (constitución §10)
```

## Evidencia para cerrado (BLOQUEANTE — Clarificación Q4)

- Capturas/logs "antes" (con `TypeError`) y "después" (sin excepción) en el entorno desplegado.
- Logs de producción (FR-009) mostrando desenlaces del protector durante la ventana SC-002 (24 h o 100 logins).
- Matriz 1-7 en verde en local y posteriormente en `inmovelar-production`; la validación desplegada
  (SC-001/SC-002/FR-009) es requisito para cerrar la feature.