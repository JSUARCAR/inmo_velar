# Contrato: Evento de login y estado de la UI

**Fecha**: 2026-09-22 · **Feature**: [spec](specs/077-fix-login-spinner/spec.md)
**Framework**: Reflex 0.8.28.post1

## Estado expuesto (public contract)

| Campo | Tipo | Rol en la UI |
|-------|------|--------------|
| `login_in_progress` | `bool` | Unica senal que activa `loading` del boton "Acceder al Panel" |
| `error_message` | `str` | Texto canonico del catalogo ([errores_autenticacion.md](errores_autenticacion.md)) |
| `is_authenticated` | `bool` | Estado general de sesion |
| `user_nombre`, `user_rol`, `user_id` | str/int | Datos del usuario |

Regla: `login_in_progress` lo activa SOLO el event handler `login()` y lo restablece en TODAS sus
rutas (exito → `redirect`; error → `False`). Ningun background task, `on_load` ni otra pagina
puede alterarlo.

## Event handler: `AuthState.login(form_data)`

- Entrada: dict con claves `username` y `password` (nombre canonico de los inputs).
- Comportamiento garantizado en reflex: cada desenlace cierra el evento; el generador termina.
- Desenlaces:
  1. Bloqueo por intentos → `error_message` canonico; `login_in_progress=False`.
  2. Success → cookies `_s`/`_r` emitidas; estado en memoria poblado; `rx.redirect("/dashboard")`.
  3. `ErrorCredencialesInvalidas` / `ErrorUsuarioInactivo` → texto canonico; `login_in_progress=False`.
  4. `ErrorRecurso` (BD/red/inesperado, incl. deadline de recurso) → texto canonico; `login_in_progress=False`;
     log seguro via `logger`.
- Prohibido: `yield` sin desenlace pendiente, emision de toast/redirect dentro de un lock de
  background task, y cualquier temporizador de interfaz (FR-009).

## Handler de proteccion: `AuthState.require_login` / `require_login_background`

- `start_navigation_generation()` SIEMPRE emparejado con `end_navigation_generation()` en todas las
  salidas del camino (valido→continua; invalido→redirige a /login y apaga `is_loading`).
- Los `yield` de toast/redirect se emiten FUERA del `async with self:` (por contrato de Reflex).
- No altera `login_in_progress`.

## Cookies

- `_s` (sesion) / `_r` (fingerprint): mismo nombre y politicas (path=/ , secure en prod, max_age 86400).
- La sesion sobrevive al redirect y a una recarga (persistencia, no cambio de comportamiento).