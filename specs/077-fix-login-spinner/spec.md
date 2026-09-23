# Feature Specification: Corrección del flujo de inicio de sesión (spinner infinito en "Acceder al panel")

**Feature Branch**: `077-fix-login-spinner`

**Created**: 2026-09-22

**Status**: Draft

**Input**: User description: "URGENTE: ingeniería inversa robusta, profunda y exhaustiva del flujo de inicio de sesión (Login). El botón 'Acceder al panel' muestra un spinner de carga y permanece indefinidamente en ese estado (bucle de carga), sin completar el proceso ni permitir el acceso a la aplicación. El usuario queda bloqueado en la pantalla de Login. Se requiere identificar la causa raíz del extremo a extremo (validación de credenciales, solicitud Frontend→Backend, endpoint de login, respuesta de la API, manejo de estados de carga, errores/excepciones, persistencia de sesión, lógica post-autenticación, redirección al panel, carga inicial del panel, consultas de BD, roles y permisos, variables de entorno, timeouts, promesas/peticiones pendientes, errores JS/TS). La solución DEBE atacar la causa raíz y NO limitarse a ocultar el spinner o poner un timeout artificial. Validación obligatoria de 10 puntos (login válido, fin del estado de carga, autenticación exitosa, persistencia de sesión, redirección, carga del panel, rol/permisos, credenciales inválidas, errores de red/Backend/BD, ausencia de regresiones)."

## Contexto e ingeniería inversa (estado actual verificado)

El flujo de autenticación actual se compone de las siguientes piezas, verificadas en el código fuente:

1. **Interfaz de Login** (`/login`): formulario HTML (`rx.form`) con campos `username` y `password` (`name="username"`, `name="password"`) y botón `type="submit"` con etiqueta "Acceder al Panel" y `loading=AuthState.is_loading`. Al enviar, Reflex invoca el event handler `AuthState.login(form_data)`.
2. **Manejo de estados de carga**: `is_loading` se declara en `NavigationGenerationMixin` (`is_loading: bool = False`) y lo hereda `AuthState`.
3. **Event handler de login** (`AuthState.login`):
   - Rate limiting por IP (máximo 5 intentos en 15 minutos) en memoria de proceso.
   - Activa `is_loading = True` y emite un `yield` para enviar el estado de carga al frontend.
   - Autentica contra PostgreSQL mediante `ServicioAutenticacion.autenticar(usuario, contraseña)` (validación de existencia, estado activo, hash Bcrypt con migración transparente SHA256→Bcrypt).
   - Crea sesión (`ServicioAutenticacion.crear_sesion`) con token `secrets.token_urlsafe(32)`, vigencia de 8 horas en BD.
   - Persiste el token en cookies ofuscadas (`_s` sesión, `_r` fingerprint), 24 h, `secure` en producción.
   - Llena el estado en memoria (`_user_data`, `is_authenticated`, `user_nombre`, `user_rol`, `user_id`).
   - Carga permisos del rol (`ServicioPermisos.obtener_permisos_rol`) y propaga `permissions_map` / `allowed_modules`.
   - Restablece `is_loading = False` y emite `yield rx.redirect("/dashboard")`.
   - En errores (`ErrorAutenticacion`, `ExcepcionDominio`, `Exception`) restablece `is_loading = False` y fija `error_message`.
4. **Protector de rutas protegidas** (`AuthState.require_login`, usado en `on_load` de `/dashboard` y ~20 páginas): inicia una "generación de navegación" con `start_navigation_generation()` que **fija `is_loading = True`**, y encola una tarea de fondo `require_login_background(gen_id)`.
5. **Carga del Dashboard** (`/dashboard`): `on_load=[AuthState.require_login, DashboardState.on_load]`.
6. **Validación de sesión** (`AuthState._validate_session`): usa la cookie `_s` contra BD; si el token es inválido redirige a `/login`; ante error transitorio de BD no invalida la sesión pero retorna `False`.

Comportamiento reportado: al ingresar credenciales y ejecutar la acción, el botón muestra el spinner y **nunca finaliza**; el usuario queda bloqueado en `/login`.

### Alcance del análisis end-to-end exigido

La ingeniería inversa debe cubrir explícitamente, con evidencia (logs, red, trazas), cada uno de estos eslabones y determinar en cuál de ellos se rompe la cadena:

- Validación de credenciales (incluida la migración automática de hash y la actualización de "último acceso" que escribe en BD).
- Solicitud enviada desde el Frontend al Backend y endpoint responsable del inicio de sesión.
- Respuesta de la API / event handler y su ciclo de vida completo (incluidas todas las rutas de `yield` / `return` del generador).
- Manejo de estados de carga (`is_loading` en todas las rutas, incluidas las tareas de fondo que lo activan sin restablecerlo).
- Gestión de errores y excepciones (incluidas excepciones fuera del bloque `try` y fallos silenciosos).
- Persistencia de sesión: cookies `_s`/`_r` y tabla de sesiones en BD (vigencia, activación de la cookie desde un event handler generador, comportamiento con `rx.redirect`).
- Lógica ejecutada después de una autenticación exitosa (permisos, fingerprints).
- Redirección hacia el panel (`/dashboard`) y su interacción con el `on_load`.
- Carga inicial del panel y sus dependencias (`DashboardState.on_load`, permisos del rol).
- Consultas a la base de datos relacionadas con el usuario autenticado (conexión, bloqueos, transacciones no cerradas).
- Gestión de roles y permisos y su impacto en el renderizado inicial del panel.
- Variables de entorno y configuraciones relacionadas con autenticación (entorno de producción vs. desarrollo, `secure` de cookies).
- Timeouts, conectividad, promesas pendientes o peticiones que no finalizan.
- Errores en JavaScript/TypeScript que impidan que el estado de carga se restablezca.

## Clarifications

### Session 2026-09-22

- Q: ¿Cómo termina un login cuya dependencia (backend/BD) nunca responde, reconcilando FR-002 (sin timeout artificial) con FR-009/SC-006 (todo desenlace debe terminar)? → A: Opción B — Causa raíz + límites en la capa de recurso. La operación real DEBE concluir por sí misma en todo escenario; además se aplican límites en la capa de recurso/infraestructura (timeout de consulta/conexión a base de datos, deadline de la operación) que convierten la espera en un ERROR REAL y visible. El spinner se restablece porque la operación subyacente concluyó en error, NUNCA por un temporizador de interfaz que finja éxito o eluda el desenlace.
- Q: ¿En qué entornos se debe reproducir, corregir y validar el flujo de login? → A: Opción B — Local primero (corrección y regresión) y luego validación del flujo completo en el entorno desplegado con credenciales reales de prueba (incluidos roles y permisos). La validación en el entorno desplegado es bloqueante para cerrar la feature.
- Q: ¿Qué método de evidencia hace medibles las métricas de aceptación (0 % de spinners, causa raíz reproducible y diagnóstico)? → A: Opción D — Automatización E2E de navegador (estado observable del botón, carga finalizada, redirección y consola limpia) + traza de logs del backend del ciclo de vida del evento (inicio/desenlace/error) para correlacionar el estado del frontend con el resultado real + capturas de pantalla antes/después (regresión visual). Aplicable en ambos entornos de validación.
- Q: ¿Se fijan textos canónicos exactos para cada desenlace terminal del login? → A: Opción A — Sí. Textos canónicos: credenciales inválidas → "Credenciales inválidas. Verifique usuario y contraseña."; usuario inactivo → "El usuario se encuentra inactivo."; red/backend sin respuesta → "No se pudo conectar con el servidor. Verifique su conexión e intente de nuevo."; base de datos no disponible → "El servicio no está disponible en este momento. Intente de nuevo."; excepción inesperada → "Ocurrió un error inesperado. Intente de nuevo."; bloqueo por intentos → "Demasiados intentos. Intente de nuevo en 15 minutos.".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Login válido que finaliza su carga y llega al panel (Priority: P1)

Como usuario autenticado, quiero ingresar mis credenciales válidas, presionar "Acceder al panel" y entrar al sistema, para poder operar la aplicación.

**Why this priority**: Es el flujo central y el síntoma reportado: sin él, ningún usuario puede acceder al sistema. Es la corrección de causa raíz y la validación principal de la feature.

**Independent Test**: Con credenciales válidas activas, enviar el formulario de login y verificar que: (a) el evento termina, (b) `is_loading` vuelve a `False`, (c) la sesión persiste, (d) se navega a `/dashboard` y (e) el panel carga con los permisos del rol.

**Acceptance Scenarios**:

1. **Given** un usuario con credenciales válidas y activo, **When** envía el formulario de login, **Then** el spinner del botón termina, la sesión queda establecida y el usuario es redirigido a `/dashboard`.
2. **Given** el login exitoso, **When** el dashboard inicia su carga (`on_load`), **Then** la sesión se valida, los permisos del rol se cargan y el panel renderiza sin volver a `/login`.
3. **Given** una recarga de página en `/dashboard`, **When** el navegador vuelve a cargar, **Then** la sesión persiste y el usuario permanece autenticado dentro de la ventana de validez.
4. **Given** el login exitoso, **When** se inspeccionan las cookies y el estado, **Then** el token de sesión queda persistido y `is_loading` no queda activo.

---

### User Story 2 - Credenciales inválidas que muestran error y restablecen la carga (Priority: P1)

Como usuario autenticado, quiero recibir un mensaje claro si mis credenciales son incorrectas, para poder corregirlas, garantizando que el spinner nunca quede atascado.

**Why this priority**: El manejo de credenciales inválidas es uno de los puntos de la matriz de validación obligatoria y debe desenbocar en un estado terminal (mensaje + carga restablecida), nunca en un loop.

**Independent Test**: Enviar el formulario con una contraseña incorrecta (rol activo) y con un usuario inexistente; en ambos casos verificar mensaje de error visible y `is_loading = False`.

**Acceptance Scenarios**:

1. **Given** un usuario con contraseña incorrecta, **When** envía el formulario, **Then** el sistema muestra "Credenciales inválidas. Verifique usuario y contraseña." y el botón deja de cargar.
2. **Given** un usuario inexistente, **When** envía el formulario, **Then** el sistema muestra "Credenciales inválidas. Verifique usuario y contraseña." y restablece el spinner.
3. **Given** un usuario inactivo, **When** envía el formulario, **Then** el sistema muestra "El usuario se encuentra inactivo." y restablece el spinner.

---

### User Story 3 - Fallos de red / Backend / Base de Datos manejados sin cuelgue (Priority: P2)

Como usuario autenticado, quiero que ante una falla de conectividad, del servicio backend o de la base de datos el login termine con un mensaje de error comprensible y el estado de carga restablecido, para no quedar bloqueado a ciegas.

**Why this priority**: Un desenlace no terminal del evento (excepción no capturada, petición sin finalizar, conexión bloqueada) es la familia de causas más probable del spinner infinito; eliminar esta clase de fallos es parte de la corrección de causa raíz.

**Independent Test**: Simular la indisponibilidad de la base de datos y del backend durante el envío del formulario y verificar que el evento termina siempre (mensaje + `is_loading = False`) dentro de un límite razonable.

**Acceptance Scenarios**:

1. **Given** la base de datos no responde, **When** se envía el formulario, **Then** el login finaliza con el mensaje canónico "El servicio no está disponible en este momento. Intente de nuevo." y el spinner se restablece (sin colgarse).
2. **Given** el backend tarda más de lo esperado (petición sin respuesta), **When** se envía el formulario, **Then** el evento no queda pendiente indefinidamente: termina con el mensaje canónico "No se pudo conectar con el servidor. Verifique su conexión e intente de nuevo." al agotarse el límite de la capa de recurso.
3. **Given** una excepción inesperada durante el login, **When** se envía el formulario, **Then** el estado de carga se restablece, el sistema muestra "Ocurrió un error inesperado. Intente de nuevo." y el error no queda silenciado en producción (se registra de forma segura).

---

### User Story 4 - Cuidado y cierre: acceso por rol/permisos y sin regresiones en otros flujos de autenticación (Priority: P2)

Como administrador del sistema, quiero que la corrección del login no altere el control de acceso por roles (RBAC), el cierre de sesión, el bloqueo por intentos ni las rutas protegidas, para que el cambio no introduzca regresiones.

**Why this priority**: El login es la puerta de entrada de toda la app; un arreglo que rompa RBAC, `logout`, rutas protegidas o rate limiting es inaceptable. Es requisito de cierre de la feature.

**Independent Test**: Ejecutar la matriz de regresión de autenticación (login válido, login inválido, logout, recarga con sesión, acceso a ruta protegida sin sesión, acceso a módulos según rol, bloqueo por 5 intentos fallidos) y comprobar que todos los comportamientos se conservan.

**Acceptance Scenarios**:

1. **Given** un usuario Administrador autenticado, **When** accede a un módulo, **Then** se le concede acceso; un usuario con rol restringido no accede (RBAC intacto).
2. **Given** una sesión activa, **When** se presiona cerrar sesión, **Then** se redirige a `/login` y las cookies/estado de sesión se limpian.
3. **Given** una sesión expirada, **When** se accede a una ruta protegida, **Then** el sistema redirige a `/login` con mensaje de sesión expirada.
4. **Given** más de 5 intentos fallidos desde la misma IP, **When** se intenta de nuevo, **Then** el sistema bloquea temporalmente según la política vigente.
5. **Given** la corrección implementada, **When** se revisa el código y la configuración, **Then** no existe ningún timeout artificial ni ocultamiento del spinner: la carga depende 100 % del resultado real del evento.

---

### Edge Cases

- ¿Envío doble del formulario (doble clic)? → El sistema no debe lanzar autenticaciones concurrentes ni dejar estados de carga inconsistentes.
- ¿Usuario con hash SHA256 legado que se migra a Bcrypt durante el login? → La migración escribe en BD en medio del flujo; debe completarse y no interrumpir el login.
- ¿Token de sesión no recibido por el navegador (cookie bloqueada/no propagada tras `rx.redirect`)? → Tras la redirección, la sesión debe existir; si no, el diagnóstico debe explicar en qué eslabón se perdió.
- ¿`is_loading` dejada en `True` por una tarea de fondo previa (protector de rutas) que no la restablece? → El estado de carga inicial de la pantalla de login debe ser coherente y nunca quedar activo sin una operación en curso.
- ¿Error de base de datos transitorio durante la validación de sesión en el `on_load` del panel? → No debe invalidar la sesión ni producir loops de redirección.
- ¿Sesión expirada o token inválido? → Redirección a `/login` con mensaje, sin loop.
- ¿Variables de entorno ausentes o entorno de producción con cookies `secure`? → El flujo no debe romperse por configuración; el diagnóstico debe cubrir este eslabón.
- ¿Rate limiting alcanzado? → Mensaje de "Demasiados intentos" y botón restablecido.
- ¿Reintento tras un fallo de red? → El usuario puede volver a intentar sin que el estado quede contaminado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE ejecutar una ingeniería inversa end-to-end del flujo de inicio de sesión que documente, con evidencia (automatización E2E de navegador sobre el estado observable del botón, traza de logs del backend del ciclo de vida del evento, trazas de red, salidas de consola y capturas antes/después — método de la Clarificación 2026-09-22), cada eslabón del alcance definido en el Contexto y determine en qué punto exacto la cadena se rompe (por qué el spinner no finaliza y dónde queda bloqueada la operación).
- **FR-002**: El sistema DEBE identificar y corregir la **causa raíz** del spinner infinito; la solución NO puede limitarse a ocultar el indicador de carga, ni establecer un tiempo de espera artificial, ni forzar un desenlace aparente sin corregir la operación subyacente.
- **FR-003**: El evento de inicio de sesión DEBE terminar en un estado terminal en TODAS sus rutas: éxito (login válido), error de créditos (credenciales inválidas/usuario inactivo), error de negocio y error inesperado. Ninguna ruta puede dejar la operación pendiente ni el indicador de carga activo.
- **FR-004**: El indicador de carga del botón "Acceder al panel" DEBE activarse solo mientras la operación está en curso y DEBE desactivarse en cuanto el login llega a un desenlace (éxito o error), incluyendo los casos de fallo de red, backend o base de datos.
- **FR-005**: Un login exitoso DEBE: autenticar al usuario, persistir la sesión de forma que sobreviva a la redirección y a una recarga de página dentro de la ventana de validez, y redirigir al panel `/dashboard`.
- **FR-006**: El panel `/dashboard` DEBE cargar correctamente tras el login: validar la sesión, cargar los permisos del rol y renderizar la información según los permisos, sin redirigir de vuelta a `/login` para un usuario válido.
- **FR-007**: El login DEBE mantener el control de acceso por roles y permisos (RBAC) vigente e intacto tras la corrección, tanto en el renderizado como en el backend.
- **FR-008**: El login DEBE mantener la política de bloqueo por intentos fallidos (rate limiting) vigente y el bloqueo NO debe impedir que la carga se restablezca ni dejar el evento pendiente.
- **FR-009**: Ante errores de red, backend o base de datos, el sistema DEBE finalizar la operación con un mensaje comprensible para el usuario y el estado de carga restablecido, sin cuelgues ni reintentos infinitos automáticos. El desenlace DEBE producirse porque la operación subyacente concluyó (éxito o error real); si una dependencia no responde, se DEBEN aplicar límites en la capa de recurso (timeout de consulta/conexión a base de datos y deadline de la operación) que conviertan la espera en un error real y visible. Queda PROHIBIDO un temporizador en la interfaz que finja éxito o eluda el desenlace real.
- **FR-010**: La corrección NO DEBE generar regresiones en los demás flujos de autenticación: cierre de sesión, rutas protegidas, redirección por sesión expirada, migración de hash y RBAC.
- **FR-011**: El sistema DEBE registrar de forma segura (sin exponer credenciales) los eventos de autenticación relevantes en producción para permitir corroborar que el flujo opera correctamente tras la corrección.

### Key Entities *(include if feature involves data)*

- **Usuario**: Identidad con credenciales (nombre de usuario, hash de contraseña), estado activo/inactivo, rol y fecha de último acceso. Es el sujeto del login.
- **Sesión de Usuario**: Registro en BD con token de sesión, usuario, fechas de inicio y fin (vigencia). Es la base de la persistencia de la autenticación.
- **Cookie de sesión (`_s`) y fingerprint (`_r`)**: Mecanismo de transporte de la sesión entre frontend y backend; su correcta emisión/persistencia es parte del flujo.
- **Rol / Permiso (RBAC)**: Conjunto de módulos y acciones asociados al rol del usuario; se carga tras el login y determina lo visible y lo permitido en el panel.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de los intentos de login con credenciales válidas finaliza el estado de carga y llega al panel `/dashboard` sin intervención manual (0 % de los botones quedan en spinner), verificado por automatización E2E de navegador sobre el estado observable del botón y la redirección.
- **SC-002**: El proceso credencial → panel completa en menos de 5 segundos en el entorno local de validación y en menos de 10 segundos en el entorno desplegado, para un usuario válido con datos nominales, sin que el valor dependa de un timeout artificial.
- **SC-003**: El estado de carga queda activo en 0 % de los desenlaces terminales (éxito o error); verificado por E2E de navegador correlacionado con la traza de logs del backend donde se observa que el evento llega a un desenlace real en cada caso.
- **SC-004**: El 100 % de los logins exitosos persisten la sesión y soportan una recarga de página en `/dashboard` dentro de la ventana de validez sin volver a pedir credenciales.
- **SC-005**: El 100 % de los intentos con credenciales inválidas muestran un mensaje claro y restablecen el spinner en menos de 2 segundos tras la respuesta del backend.
- **SC-006**: El 100 % de los escenarios de fallo de red, backend o base de datos simulados terminan con un mensaje y el spinner restablecido; 0 % quedan pendientes indefinidamente. El desenlace se produce porque la operación subyacente concluyó (incluidos los límites de la capa de recurso que la convierten en un error real), nunca por un temporizador de interfaz.
- **SC-007**: 0 regresiones en los demás flujos de autenticación verificados: login válido, login inválido, logout, sesión expirada, rutas protegidas, RBAC y rate limiting (matriz completa de regresión en verde).
- **SC-008**: La causa raíz queda documentada con evidencia reproducible antes/después (pasos de reproducción E2E, traza de logs del ciclo de vida del evento, capturas antes/después y el punto exacto del flujo donde la operación quedaba bloqueada) en el artefacto de la feature, de modo que cualquier ingeniero pueda verificarla.

## Assumptions

- El bug reportado se manifiesta con credenciales válidas y activas; la corrección se valida en dos fases con orden firme (Clarificación 2026-09-22): (1) entorno local/dev con base de datos local para reproducir, corregir y ejecutar la matriz de regresión; (2) entorno desplegado con credenciales reales de prueba para la validación del flujo completo (10 puntos, incluidos roles y permisos). La fase (2) es bloqueante para cerrar la feature.
- La autenticación es por usuario y contraseña contra PostgreSQL con sesiones en BD y cookies; se reutiliza la infraestructura existente, sin introducir un proveedor de identidad nuevo.
- La sesión tiene vigencia de 8 horas en BD y cookies de 24 horas; estos valores se conservan salvo que el diagnóstico demuestre que participan en la causa raíz.
- La política de rate limiting (máximo 5 intentos en 15 minutos por IP) y el RBAC vigentes NO se modifican: solo se garantiza que no produzcan cuelgues.
- La corrección se hace por cirugía mínima sobre el flujo de autenticación existente; no se rediseña la arquitectura de sesiones ni se cambia el esquema de base de datos.
- La "finalización" de la carga se evalúa por el resultado real del evento (éxito o error), nunca por un temporizador; un timeout artificial en la interfaz se considera una solución inválida y NO cumple esta feature. Los límites de tiempo en la capa de recurso (consulta/conexión a base de datos y deadline de la operación) SÍ se permiten y son la vía para garantizar el desenlace cuando una dependencia no responde, porque producen un error real y visible (Clarificación 2026-09-22).
- Los escenarios de fallo de red/backend/BD se simulan de forma controlada en el entorno de validación (por ejemplo, desconectando recursos o forzando excepciones) sin afectar datos reales.
- Métricas de rendimiento límite de las consultas de carga del panel no son parte de este spec: el límite de 5/10 segundos cubre el trayecto credencial → panel con datos nominales y se afina en el plan si el diagnóstico lo exige.