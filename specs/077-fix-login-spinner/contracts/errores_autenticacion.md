# Contrato: Catalogo de errores de autenticacion

**Fecha**: 2026-09-22 · **Feature**: [spec](specs/077-fix-login-spinner/spec.md)

Catalogo unico de textos canonicos (decision del usuario, Clarificacion Q4). Existe UN solo
formato de error estructurado en el sistema (constitucion §9).

## Formato interno (log/traza)

```json
{
  "codigo": "ERR_AUTH_INVALIDAS | ERR_AUTH_INACTIVO | ERR_AUTH_RECURSO | ERR_AUTH_POLITICA | ERR_AUTH_INESPERADO",
  "desenlace": "CREDENCIALES | INACTIVO | RECURSO | POLITICA | INESPERADO",
  "usuario": "[nombre_usuario si existe; nunca el hash]",
  "transitorio": true | false
}
```

- Zero leak: el log NO contiene contraseña, token, hash ni IP en claro sin sanitizar.
- En produccion los detalles tecnicos se ocultan (patron actual de `auth_state`).

## Cono surface al usuario (UI)

| Desenlace | Texto exacto mostrado al usuario |
|-----------|----------------------------------|
| Credenciales invalidas | "Credenciales invalidas. Verifique usuario y contraseña." |
| Usuario inactivo | "El usuario se encuentra inactivo." |
| BD no disponible | "El servicio no está disponible en este momento. Intente de nuevo." |
| Red/backend sin respuesta | "No se pudo conectar con el servidor. Verifique su conexión e intente de nuevo." |
| Excepcion inesperada | "Ocurrió un error inesperado. Intente de nuevo." |
| Bloqueo por intentos | "Demasiados intentos. Intente de nuevo en 15 minutos." |

Regla: el `error_message` del estado jamas se llena con texto tecnico ni con `str(excepcion)`.
La fuente unica de estos textos es este catalogo (constante de presentacion o esquema de dominio).