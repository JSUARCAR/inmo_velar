# Data Model: Correccion del flujo de inicio de sesion

**Fecha**: 2026-09-22
**Alcance**: No introduce cambios de esquema. Documenta las entidades que participan en el flujo de
login y los nuevos estados de runtime/dominio que la feature debe sostener.

## Entidades persistentes (sin modificacion de esquema)

### Usuario
- Campos relevantes: `id_usuario`, `nombre_usuario`, `contrasena_hash` (Bcrypt `$2b$` o SHA256 legacy),
  `estado_usuario` (bool), `rol`, `ultimo_acceso`.
- Reglas: un solo `nombre_usuario` unico; el login requiere `estado_usuario = True`.

### SesionUsuario
- Campos: `id`, `id_usuario`, `token_sesion`, `fecha_inicio`, `fecha_fin` (vigencia 8 h).
- Regla: una sesion es valida si existe y `esta_activa()`.

## Estados de runtime (Reflex)

### AuthState
- `login_in_progress: bool` (**nuevo**): unica senal que activa el `loading` del boton
  "Acceder al Panel". Es independiente de `is_loading` (proteccion de rutas).
- `is_loading: bool` (heredado del mixin): solo para ciclos de navegacion/background;
  el ciclo de proteccion debe restablecerlo en TODAS las rutas (`end_navigation_generation()`).
- `error_message: str`: texto canonico por desenlace (nunca detalle tecnico).
- `session_token`/`_refresh_fingerprint` (cookies `_s`/`_r`): intocados.

### Transiciones de estado de login (maquina de estados)

```text
idle → submitting → success(redirect /dashboard)
idle → submitting → error_permanente (message + idle)      # credenciales invalidas / inactivo
idle → submitting → error_transitorio (message + idle)     # red / backend / BD / inesperado
submitting → (deadline recursos) → error_transitorio       # FR-009, sin temporizador de UI
```

- Toda transicion DEBE terminar en `idle` (o en `redirect`), nunca dejar `submitting` activo.
- El `loading` del boton es `login_in_progress`; el resto del sistema no puede activarlo.

## Errores tipados de dominio (nuevos)

### Resultado de autenticacion (dominio)
- `ExitoAutenticacion(usuario, sesion)`.
- `ErrorCredencialesInvalidas` (usuario inexistente o contraseña incorrecta).
- `ErrorUsuarioInactivo`.
- `ErrorRecurso` (BD no disponible, timeout de recurso, excepcion inesperada).
- `ErrorPoliticaIntentos` (rate limiting alcanzado).

| Desenlace | Texto canonico | Clase de dominio | Transitorio |
|-----------|---------------|------------------|-------------|
| Credenciales invalidas | "Credenciales invalidas. Verifique usuario y contraseña." | `ErrorCredencialesInvalidas` | No |
| Usuario inactivo | "El usuario se encuentra inactivo." | `ErrorUsuarioInactivo` | No |
| BD no disponible | "El servicio no está disponible en este momento. Intente de nuevo." | `ErrorRecurso` | Si |
| Red/backend sin respuesta | "No se pudo conectar con el servidor. Verifique su conexión e intente de nuevo." | `ErrorRecurso` | Si |
| Excepcion inesperada | "Ocurrió un error inesperado. Intente de nuevo." | `ErrorRecurso` | Si |
| Bloqueo por intentos | "Demasiados intentos. Intente de nuevo en 15 minutos." | `ErrorPoliticaIntentos` | Si |

Nota de seguridad: exhibir "inactivo" filtra la existencia de la cuenta; es un tradeoff
aceptado por decision del usuario (Clarificacion Q4 del spec).

## Configuracion (limites de recurso)

- `DB_CONNECT_TIMEOUT` (default 10 s): existe.
- `DB_STATEMENT_TIMEOUT` (**nuevo**, ms; default 5000): `statement_timeout` de psycopg2.
- `LOGIN_OPERATION_DEADLINE_SECONDS` (**nuevo**, default 12 s): deadline de la operacion de login.
- Ninguno de estos valores es un temporizador de la interfaz; producen un error real (FR-009).