# Diagnóstico: Novedad Navegación Dashboard a Módulos

## Clarifications

### Session 2026-09-03
- Q: ¿Qué patrón debe ser el estándar estricto para la inicialización de páginas (`on_load`)? → A: Retornar el manejador de eventos desde `on_load` y usar `@rx.event(background=True)` para la carga de datos.
- Q: ¿Cómo debe indicarse visualmente la carga asíncrona de datos en cada módulo? → A: Usar componentes de carga explícitos (skeleton o spinner) basados en el estado `is_loading` en cada módulo.
- Q: ¿Debe incluirse AuthState en el alcance de refactorización de on_load? → A: Sí, incluir explícitamente AuthState en la refactorización usando tareas en segundo plano.
- Q: ¿Cómo debe implementarse el control de concurrencia para navegación rápida (EC-003)? → A: Implementar un identificador de "generación" (ej. timestamp) en el estado para descartar mutaciones asíncronas caducadas.
- Q: ¿Qué sucede si la tarea background falla o excede el timeout (CHK002/CHK020)?   A: Regresar al usuario al Dashboard (Graceful Rollback) y mostrar un rx.toast indicando caducidad.
- Q: ¿Cuáles son las métricas de latencia y navegación rápida (CHK005/CHK007)?   A: Clics consecutivos en < 500ms se consideran navegación rápida. Asumir latencia de red P90 < 500ms para skeletons.
- Q: ¿Qué componente usar para carga y qué arquitectura en Railway (CHK004/CHK014)?   A: Usar rx.spinner() estándar. Asumir concurrencia asyncio nativa en Railway sin Redis inicialmente.
- Q: ¿Cómo se inyectan fallos de QA y seed data (CHK001/CHK003)?   A: Vía Chrome DevTools (Offline) para timeouts, y ejecución de seed.sql para auth.
- Q: ¿Criterios de Verificabilidad para QA (CHK005/CHK009)?   A: Caja Blanca (Estricto): QA debe verificar logs del servidor para ver drops de promesas y validar que el toast tenga texto exacto.

## 1. Problema Reportado
- Al hacer login, el sistema direcciona al Dashboard.
- Al dar clic a otro módulo (ej. Personas), vuelve a cargar el Dashboard.
- En un segundo intento, muestra la página de Personas pero el frontend no carga correctamente (estado corrupto o error de hidratación).

## 2. Análisis de Causa Raíz (Root Cause Analysis)

Mediante ingeniería inversa del ciclo de vida de Reflex y el manejo de estado, se identificó el siguiente flujo anómalo:

1. **Interrupción de Transición (Route Abort):**
   - Cuando el usuario hace clic en el enlace "Personas" en el Sidebar, el enrutador cliente (React Router/NextJS en Reflex) inicia una navegación suave (soft navigation) hacia `/personas`.
   - Reflex dispara inmediatamente los eventos configurados en el `on_load` de la página de destino en el backend: `[AuthState.require_login, PersonasState.load_personas]`.
   - La función `PersonasState.load_personas` contiene un `yield` vacío a mitad de su ejecución (`self.is_loading = True; yield`).
   - Este `yield` fuerza a Reflex a enviar una actualización de estado (Delta) al frontend inmediatamente.
   - **Fallo del Router:** Si el frontend recibe una mutación de estado *mientras* está en plena transición de ruta, el router cliente de Reflex/React aborta la navegación en curso, revirtiendo al usuario a la página anterior (Dashboard). Por eso "vuelve a cargar el Dashboard".

2. **Corrupción del Frontend (White Screen / Hydration Error):**
   - En el segundo intento (o si el usuario da múltiples clics), la transición puede forzarse o el estado de carga (`is_loading = True`) ya está mutado.
   - Sin embargo, debido al montaje fallido anterior y a que el estado fue mutado de forma asíncrona sin un `@rx.background`, los componentes de React pueden perder sincronía (hidratación corrupta), provocando que la UI de Personas se rompa o "no cargue correctamente".

## 3. Comprobación de Patrón
El problema no es exclusivo de `PersonasState`. Se confirmó mediante búsqueda en el código que otras clases de estado también usan el anti-patrón de `yield` síncrono dentro de las funciones llamadas en el `on_load`:
- `PersonasState.load_personas`
- `AlertasState.load_alertas`
- `AlertasDashboardState.load_alertas`

Otras páginas (como `ProveedoresState` o `DashboardState`) funcionan correctamente porque manejan su `on_load` retornando un evento (ej. `return ProveedoresState.load_proveedores`) y la función de carga usa `@rx.event(background=True)`.

## 4. Solución Arquitectónica Propuesta
- **Refactorización de `on_load`:** 
  1. No usar `yield` vacíos en métodos invocados directamente desde `on_load`.
  2. Retornar los manejadores de eventos desde `on_load` (ej. `return cls.load_data`) y decorar los métodos de carga con `@rx.event(background=True)`.
  3. Aplicar la solución a `PersonasState`, `AlertasState`, `AlertasDashboardState` y `AuthState` para garantizar que la validación de sesión no bloquee las rutas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navegación Exitosa Post-Login (Priority: P1)

Como usuario autenticado, quiero poder navegar desde el Dashboard a cualquier otro módulo (por ejemplo, Personas) en el primer intento y que la interfaz de usuario cargue correctamente.

**Why this priority**: Es el flujo principal de navegación de la aplicación; sin esto, la experiencia de usuario se ve gravemente degradada y puede causar confusión al parecer que los clics no funcionan.

**Independent Test**: Se puede probar independientemente haciendo login e intentando hacer clic en una opción del menú lateral. Se espera que cargue de inmediato el módulo correspondiente sin requerir un doble clic y con el frontend completo.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en la página de Dashboard, **When** hace clic en el enlace del módulo "Personas", **Then** el sistema debe direccionar inmediatamente a la página de Personas y renderizar todos los componentes frontend correctamente.
2. **Given** un usuario autenticado que acaba de ingresar, **When** hace clic en cualquier otro módulo del menú, **Then** no debe recargarse la página del Dashboard en el primer intento.

### Edge Cases
 
 - En caso de requerir autenticación post-login, el sistema debe bloquear la navegación de forma transparente, permitiendo la redirección final solo una vez validado el token.
 - En caso de latencia de red alta durante la transición, el módulo DEBE renderizar componentes de carga visual (*skeleton* o *spinner* asociados a `is_loading`) para dar retroalimentación inmediata sin abortar la ruta.
 - En caso de navegación rápida entre módulos, el sistema DEBE evitar condiciones de carrera en el estado global implementando un identificador de "generación" (ej. timestamp de navegación); las peticiones asíncronas caducadas deben ser descartadas sin mutar el estado.
 - En caso de que la carga asíncrona falle o exceda el timeout (o si el ID de generación falla), el sistema DEBE aplicar un rollback grácil: devolver al usuario al Dashboard y mostrar un rx.toast (Warning).
 - Para pruebas objetivas, la navegación rápida se define como clics con diferencia < 500ms, y la latencia esperada de red es de P90 < 500ms.
 - Para los indicadores de carga se utilizará el componente genérico rx.spinner() centrado, sin requerir implementaciones CSS complejas (Skeleton).
 
 ## Requirements *(mandatory)*
 
 ### Functional Requirements
 
 - **FR-001**: El sistema DEBE procesar la navegación hacia un nuevo módulo en el primer intento tras el clic en el menú.
 - **FR-002**: El sistema NO DEBE recargar el Dashboard cuando se solicita explícitamente otro módulo.
 - **FR-003**: El sistema DEBE asegurar que la página destino se renderice sin errores de hidratación, utilizando indicadores de carga explícitos mientras las peticiones asíncronas de datos se resuelven de fondo.
 - **FR-004**: El sistema DEBE preservar el token/estado de sesión consistentemente a través de los cambios de ruta sin forzar re-evaluaciones innecesarias de redirección.

### Key Entities

- **Estado de Autenticación**: El componente o clase que maneja la sesión activa del usuario y determina las redirecciones de seguridad.
- **Estado Global/Base**: El State principal de Reflex que se carga o evalúa en cada navegación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las transiciones desde Dashboard a otro módulo tras el login se completan en el primer clic.
- **SC-002**: Tiempo de respuesta visual de la transición de página es inferior a 1 segundo.
- **SC-003**: 0% de recargas redundantes del Dashboard durante la navegación a otras secciones.
- **SC-004**: Los componentes de la página destino se renderizan completamente (estilos, datos, interactividad) en la primera carga.

## Assumptions

- Se asume que el problema de renderizado ("no carga correctamente el frontend") es un síntoma de un estado inconsistente de Reflex (probablemente una interrupción en el event loop del State o un problema con on_load).
- Se asume que el comportamiento ocurre en un entorno local y en producción de forma consistente.
- Se asume que la migración reciente (Flet a Reflex) o los decoradores de RBAC/autenticación podrían estar interfiriendo en el ciclo de vida de la ruta.
- Se asume que el entorno de Railway soportará los @rx.event(background=True) usando el event loop nativo de asyncio, sin necesidad de aprovisionar un broker de Redis en esta fase.


