# Auth Flow Requirements Quality Checklist

**Purpose**: Validar la calidad, claridad, completitud y consistencia de los requisitos de la corrección del flujo de inicio de sesión (spinner infinito en "Acceder al panel") antes de la implementación
**Created**: 2026-09-22
**Feature**: [spec.md](specs/077-fix-login-spinner/spec.md)

**Note**: Este checklist evalúa la CALIDAD DE LOS REQUISITOS (completitud, claridad, consistencia, medibilidad, cobertura), no el comportamiento de la implementación.

## Requirement Completeness

- [x] CHK001 ¿La especificación exige documentar con evidencia cada eslabón del flujo end-to-end del login (validación, petición, respuesta, estados de carga, errores, sesión, redirección, panel, permisos, entorno) y determinar en cuál se rompe la cadena? [Completeness, Spec §Contexto / FR-001]
- [x] CHK002 ¿Está documentado que la solución debe atacar la causa raíz y que quedan explícitamente prohibidos los mitigantes sintomáticos (ocultar el spinner, timeout artificial)? [Completeness, Spec §FR-002]
- [x] CHK003 ¿Existen requisitos de estado terminal para TODAS las rutas del login (éxito, credenciales inválidas, usuario inactivo, error de negocio, error inesperado)? [Completeness, Spec §FR-003]
- [x] CHK004 ¿Están definidos requisitos de persistencia de sesión que cubran la redirección y la recarga de página dentro de la ventana de validez? [Completeness, Spec §FR-005 / SC-004]
- [x] CHK005 ¿Se especifica un requisito de registro/observabilidad seguro (sin exponer credenciales) para los eventos de autenticación en producción? [Completeness, Spec §FR-011]
- [x] CHK006 ¿Se define qué evidencia concreta (logs, trazas de red/consola, salidas de diagnóstico) debe producir el análisis para confirmar la causa raíz? [Gap, Spec §Contexto]

## Requirement Clarity

- [x] CHK007 ¿El síntoma "spinner infinito" se describe con criterios objetivos y verificables (estado de carga activo sin desenlace conocido), no solo con una descripción cualitativa? [Clarity, Spec §Contexto / US1]
- [x] CHK008 ¿Los límites de SC-002 (5s/10s) se definen como medición del trayecto funcional credencial→panel y NO como un timeout que enmascare el bug, sin ambigüedad? [Clarity, Spec §SC-002 / FR-002]
- [x] CHK009 ¿Queda explícito que la "finalización de la carga" se mide por el resultado real del evento (éxito o error) y nunca por temporizador? [Clarity, Spec §Assumptions]
- [x] CHK010 ¿"Sesión persistente" tiene fronteras verificables (ventana de validez, recarga de página, cookie establecida/transmitida)? [Clarity, Spec §FR-005 / SC-004]
- [x] CHK011 ¿El texto o criterio mínimo de los mensajes de error está especificado para cada desenlace (credenciales, red, BD, negocio)? [Gap, Spec §US2 / US3]

## Requirement Consistency

- [x] CHK012 ¿El manejo del estado de carga es consistente entre el login (FR-003/FR-004) y el protector de rutas/tareas de fondo que también lo manipulan? [Consistency, Spec §Contexto]
- [x] CHK013 ¿Los requisitos de redirección son consistentes entre FR-005 (login→panel), FR-006 (el panel valida la sesión) y el edge case de sesión expirada (→/login sin loop)? [Consistency, Spec §FR-005 / FR-006]
- [x] CHK014 ¿Las políticas de rate limiting y RBAC que se declaran "no modificar" son consistentes entre FR-007, FR-008 y la User Story 4? [Consistency, Spec §FR-007 / FR-008 / US4]
- [x] CHK015 ¿El alcance "sin regresiones" (FR-010) es consistente con las historias de usuario y los edge cases (migración de hash, doble clic, sesión expirada)? [Consistency, Spec §FR-010 / Edge Cases]

## Acceptance Criteria Quality

- [x] CHK016 ¿Las condiciones de aceptación de cada User Story son verificables de forma objetiva, sin depender de interpretación del implementador? [Acceptance Criteria, Spec §US1–US4]
- [x] CHK017 ¿La SC-001 ("0 % de botones en spinner") define cómo se observa/contabiliza ese resultado de forma reproducible? [Gap, Spec §SC-001]
- [x] CHK018 ¿La SC-003 (estado de carga activo en 0 % de desenlaces terminales) especifica el método de observación (estado/consola) y no solo la métrica? [Gap, Spec §SC-003]
- [x] CHK019 ¿La SC-005 (2s para credenciales inválidas) usa el mismo criterio de medición que el resto de criterios de tiempo para poder compararse? [Measurability, Spec §SC-005 / SC-002]
- [x] CHK020 ¿La SC-008 define requisitos de contenido del artefacto de causa raíz (reproducibilidad, antes/después, punto exacto del bloqueo)? [Clarity, Spec §SC-008]

## Scenario Coverage

- [x] CHK021 ¿Los escenarios de excepción/error (red, backend, BD) tienen requisitos funcionales exigibles (FR-009) y no solo narrativas en historias? [Coverage, Spec §US3 / FR-009]
- [x] CHK022 ¿Existe requisito para el escenario de reintento tras un fallo (el usuario puede volver a intentar sin estado contaminado)? [Coverage, Spec §Edge Cases]
- [x] CHK023 ¿Está cubierto el escenario de cookie no propagada/bloqueada tras la redirección (sesión existe en BD pero no llega al navegador)? [Coverage, Spec §Edge Cases]
- [x] CHK024 ¿El estado de carga heredado (una tarea de fondo/protector de rutas que deja el indicador activo sin operación en curso) está cubierto por algún requisito? [Gap, Spec §Edge Cases]
- [x] CHK025 ¿La migración transparente de hash durante el login (SHA256→Bcrypt con escritura en BD en mitad del flujo) tiene requisito verificable y no interrumpe el login? [Coverage, Spec §Edge Cases]

## Edge Case Coverage

- [x] CHK026 ¿Los edge cases listados (doble envío, rate limiting, usuario inactivo, sesión expirada, error transitorio de BD, entorno/cookies) están vinculados a requisitos funcionales exigibles y no quedan solo como notas? [Edge Case Coverage, Spec §Edge Cases]
- [x] CHK027 ¿Se especifica el comportamiento exigido ante configuración/variables de entorno ausentes o cookies `secure` en producción sin romper el flujo? [Gap, Spec §Edge Cases]

## Non-Functional Requirements

- [x] CHK028 ¿Los requisitos de rendimiento del trayecto credencial→panel definen qué es degradación aceptable frente a qué es cuelgue, con criterios objetivos? [NFR, Spec §SC-002]
- [x] CHK029 ¿Se definen requisitos de seguridad para el diagnóstico/logs (no exponer credenciales ni datos sensibles en ninguna salida)? [NFR Security, Spec §FR-011]
- [x] CHK030 ¿Existen requisitos de fiabilidad que garanticen que toda petición/promesa pendiente del login termina o se aborta, SIN depender de un timeout artificial? [NFR Reliability, Gap, Spec §FR-002 / FR-009]

## Dependencies & Assumptions

- [x] CHK031 ¿Las asunciones de entorno de validación (local vs. desplegado) y disponibilidad de credenciales de prueba son verificables y están documentadas? [Assumption, Spec §Assumptions]
- [x] CHK032 ¿Están documentadas las dependencias de infraestructura (base de datos, cookies, gestión de estado) y el comportamiento esperado si una falla? [Dependency, Spec §Assumptions]
- [x] CHK033 ¿La asunción "un timeout artificial es solución inválida" está redactada sin margen de interpretación conflictiva con otros requisitos? [Assumption, Spec §FR-002 / Assumptions]

## Ambiguities & Conflicts

- [x] CHK034 ¿"Finaliza la carga" (FR-003) no admite dos interpretaciones (evento terminado vs. spinner apagado) que entren en conflicto con SC-003/SC-006? [Ambiguity, Spec §FR-003]
- [x] CHK035 ¿El posible conflicto entre SC-002 (límites de tiempo) y FR-002/Assumptions (prohibición de timeout artificial) está resuelto explícitamente en el spec? [Conflict, Spec §SC-002 / FR-002 / Assumptions]
- [x] CHK036 ¿Queda sin ambigüedad en qué entorno(s) debe reproducirse y verificarse el bug (producción, desarrollo, ambos) y qué evidencia se admite por entorno? [Ambiguity, Spec §Assumptions]

## Evidencia Visual (imagen del síntoma)

Confirmado en imagen: pantalla de login con usuario y contraseña diligenciados, botón "Acceder al Panel" **deshabilitado (gris) con spinner circular continuo** (~ "el frontend inició una petición asíncrona y quedó esperando").

- [x] CHK037 ¿El spec exige que el estado deshabilitado/con-spinner del botón esté vinculado únicamente a una operación en curso real y se restablezca en TODO desenlace (éxito o error), de modo que un botón gris con spinner sin operación subyacente sea un defecto contemplado? [Completeness, Spec §FR-003 / FR-004]
- [x] CHK038 ¿La especificación distingue exigiblemente entre "backend no responde" (petición sin respuesta) y "backend responde con error", y exige un desenlace conocido del estado de carga en ambos casos, sin depender de un timeout artificial? [Clarity, Spec §FR-009 / FR-002]
- [x] CHK039 ¿El alcance del diagnóstico exige cubrir las clases de fallo de la petición señaladas por la evidencia (sin respuesta del servidor, error de conexión, tipo CORS, servidor caído, excepción no capturada) y determinar cuál de ellas bloquea el desenlace? [Completeness, Spec §Contexto / FR-001]
- [x] CHK040 ¿Se especifica que tras un desenlace fallido el usuario puede reintentar el login con los campos ya diligenciados, sin estado de carga heredado ni peticiones concurrentes? [Coverage, Spec §Edge Cases]
- [x] CHK041 ¿Los criterios de éxito (SC-001/SC-003) definen como evidencia de aceptación el aspecto observable del botón (habilitado / carga finalizada / mensaje o redirección) y no solo atributos internos de estado? [Measurability, Spec §SC-001 / SC-003]

## Performance & Fiabilidad *(anexo /speckit.checklist — PR gate)*

- [x] CHK042 ¿Los requisitos definen un límite de recurso explícito (conexión, `statement_timeout`, deadline de operación) para CADA dependencia del trayecto login (BD, backend, red), y no una única métrica global? [Completeness, Spec §FR-009 / data-model.md §Configuración]
- [x] CHK043 ¿Las métricas de tiempo (SC-002: 5 s/10 s; SC-005: 2 s) especifican las condiciones nominales de medición (datos, entorno, sin competencia de recursos) para ser reproducibles en ambos entornos? [Clarity, Spec §SC-002 / Assumptions]
- [x] CHK044 ¿Queda verificable en requisitos que el desenlace por límite de recurso es un error REAL y visible (nunca un temporizador de interfaz que finja éxito), con criterio de aceptación explícito? [Clarity, Spec §FR-009 / SC-006]
- [x] CHK045 ¿Los umbrales de recurso (`DB_CONNECT_TIMEOUT` 10 s, `DB_STATEMENT_TIMEOUT` 5000 ms, `LOGIN_OPERATION_DEADLINE_SECONDS` 12 s) están documentados como configuración y referenciados desde el spec/plan, sin números mágicos? [Completeness, data-model.md §Configuración]
- [x] CHK046 ¿SC-006 define el método para observar que el desenlace proviene del resultado real de la operación (traza de logs correlacionada con el estado del botón) y no de un temporizador? [Measurability, Spec §SC-006 / SC-003]
- [x] CHK047 ¿Se especifica si la carga del panel queda dentro o fuera de la métrica SC-002, de forma consistente con las Assumptions? [Consistency, Spec §SC-002 / Assumptions]
- [x] CHK048 ¿El spec define con criterio medible qué es "cuelgue" (operación pendiente sin desenlace) frente a "degradación aceptable" (trayecto mayor que el nominal pero terminal)? [Clarity, Spec §SC-002 / FR-009]
- [x] CHK049 ¿Los reintentos tras fallo están acotados por requisito y se prohíben reintentos infinitos automáticos, sin depender del límite de recurso para ocultar un bug? [Coverage, Spec §FR-009 / Edge Cases]
- [x] CHK050 ¿Los límites de recurso cubren las consultas internas del trayecto (migración de hash SHA256→Bcrypt y escritura de último acceso) y no solo la autenticación principal? [Coverage, Spec §Contexto / Edge Cases]
- [x] CHK051 ¿Se define cómo se induce y cómo se verifica cada escenario simulado de SC-006 (indisponibilidad de BD/backend/red) con evidencia reproducible antes/después? [Measurability, Spec §US3 / Assumptions]
- [x] CHK052 ¿Los valores de límite de recurso y las métricas SC-002/SC-006 son mutuamente consistentes (no contradictorios) entre spec y plan (p. ej. `statement_timeout` 5000 ms y deadline 12 s frente a un máximo desplegado de 10 s)? [Consistency, data-model.md §Configuración / Spec §SC-002]

## Notes

- Checklist generado desde `spec.md` (no existe aún plan.md/tasks.md; cuando existan, se recomienda re-ejecutar para cubrir decisiones técnicas del plan).
- Los ítems marcados [Gap] señalan aspectos de requisitos ausentes o insuficientes que deben resolverse antes de o durante `/speckit.plan`.
- ≥80 % de los ítems incluyen referencia de trazabilidad al spec.
- Anexo tras evidencia del usuario: sección "Evidencia Visual" (CHK037–CHK041) derivada del estado observado (botón deshabilitado con spinner tras enviar credenciales).