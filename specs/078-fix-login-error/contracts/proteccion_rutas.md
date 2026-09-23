# Contrato: Protección de rutas y cierre de la generación de navegación

**Feature**: 078-fix-login-error · **Rige sobre**: `src/presentacion_reflex/state/auth_state.py`
(referencia) y `src/presentacion_reflex/state/navigation_mixin.py` (inmutable, FR-004).

## 1. Ciclo de protección de una ruta

```text
rx.page(route="/x", on_load=[AuthState.require_login, ...])
   │
   ▼
require_login()                                  # auth_state.py:194
   ├─ start_navigation_generation()  → gen_id    # mixin: is_loading=True
   └─ yield require_login_background(gen_id)
   │
   ▼
require_login_background(gen_id)                 # auth_state.py:203  (background)
   ├─ async with self:
   │    ├─ if NOT validate_generation(gen_id): DROP (navegó fuera) → return
   │    ├─ valid = _validate_session()           # O(1), dentro del lock (comportamiento 077 preservado)
   │    └─ end_navigation_generation()           # SIN argumento (contrato; fix de la regresión)
   ├─ si NOT valid:  toast "Sesión expirada. Por favor, inicie sesión nuevamente." + redirect /login
   └─ si valid:      _sync_permissions() si allowed_modules está vacío
```

## 2. Contrato del mixin (NO cambiar; FR-004)

| Método | Firma | Nota |
|--------|-------|------|
| `start_navigation_generation` | `(self) -> str` | Solo AuthState la usa para el protector |
| `end_navigation_generation` | `(self) -> None` | **Prohibido pasar argumentos**. Idempotente (`is_loading=False`) |
| `validate_generation` | `(self, generation_id: str) -> bool` | Descarta tasks obsoletas (log `[DROP]`) |
| `trigger_graceful_rollback` | `(self) -> list[rx.event.EventSpec]` | Fallback existente; no se toca |

**Regla de firma (SC-005/SC-006)**: toda invocación a `end_navigation_generation` en el codebase DEBE ser
sin argumento. Verificados hoy: `personas_state.py:341`, `alertas_dashboard_state.py:92` y (tras el fix)
`auth_state.py:215`.

**Invariantes**:
- Todo camino del protector termina con `is_loading = False` (FR-004).
- La invocación es idempotente: repetir con `is_loading` ya en `False` no produce efecto ni error (Clarificación Q3).
- El mixin NO se rediseña: ningún parámetro, default ni rama condicional nueva (FR-004, §12 Chesterton).

## 3. Log seguro de desenlace (FR-009 / SC-002)

Emisión en los dos caminos terminales de `require_login_background`, a nivel `logger` de módulo:

| Caso | Nivel | Mensaje (plantilla) |
|------|-------|---------------------|
| Acceso permitido | `info` | `Protección de rutas: acceso permitido` |
| Acceso denegado (sesión inválida/transitorio) | `warning` | `Protección de rutas: acceso denegado (redirección a /login)` |

- **Campos prohibidos**: credenciales, `password`, `token`, `nombre_usuario`, `contrasena_hash`, cookies. (Zero Leak).
- La tarea descartada (generación obsoleta) NO emite este log; el mixin ya registra `[DROP]`.
- El log NO sustituye al mensaje visible al usuario ("Sesión expirada...") ni al error genérico de Reflex.

## 4. Ruta protegida (criterio objetivo; FR-003 / SC-003)

Se considera ruta protegida **toda página cuyo `on_load` ejecuta `AuthState.require_login`**. Inventario
mínimo confirmado (18): `/dashboard`, `/personas`, `/propiedades`, `/contratos`, `/liquidaciones`,
`/liquidacion_asesores`, `/recaudos`, `/recibos`, `/propiedad_horizontal`, `/usuarios`, `/seguros`,
`/saldos_favor`, `/proveedores`, `/incrementos`, `/incidentes`, `/desocupaciones`, `/configuracion`,
`/auditoria`. Cualquier página que añada el protector queda cubierta por el mismo criterio (no requiere
modificar este contrato).

## 5. Matriz de regresión preservada (077)

No se reabre el flujo de login de la 077. La corrección no altera: `login()` (desenlaces tipados,
`login_in_progress`), rate limiting, `_validate_session` (error transitorio → no invalidación), ni los
desenlaces de `personas`/`alertas_dashboard` (FR-006/FR-007). Ver `quickstart.md` para la validación de SC-004.