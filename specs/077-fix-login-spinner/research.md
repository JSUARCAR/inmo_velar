# Research: Correción del flujo de inicio de sesión (spinner infinito)

**Fecha**: 2026-09-22
**Feature**: [spec.md](spec.md)

## Objetivo

Resolver los desconocidos tecnicos necesarios para disenar la correccion de causa raiz del
spinner infinito del boton "Acceder al panel", sin violar la constitucion (FR-002: nada de
timeouts de interfaz ni ocultamiento del desenlace).

## Environment

- **Lenguaje / Runtime**: Python 3.11 en despliegue (`runtime.txt`); la maquina local usa Python 3.12.6.
- **Framework UI**: `reflex==0.8.28.post1` instalado localmente (el manifest exige `reflex>=0.6.0`).
  → Decision: la correccion se disena y valida contra **0.8.28.post1** (definido por `catalogo de paquetes`).
- **Base de datos**: PostgreSQL via `psycopg2-binary` (pool `ThreadedConnectionPool` min=1, max=20).
  Modo dual SQLite solo como fallback local de desarrollo; **no** se introduce logica nueva de negocio sobre SQLite.
- **Testing**: `pytest` (asyncio auto), integraciones contra BD de prueba, E2E Playwright (`playwright@^1.60`).
- **Lint/Type**: `ruff` (E,F,I; line-length 100), `black` (line-length 100), `mypy`.

## Problema: mapa de estados de carga

### Hallazgo 1 — `is_loading` global nunca se restablece tras validar rutas

`NavigationGenerationMixin.start_navigation_generation()` fija `is_loading=True` (`navigation_mixin.py:16-20`).
`AuthState.require_login` (usa en `on_load` de ~22 rutas protegidas) invoca ese metodo y lanza
`require_login_background`, que **jamas llama** `end_navigation_generation()` (FD en `auth_state.py:193-219`).
Otros estados (`personas_state`, `alertas_dashboard_state`) si cierran su generacion con
`end_navigation_generation()`. Consecuencia observable: al navegar a cualquier pagina protegida y
ser redirigido a `/login`, `AuthState.is_loading` queda en `True` → el boton del login se renderiza
en estado de carga `loading=AuthState.is_loading` sin operacion en curso.

- **Decision**: El boton del login DEBE derivar su estado de carga de una senal **dedicada al evento de login**
  (p.ej. `login_in_progress: bool`), y el ciclo de proteccion de rutas DEBE restablecer `is_loading`
  en todas sus rutas (reusar `end_navigation_generation()` igual que los otros mixins).
- **Rationale**: `is_loading` es un flag compartido (login + proteccion de rutas) y la causa de que el
  spinner aparezca "pegado". Desacoplarlo hace el estado explicito y verificable (Contrato).
- **Alternatives considered**:
  - Reutilizar `is_loading` en ambos: se descarta porque la interlepre de generaciones deja
    estados residuales (evid. Hallazgo 1) y dificulta el criterio de aceptacion E2E.
  - Timer de interfaz para apagar el spinner: prohibido por el spec (FR-002/SC-006).

### Hallazgo 2 — Rutas del generador `login()` con `yield` + `return`

El handler `login()` es un generador que mezcla `yield` (envio de estado) y `return` (lineas 311-312).
En la ruta de exito prepara cookies, fija `is_loading=False` y emite `yield rx.redirect("/dashboard")`
seguido de `return`. Reflex 0.8 documenta que los handlers generadores pueden encadenar eventos via
`yield`; el caso critico es que **todo camino del generador debe terminar** sin dejar el WebSocket
pendiente ("event never completes" → spinner eterno). Si la cookie `_s` no viaja en el mismo delta
que el redirect, el `on_load` de `/dashboard` revalida sin token → redireccion a `/login` sin finalizar
el indicador (bucla + spinner).

- **Decision**: Reestructurar `login()` como flujo **síncrono con finalizacion garantizada** y
  redireccion terminal pura: retornar `rx.redirect` al final del handler (sin `yield` intermedio que
  pueda quedar abierto), o dividir en `login()` → `_finalize_login_success()` si se requiere el delta de estado.
- **Rationale**: Simplifica el contrato del evento (una sola ruta de salida por desenlace) y hace
  deterministico el cierre del indicador de carga.
- **Alternatives considered**:
  - Mantener `yield` + `return`: se conserva pero solo si el diagnostico E2E demuestra que el delta
    se entrega; riesgo de no cerrar el evento justo del bug.
  - Background task para el login: se descarta (complejidad injustificada; login es una operacion corta).

### Hallazgo 3 — Generador de proteccion con `yield` dentro de `async with self`

`require_login_background` emite `yield rx.toast.error(...)` y `yield rx.redirect(...)` DENTRO del bloque
`async with self:` (FD `auth_state.py:203-219`). Reflex 0.8 advierte que los background tasks deben
liberar el lock para operaciones largas y que `yield` de eventos UI desde un background task es fragil
(puede no completar la navegacion). Es un candidato fuerte para el "no terminal".

- **Decision**: En el ciclo de proteccion, separar mutacion bajo lock (validar y poblar estado) de la
  emision de eventos terminales (toast/redirect) fuera del contexto, o programar la navegacion con el
  estado ya resuelto desde un handler secundario.
- **Rationale**: Cumple el contrato del framework (background tasks) y elimina la clase de fallo
  "redirect que nunca navega".
- **Alternatives considered**: Dejar la emision dentro del contexto → se descarta (evidencia framework).
  Usar un only-background redirect via `return` del task → valido como alternativa si el diagnostico lo confirma.

### Hallazgo 4 — Límites de recurso ya existentes

`database.py` ya parametriza `connect_timeout` (default 10s) via `DB_CONNECT_TIMEOUT`; el pool es
`ThreadedConnectionPool`. Faltan: `statement_timeout` (DML/consultas colgadas) y un deadline global de
la operacion de login. Sin estos, una consulta colgada mantiene el evento abierto (sin desenlace real).

- **Decision**: Parametrizar `options`, `statement_timeout` y opcionalmente `lock_timeout` en
  `pg_config`, y aplicar un deadline de operacion en el login via excepcion tipada de dominio.
- **Rationale**: Convierte la espera en un error real y visible (FR-009) sin temporizadores de UI.
- **Alternatives considered**: Quedarse con el `connect_timeout` solo → insuficiente (no cubre queries colgadas).

### Hallazgo 5 — Distincion credenciales invalidas vs. inactivo

`ServicioAutenticacion.autenticar()` lanza `ErrorAutenticacion` con mensajes diferenciados
("Usuario o contraseña incorrectos" / "El usuario se encuentra inactivo"), pero `AuthState.login`
**sobrescribe todo** `ErrorAutenticacion` con "Credenciales invalidas..." (`auth_state.py:314-319`).
El spec (Q4) exige "El usuario se encuentra inactivo." como canonico para usuarios inactivos.

- **Decision**: Introducir excepciones/resultado tipado de dominio para distinguir el desenlace
  (p.ej. `ErrorCredencialesInvalidas` vs. `ErrorUsuarioInactivo`), mapeados a los textos canonicos.
  Los textos canonico se centralizan en un catalogo (ver `contracts/errores_autenticacion.md`).
- **Rationale**: Sin codigo de desenlace, el texto inactivo es imposible sin filtrar existencia de
  cuentas de forma gratuita.
- **Alternatives considered**: Mantener el mensaje unico para todos los fallos de credenciales (seguridad
  estricta) → descartada por decision explicita del usuario en Q4; se documenta la implicacion
  (fuga de existencia de cuenta) como tradeoff aceptado.
- **Seguridad (zero leak)**: los detalles tecnicos jamas se exponen; el log sigue sin credenciales.

## Constitucion / Gates (validados)

| Gate | Estado | Evidencia |
|------|--------|-----------|
| Sin Flet/SQLite en codigo nuevo | Cumple | La correccion vive en `presentacion_reflex/state` + `dominio/aplicacion`; sin tocar transporte |
| Idioma 100% espanol | Cumple | Textos canonicos y documentacion en espanol |
| Clean architecture (dependencia unidireccional) | Cumple | Excepciones en `dominio`, servicio en `aplicacion`, gap de contenido en `presentacion` |
| Tipado + constantes UPPER_SNAKE + docstrings Google | Cumple | Se respeta en artfactory |
| Excepciones tipadas de dominio (no genericas supresivas) | Cumple | El `except Exception` final queda solo como fallback loggeado y terminal |
| Persistencia PostgreSQL (%s, RETURNING, sin magic numbers) | Cumple | Sin cambios de esquema; limites vía configuración documentada |
| Tests: dominio 100%, logica nueva >90%, unit sin I/O | Cumple | TDD: primero unit de excepciones/mensajes y de mixin |
| Verificacion en navegador + regresion visual | Cumple | Evidencia por E2E Playwright + capturas antes/despues (Q3) |
| Zero leak | Cumple | Logs sin credenciales; `debug` respeta `IS_PROD` |

## Unknowns resueltos

1. Version de Reflex → **0.8.28.post1** (ver Environment).
2. ¿Donde se pierde el desenlace? → 4 candidatas de causa raiz con evidencia estatica (Hallazgos 1–4);
   la confirmacion empirica se ejecuta en implementacion siguiendo FR-001 (E2E + traza + capturas) y
   STOP-THE-LINE.
3. ¿Existen limites de recurso? → `connect_timeout` si; `statement_timeout` no (Hallazgo 4).
4. ¿Como distinguir "inactivo" de "invalido" sin romper seguridad? → excepciones tipadas + catalogo de textos (Hallazgo 5).
5. ¿Patterns de event handler en Reflex 0.8? → fuerza mayor: un handler debe terminar en todas sus rutas;
   background tasks no deben emitir eventos UI dentro del lock (Hallazgos 2-3).