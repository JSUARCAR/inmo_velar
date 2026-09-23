# Quickstart: Validacion de la correccion del login (spinner infinito)

**Fecha**: 2026-09-22 · **Feature**: [spec](specs/077-fix-login-spinner/spec.md)

Guia de validacion de extremo a extremo. Detalles de implementacion en `tasks.md`.

## Prerequisitos

- Entorno local: `reflex==0.8.28.post1`, Python 3.11+, PostgreSQL o `DB_MODE=sqlite` para dev.
- `.env` con `DATABASE_URL` (env desplegado) o config dev.
- Credenciales de prueba: un usuario activo (rol Administrador) y un usuario con rol restringido;
  una cuenta inactiva y una inexistente.
- Playwright: `npm install` (package.json ya incluye `playwright@^1.60`).

## Antes: evidencia del bug (FR-001 / SC-008)

1. Iniciar servidor minimo: `reflex run --env dev` (constitucion §6) o desplegado.
2. Ejecutar el repro E2E existente: `node tests/e2e/login_visible.spec.mjs` (con `TEST_USER`/`TEST_PASSWORD`).
3. Registrar: URL final, estado del boton (spinner si/no), consola del navegador, WebSocket events,
   y `[AUTH_DEBUG]` del backend. Guardar captura "antes".

> El diagnostico confirma cual(es) de los Hallazgos 1-4 (research.md) provoca el desenlace no
> terminal; con evidencia documentada se decide y se corrige la raiz (STOP-THE-LINE).

## Matriz de validacion obligatoria (10 puntos del spec)

| # | Escenario | Metodo | Resultado esperado |
|---|-----------|--------|--------------------|
| 1 | Login valido | E2E navegador | Redirige a `/dashboard`; sin log en consola; evento termina |
| 2 | Fin del estado de carga | E2E DOM | `login_in_progress=False`; boton habilitado; traza backend con desenlace |
| 3 | Autenticacion exitosa | traza + estado | `is_authenticated=True`, usuario/rol poblados |
| 4 | Persistencia de sesion | recarga en `/dashboard` | Sigue autenticado (8 h) sin pedir credenciales |
| 5 | Redireccion | E2E | `/login` → `/dashboard` correcto |
| 6 | Carga del panel | E2E | Permisos cargados; sin vuelta a `/login` |
| 7 | Rol/permisos | E2E RBAC | Admin accede a modulos; rol restringido no |
| 8 | Credenciales invalidas | E2E | Texto canonico + spinner restablecido |
| 9 | Errores de red/Backend/BD | simular indisponibilidad | Texto canonico + spinner restablecido (< deadline de recurso) |
| 10 | Sin regresiones | matriz auth completa | logout, sesion expirada, rutas protegidas, rate limiting OK |

## Comandos de verificacion

```bash
# Tests unitarios (TDD) e integracion
pytest tests/unit/test_*auth* tests/integration/test_auth_* -q

# Lint / tipo / formato (pre-commit, constitucion §5)
python scripts/diagnostico/check_syntax.py   # (o equivalente del repo)
ruff check src/
black --check src/
mypy src/

# E2E navegador (evidencia, Q3)
node tests/e2e/login_visible.spec.mjs

# Verificacion en vivo
reflex run --env dev   # luego validar DOM/Consola/Red limpios (constitucion §10)
```

## Evidencia para cerrado

- Capturas antes/despues (regresion visual, Q3).
- Traza de logs del backend con el ciclo de vida del evento (inicio → desenlace → fin).
- Reporte de la causa raiz documentada en la feature (SC-008).
- Matriz de los 10 puntos en verde, en entorno local y despues en el desplegado (Q2, bloqueante).