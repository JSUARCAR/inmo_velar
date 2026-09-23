# Feature Specification: Corrección del error de producción tras el inicio de sesión (TypeError en protección de rutas)

**Feature Branch**: `078-fix-login-error`

**Created**: 2026-09-23

**Status**: Draft

**Input**: User description: "En el sitio desplegado (https://inmovelar-production.up.railway.app/login), después de iniciar sesión aparece el error 'An error occurred. Contact the website administrator.' Los logs de Railway muestran repetidamente: `File "/app/src/presentacion_reflex/state/auth_state.py", line 215, in require_login_background; self.end_navigation_generation(gen_id); TypeError: NavigationGenerationMixin.end_navigation_generation() takes 1 positional argument but 2 were given`. El login en sí tiene éxito (redirige a /dashboard) pero el protector de rutas lanza la excepción en cada navegación protegida."

## Contexto y causa raíz (verificada)

La causa raíz está confirmada en el código fuente:

1. **Protector de rutas** (`AuthState.require_login`, usado en `on_load` de `/dashboard` y las 18 páginas protegidas del inventario) inicia una "generación de navegación" con `start_navigation_generation()` y encola la tarea de fondo `require_login_background(gen_id)` (`auth_state.py:199-200`).
2. **Tarea de fondo** (`require_login_background`, `auth_state.py:203`) valida la generación, valida la sesión y, dentro del `async with self`, llama `self.end_navigation_generation(gen_id)` en la línea 215.
3. **Método del mixin** (`NavigationGenerationMixin.end_navigation_generation`, `navigation_mixin.py:22`) **NO recibe argumentos**: su única responsabilidad es restablecer `is_loading = False`. La firma es `def end_navigation_generation(self):`.
4. **Regresión confirmada**: el commit `e8d133e` (feature `077-fix-login-spinner`) insertó `self.end_navigation_generation(gen_id)` en esa línea. Otros estados lo invocan correctamente sin argumentos: `personas_state.py:341` y `alertas_dashboard_state.py:92` usan `self.end_navigation_generation()`.
5. **En producción (Railway)**: tras un login exitoso, cada `on_load` de ruta protegida dispara `require_login_background`, que lanza `TypeError: NavigationGenerationMixin.end_navigation_generation() takes 1 positional argument but 2 were given`. Reflex captura la excepción y muestra el mensaje genérico "An error occurred. Contact the website administrator." al usuario.

La solución DEBE corregir la invocación en `require_login_background` (verificar firma del método y llamarlo sin argumento), preservando la intención de la feature 077: que `is_loading` se restablezca al final del protector de rutas.

## Clarifications

### Session 2026-09-23

- Q: ¿La corrección incluye un test de regresión dedicado que blinde el contrato del mixin, o basta con la matriz de regresión existente (SC-004)? → A: Opción B — corrección quirúrgica de la invocación en `auth_state.py` MÁS un test de regresión dedicado que garantice que el protector de rutas termina sin `TypeError` y que `end_navigation_generation()` se invoca sin argumento, según el mandato de blindaje de la constitución (§13 Triage: "Corregir Raíz → Blindar").
- Q: ¿Debe el spec exigir un requisito explícito de verificación por logs en producción, dado que SC-002/SC-006 dependen de evidencia de logs pero ningún FR lo declara? → A: Opción B — añadir un FR explícito: el sistema DEBE registrar de forma segura (sin credenciales) el desenlace del protector de rutas en producción para corroborar la ausencia del `TypeError`.
- Q: ¿Se enumeran explícitamente las ~20 rutas protegidas en el spec, o se deja la lista para el plan de validación? → A: Opción A — no enumerar en el spec; fijar el criterio objetivo (toda ruta cuyo `on_load` ejecuta `AuthState.require_login`) y dejar la lista concreta de rutas al plan de validación.
- Q: ¿Qué comportamiento debe definir el spec ante invocación duplicada de `end_navigation_generation()` (cuando `is_loading` ya es `False`)? → A: Opción A — declarar la invocación idempotente/inocua (repetirla no tiene efecto ni error); el test FR-008 no necesita cubrir doble invocación y no se añade guardia condicional.
- Q: ¿La validación en el entorno desplegado debe ser bloqueante para cerrar la feature? → A: Opción A — bloqueante: la validación desplegada (SC-001/SC-002 + FR-009 en logs) es requisito para cerrar la feature, replicando el criterio de bloqueo de la 077.
- Q: ¿SC-004 (matriz de regresión de autenticación) es la matriz de 10 puntos de la feature 077 o solo los 6 comportamientos enumerados en el spec? → A: Opción A — SC-004 se valida con la matriz de 10 puntos de la feature 077, que es la fuente autoritativa e históricamente validada en producción; los 6 comportamientos enumerados en el spec (login válido, login inválido, logout, sesión expirada, RBAC, rate limiting) son un subconjunto obligatorio de dicha matriz, no una lista independiente.
- Q: ¿Cuándo inicia la ventana de validación SC-002 (24 h / 100 logins) tras el despliegue, y cómo se verifica la ausencia del `TypeError`? → A: Opción A — la ventana inicia al completarse el despliegue de la corrección en Railway; la verificación es una búsqueda ACTIVA del patrón de excepción `TypeError: ... end_navigation_generation()` y de las líneas de desenlace FR-009 en los logs de producción, no solo ausencia visual.
- Q: ¿El spec debe exigir la actualización de los tests existentes que codifican la firma errónea (CHK001/CHK010)? → A: Opción A — el spec DEBE incluir un requisito explícito de actualizar los tests existentes que asertan la firma errónea (`test_proteccion_rutas.py` con `assert_called_with("test-gen-N")` y el mockeo de `end_navigation_generation` en `test_auth_login.py`), de modo que toda la suite valide el contrato real sin argumento y no re-codifique el bug.
- Q: ¿Debe habilitarse el harness E2E (Playwright) como parte del alcance de 078 para que SC-003/SC-004 sean verificables (CHK025/CHK022)? → A: Opción A — habilitar el harness E2E como parte del alcance de 078: instalar y ejecutar los specs de navegación para que SC-003/SC-004 (parte E2E) sean verificables, asumiendo explícitamente la deuda pendiente T042 de la feature 077.
- Q: ¿Con qué evidencia se satisface SC-001 en el entorno desplegado, dado el conflicto entre outcome en pantalla y evidencia por logs (CHK013/CHK031)? → A: Opción A — en producción, SC-001 se evidencia con las líneas de desenlace FR-009 en logs (éxito/redirección/fin sin excepción) y con SC-002 (búsqueda activa del `TypeError`); la observación visual en pantalla corresponde al E2E habilitado (FR-008/SC-003) ejecutado contra el entorno desplegado.
- Q: ¿Qué caminos terminales del protector debe cubrir el test de regresión FR-008 (tras gap U2/U3 del análisis)? → A: Opción A — FR-008 DEBE cubrir los tres caminos terminales en el test unitario: acceso permitido, acceso denegado (redirección a `/login`) y generación obsoleta (`validate_generation == False` → DROP sin llamado a `end_navigation_generation`), más la invariante `is_loading == False`.
- Q: ¿Cómo se verifica la recarga de página en una ruta protegida (Edge Case 4, gap U2 del análisis)? → A: Opción A — SC-003/SC-005 DEBEN incluir la recarga (`page.reload()`) sobre el inventario de rutas protegidas en el E2E: la ruta se visita, se recarga con sesión válida y se verifica ausencia de error genérico y `is_loading == False`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inicio de sesión válido que llega al panel sin error (Priority: P1)

Como usuario autenticado, quiero iniciar sesión con credenciales válidas y ser llevado al panel sin ver ningún mensaje de error, para poder operar la aplicación.

**Why this priority**: Es el síntoma reportado: el login "funciona" pero el usuario ve el error genérico en lugar del panel. Sin esta corrección, ningún usuario autenticado puede operar el sistema en producción.

**Independent Test**: Con credenciales válidas activas, completar el login y verificar que: (a) no aparece el mensaje "An error occurred. Contact the website administrator.", (b) se llega a `/dashboard`, (c) no aparecen excepciones `TypeError` en los logs del backend.

**Acceptance Scenarios**:

1. **Given** un usuario con credenciales válidas y activo en el entorno desplegado, **When** envía el formulario de login, **Then** es llevado a `/dashboard` sin ver el mensaje de error genérico y el panel carga con los permisos del rol.
2. **Given** el login exitoso, **When** el `on_load` del panel ejecuta el protector de rutas, **Then** el protector termina sin excepciones y `is_loading` queda en `False`.

---

### User Story 2 - Navegación a cualquier ruta protegida con sesión válida sin error (Priority: P1)

Como usuario autenticado, quiero navegar por todas las páginas protegidas del sistema sin que se muestre el error genérico, para que la aplicación sea utilizable.

**Why this priority**: El error se dispara en cada ruta protegida (18 rutas del inventario) cada vez que se ejecuta su `on_load`; afecta a la totalidad de la navegación autenticada.

**Independent Test**: Navegar a las rutas protegidas principales (`/dashboard`, `/personas`, `/contratos`, `/liquidaciones`, etc.) con una sesión válida y verificar que ninguna muestra el error genérico ni produce `TypeError` en el backend.

**Acceptance Scenarios**:

1. **Given** una sesión válida, **When** se navega a cualquier ruta protegida, **Then** la página carga correctamente sin el mensaje de error genérico.
2. **Given** una sesión válida, **When** el `on_load` de cada ruta protegida ejecuta `require_login_background`, **Then** la tarea termina sin excepciones (0 `TypeError` registrados).

---

### User Story 3 - Sesión expirada que redirige a /login con mensaje (Priority: P2)

Como usuario con una sesión expirada, quiero ser enviado de vuelta a `/login` con un mensaje claro, para poder volver a autenticarme.

**Why this priority**: El protector de rutas debe seguir cumpliendo su función de redirigir sesiones inválidas; la corrección no debe romper este flujo (comportamiento de la feature 077).

**Independent Test**: Con un token de sesión invalidado/vigencia vencida, acceder a una ruta protegida y verificar la redirección a `/login` con el mensaje canónico de sesión expirada y sin `TypeError`.

**Acceptance Scenarios**:

1. **Given** un token de sesión expirado o invalidado, **When** se accede a una ruta protegida, **Then** el sistema redirige a `/login` con el mensaje "Sesión expirada. Por favor, inicie sesión nuevamente." sin lanzar `TypeError`.

---

### User Story 4 - Sin regresiones en los demás flujos que usan el mixin de navegación (Priority: P2)

Como administrador del sistema, quiero que la corrección no altere los demás states que usan el control de navegación (`personas`, `alertas_dashboard`) ni el flujo de login corregido en la feature 077, para que no se introduzcan regresiones.

**Why this priority**: `end_navigation_generation()` se invoca en varios states; la corrección debe restringirse al llamado erróneo sin modificar el comportamiento común del mixin.

**Independent Test**: Ejecutar la matriz de regresión de autenticación (login válido, login inválido, logout, sesión expirada, RBAC, rate limiting) y verificar el comportamiento de `personas_state` y `alertas_dashboard_state` tras la corrección.

**Acceptance Scenarios**:

1. **Given** la corrección aplicada, **When** se ejecuta la matriz de regresión de autenticación (login válido, login inválido, logout, sesión expirada, RBAC, rate limiting), **Then** todos los comportamientos se conservan.
2. **Given** la corrección aplicada, **When** se ejercen los flujos de `personas` y `alertas_dashboard`, **Then** `end_navigation_generation()` sigue funcionando sin cambios (sin argumento).

---

### Edge Cases

- ¿El usuario navega fuera de la página mientras la tarea de fondo está pendiente (generación obsoleta)? → `validate_generation` devuelve `False` y la tarea se descarta (DROP) **sin invocar** `end_navigation_generation()`; el protector no llega al llamado erróneo, el comportamiento debe conservarse y el camino queda blindado por el caso (3) de FR-008 (Clarificación Q→A: tres caminos terminales).
- ¿Sesión inválida y generación válida al mismo tiempo? → Debe ejecutarse el desenlace de redirección a `/login` sin excepción.
- ¿Ruta protegida sin sesión y con error transitorio de BD en `_validate_session`? → No debe invalidarse la sesión ni producirse `TypeError` (comportamiento de 077 preservado).
- ¿Recarga de página en una ruta protegida? → El protector vuelve a ejecutarse y debe terminar sin el mensaje de error genérico; verificación incluida en SC-003/SC-005 mediante `page.reload()` sobre el inventario de rutas protegidas (Clarificación Q→A: SC-003/SC-005 recarga E2E).
- ¿Invocación duplicada de `end_navigation_generation()` cuando `is_loading` ya está en `False`? → La invocación es idempotente (solo asigna `False`): repetirla no tiene efecto ni produce error; no se exige guardia condicional ni un escenario de doble invocación en el test FR-008.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El protector de rutas (`require_login_background`) DEBE completar su ejecución sin lanzar excepciones al restablecer el estado de carga; en particular, la invocación de `end_navigation_generation()` DEBE ser compatible con la firma del método (que no recibe argumentos).
- **FR-002**: Tras un login exitoso, el usuario DEBE llegar al panel `/dashboard` sin ver el mensaje de error genérico "An error occurred. Contact the website administrator."
- **FR-003**: Ninguna ruta protegida DEBE mostrar el error genérico ni generar la excepción `TypeError: ... end_navigation_generation() takes 1 positional argument but 2 were given` cuando su `on_load` ejecuta el protector de rutas con una sesión válida. Se entiende por "ruta protegida" toda ruta cuyo `on_load` ejecuta `AuthState.require_login` (el inventario concreto de rutas se fija en el plan de validación).
- **FR-004**: El protector de rutas DEBE restablecer `is_loading = False` al finalizar su ejecución (intención original de la feature 077), sin cambiar el contrato del mixin `NavigationGenerationMixin`.
- **FR-005**: La corrección DEBE mantener el comportamiento de sesión expirada: redirección a `/login` con el mensaje "Sesión expirada. Por favor, inicie sesión nuevamente." y sin excepciones.
- **FR-006**: La corrección DEBE limitarse al flujo afectado y NO romper los demás consumidores de `end_navigation_generation()` (`personas_state`, `alertas_dashboard_state`), que lo invocan correctamente sin argumento.
- **FR-007**: La corrección NO DEBE introducir regresiones en los flujos ya corregidos por la feature 077: login válido, login inválido (credenciales), usuario inactivo, fallos de red/backend/BD, rate limiting, RBAC y logout.
- **FR-008**: El sistema DEBE incluir un test de regresión dedicado, unitario (sin I/O), que verifique que el protector de rutas (`require_login_background`) termina sin lanzar la excepción `TypeError` y que `end_navigation_generation()` se invoca sin argumento (blindaje del contrato del mixin, constitución §13). El test DEBE cubrir los tres caminos terminales del protector: (1) acceso permitido, (2) acceso denegado (redirección a `/login`), (3) generación obsoleta (`validate_generation == False` → DROP sin llamado a `end_navigation_generation`), más la invariante `is_loading == False` en todos los caminos. El test DEBE fallar con el bug presente antes de la corrección (RED, TDD) y pasar tras ella. El harness E2E (Playwright, reutilizado de la feature 077) debe quedar habilitado dentro del alcance de 078 para que SC-003/SC-004 sean verificables de forma automatizada.
- **FR-009**: El sistema DEBE registrar de forma segura (sin exponer credenciales, tokens, cookies ni datos de usuario) el desenlace del protector de rutas en producción (éxito o excepción) para permitir corroborar la ausencia del `TypeError` en los logs, tal como exigen SC-002 y SC-006.
- **FR-010**: Los tests existentes que codifican la firma errónea DEBEN actualizarse para validar el contrato real de `end_navigation_generation()` sin argumento: quitar el argumento en las aserciones de `test_proteccion_rutas.py` (`assert_called_with("test-gen-N")`) y des-mockear el método en `test_auth_login.py`, garantizando que la suite ni asertando ni mockeando re-codifique el bug.

### Key Entities *(include if feature involves data)*

- **Usuario**: Identidad con credenciales, estado activo/inactivo y rol. Sujeto del flujo de autenticación.
- **Sesión de Usuario**: Registro en BD con token y vigencia; base de la persistencia de la autenticación.
- **Generación de Navegación**: Mecanismo de control de concurrencia del mixin (`current_generation`, `is_loading`) que evita mutaciones de estados abandonados; el error de firma ocurre al finalizarla.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de los logins con credenciales válidas en el entorno desplegado llegan a `/dashboard` sin mostrar el mensaje de error genérico (0 % de pantallas de error tras login). En producción, la evidencia de este criterio es por logs: líneas de desenlace FR-009 (éxito/redirección/fin sin excepción) y SC-002; la observación visual en pantalla corresponde al E2E habilitado (FR-008/SC-003) contra el entorno desplegado.
- **SC-002**: 0 ocurrencias de la excepción `TypeError: ... end_navigation_generation() takes 1 positional argument but 2 were given` en los logs de producción en la ventana de validación de 24 horas o 100 inicios de sesión, lo que ocurra primero, iniciada al completarse el despliegue de la corrección; la verificación es una búsqueda activa del patrón de excepción y de las líneas de desenlace FR-009 en los logs, no solo ausencia visual.
- **SC-003**: El 100 % de las rutas protegidas cargan sin error genérico ni `TypeError` con una sesión válida, verificado por navegación automatizada sobre el inventario de rutas protegidas definido en el plan de validación; la verificación DEBE incluir la recarga de página (`page.reload()`) sobre cada ruta con sesión válida y confirmar ausencia de error genérico (Edge Case 4, Clarificación Q→A: recarga E2E).
- **SC-004**: El 100 % de la matriz de regresión de autenticación (la matriz de 10 puntos de la feature 077, que incluye como subconjunto obligatorio los comportamientos login válido, login inválido, logout, sesión expirada, RBAC y rate limiting) queda en verde tras la corrección.
- **SC-005**: `is_loading` queda en `False` al finalizar la ejecución del protector de rutas en el 100 % de los casos verificados (sin spinner atascado), conservando la intención de la feature 077; la verificación cubre tanto la carga inicial de la ruta como la recarga de página (`page.reload()`) con sesión válida (Clarificación Q→A: recarga E2E).
- **SC-006**: El test de regresión dedicado (FR-008) pasa en el 100 % de las ejecuciones de la suite y queda integrado como guardia permanente contra la reintroducción del `TypeError`.

## Assumptions

- La causa raíz está confirmada en el código: `auth_state.py:215` invoca `end_navigation_generation(gen_id)` pero el método del mixin no recibe argumentos. La solución es una corrección quirúrgica de la invocación (llamado sin argumento), sin rediseñar el mixin ni el control de concurrencia.
- La corrección se valida primero en local (reproducir el `TypeError`, corregir y ejecutar la matriz de regresión) y luego en el entorno desplegado (Railway, `inmovelar-production`) para confirmar la desaparición del error, siguiendo la práctica establecida en la feature 077. La validación en el entorno desplegada (SC-001/SC-002 con evidencia de logs, FR-009) es BLOQUEANTE para cerrar la feature.
- La feature `077-fix-login-spinner` ya corrigió el spinner infinito; este spec cubre únicamente la regresión de firma introducida por ese mismo cambio y NO reabre el flujo completo de login, ni los límites temporales de 5/10 segundos establecidos en dicha feature (quedan fuera del alcance de este fix).
- Se reutiliza la infraestructura de pruebas existente (tests de integración, tests E2E con Playwright y automatización de navegador) para las validaciones.
- El mensaje "An error occurred. Contact the website administrator." es el error genérico de Reflex en producción; no se busca reemplazar ese texto, sino eliminar la excepción que lo provoca.