# Data Model: Corrección del error de producción tras el inicio de sesión (TypeError en protección de rutas)

**Fecha**: 2026-09-23
**Alcance**: No introduce cambios de esquema ni de persistencia. Documenta la entidad de runtime
(Generación de Navegación) cuyo contrato se restablece, los estados del protector y los datos del
log seguro requerido por FR-009.

## Entidades persistentes (sin modificación)

### Usuario
- Campos relevantes: `id_usuario`, `nombre_usuario`, `contrasena_hash` (Bcrypt `$2b$` o SHA256 legacy),
  `estado_usuario` (bool), `rol`.
- Regla: el protector valida una sesión existente y activa; no altera al usuario.

### SesionUsuario
- Campos: `id`, `id_usuario`, `token_sesion`, `fecha_inicio`, `fecha_fin` (vigencia 8 h).
- Regla: una sesión es válida si existe y `esta_activa()`; el protector no la modifica.

> No hay DML, migraciones ni repositorios nuevos. Referencia de contratos: `contracts/proteccion_rutas.md`.

## Entidad de runtime: Generación de Navegación (mixin)

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `current_generation` | `str` | Identificador UUID de la generación activa (por página/navegación) |
| `is_loading` | `bool` | Bandera de carga de navegación; **se restablece a `False` al finalizar el protector** |

### Contrato de métodos (invariantes)

| Método | Firma | Invariante |
|--------|-------|------------|
| `start_navigation_generation` | `() -> str` | Fija `current_generation` y `is_loading=True`; retorna el id |
| `end_navigation_generation` | `()` -> None | **Sin argumentos**. Idempotente: solo asigna `is_loading=False` |
| `validate_generation` | `(gen_id: str) -> bool` | Descarta tareas de generaciones obsoletas antes de mutar |

- **Invariante de firma (regresión 077, FR-001/FR-004)**: `end_navigation_generation` DEBE invocarse sin
  argumento. Cualquier llamada con argumentos reintroduce `TypeError` en producción.
- **Invariante de idempotencia (Clarificación Q3, FR-004)**: invocar cuando `is_loading` ya es `False` es
  inocuo; no se exige guardia condicional.

## Transiciones del protector de rutas (máquina de estados)

```text
on_load(ruta protegida)
  ├─ require_login() → start_navigation_generation() → encola require_login_background(gen_id)
  │
  └─ require_login_background(gen_id):
       ├─ validate_generation(gen_id) == False  → DROP (tarea obsoleta), sin end_navigation_generation
       ├─ validate_generation(gen_id) == True
       │     ├─ _validate_session() == True  → acceso permitido → end_navigation_generation()  → _sync_permissions() si faltan
       │     └─ _validate_session() == False → acceso denegado → end_navigation_generation()  → log + toast + redirect /login
       │
       └─ error transitorio BD en _validate_session → NO invalida sesión; retorna False (comportamiento 077) → mismo camino de denegado
```

- Todo camino configurado termina con `is_loading = False` (FR-004/SC-005) y sin lanzar `TypeError` (FR-001).
- La generación obsoleta (navegó fuera) se descarta antes del llamado a `end_navigation_generation`
  (Edge Case §1 conservado).
- El caso "sesión inválida y generación válida" cae en el camino de denegado sin excepción (Edge Case §2).

## Datos del log seguro (FR-009)

Formato recomendado (definido en `contracts/proteccion_rutas.md`), a nivel `logger`:

| Campo | Ejemplo | Permitido / Prohibido |
|-------|---------|------------------------|
| Desenlace | `acceso_permitido` / `acceso_denegado` | Permitido |
| Ruta/referencia | `/dashboard` (opcional) | Permitido (sin datos de usuario) |
| Generación | `gen_id` | Permitido (UUID) |
| Credenciales / token / usuario / datos sensibles | — | **Prohibido** (Zero Leak, constitución §4) |

No requiere persistencia: se consumen desde los logs del entorno desplegado (Railway) para SC-002.