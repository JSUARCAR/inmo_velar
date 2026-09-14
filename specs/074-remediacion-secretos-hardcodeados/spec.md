# Feature Specification: Remediación de Credenciales Hardcodeadas y Datos Sensibles Expuestos

**Feature Branch**: `074-remediacion-secretos-hardcodeados`

**Created**: 2026-09-14

**Status**: Draft

**Input**: User description: "Auditoría de seguridad `AUDIT_SECRETS_CREDENCIALES_HARDCODEADAS.md` (2026-09-08, commit auditado d20f78d2): remediar credenciales hardcodeadas (cuenta administradora, contraseña de base de datos de producción y cuenta de prueba), documentación que publica esos valores en texto plano, información personal real versionada en `assets/` y detección insuficiente del escáner automático de secretos. La remediación previa (`specs/066-security-hardening-remediation/`) corrigió un solo archivo; el resto del inventario sigue vigente."

## Clarifications

### Session 2026-09-14

- Q: ¿Qué debe hacer la integración continua si el escaneo de secretos no puede ejecutarse? → A: Bloquear (fail-closed): la fusión queda bloqueada hasta completar el escaneo exitosamente.
- Q: ¿Dónde debe residir el inventario enmascarado y la evidencia de la remediación? → A: Documento enmascarado en el repositorio, versionado como fuente de verificación (sin valores reales).
- Q: ¿Cómo se detectan los valores exactos comprometidos sin violar la prohibición de versionarlos? → A: Reglas de patrón generalizadas versionadas + lista de valores exactos en configuración protegida de CI, inyectada en tiempo de ejecución y nunca versionada.
- Q: ¿El barrido incluye documentación externa al repositorio? → A: Sí, además del repositorio y su historial se incluyen los canales externos conocidos (wiki, runbooks, correos, tickets), registrando su limpieza como evidencia.
- Q: ¿Cómo debe hacerse efectivo el bloqueo del escaneo para impedir fusiones con secretos? → A: Verificación requerida en la protección de la rama principal: ninguna fusión sin escaneo exitoso; los fallos e indisponibilidades quedan registrados como evidencia.
- Q: ¿Cómo se asignan los responsables de verificaciones e inventario? → A: Responsable de seguridad único designado (inventario con identificador único por hallazgo, lista protegida y excepciones, evidencia); operaciones ejecuta rotación y purga.
- Q: ¿Qué mecanismos cuentan como configuración externa al control de versiones? → A: Variables de entorno y/o gestor de secretos; prohibido cualquier archivo versionado con valores reales.
- Q: ¿Cómo se resuelven los falsos positivos del escáner sin debilitar la detección? → A: Lista de permitidos acotada en la configuración protegida, revisada y justificada por el responsable de seguridad; nunca aplica a los valores comprometidos.
- Q: ¿Cómo se establece la trazabilidad entre historias, requisitos y criterios de éxito? → A: Identificadores US-01…US-05 en los títulos de historia, referenciables desde el plan y las tareas; sin matriz adicional.

## User Scenarios & Testing *(mandatory)*

### User Story 1 (US-01) - Revocación y rotación de las credenciales expuestas (Priority: P1)

Como responsable de seguridad del sistema, quiero que todas las credenciales expuestas en el repositorio (cuenta administradora, contraseña de la base de datos de producción y cuenta de prueba) sean invalidadas y reemplazadas por valores nuevos que solo existan en configuración segura, para que la exposición histórica deje de otorgar acceso a producción.

**Why this priority**: El repositorio es accesible a terceros y contiene la credencial de administrador junto con la URL real de producción, además de la contraseña de la base de datos. Cualquier persona con acceso de lectura tiene acceso administrativo potencial hoy mismo; la rotación es la única medida que neutraliza ese acceso de inmediato. Sin rotación, cualquier otra acción deja el riesgo activo.

**Independent Test**: Intentar autenticarse con los valores comprometidos debe fallar en todos los entornos, mientras que la aplicación y los scripts autorizados deben seguir operando con los nuevos valores inyectados desde configuración externa.

**Acceptance Scenarios**:

1. **Given** que la credencial de administrador estuvo publicada en archivos versionados, **When** se intenta autenticar con el valor comprometido contra el entorno de producción, **Then** la autenticación es rechazada.
2. **Given** que la contraseña de la base de datos de producción fue expuesta, **When** se intenta abrir una conexión con el valor comprometido, **Then** la conexión es rechazada y la aplicación continúa operativa con la nueva credencial.
3. **Given** que la cuenta de prueba pudo tener privilegios reales, **When** se usa su credencial comprometida, **Then** el acceso es rechazado o la cuenta fue eliminada.
4. **Given** los nuevos valores rotados, **When** la aplicación y los scripts autorizados se ejecutan con la configuración externa actualizada, **Then** los flujos críticos (inicio de sesión administrativo, generación de PDF, liquidaciones) funcionan sin interrupción.

---

### User Story 2 (US-02) - Eliminación de credenciales hardcodeadas del código y la documentación (Priority: P1)

Como desarrollador del proyecto, quiero que ningún archivo versionado contenga credenciales en texto plano ni valores por defecto inseguros, para que leer el repositorio no permita acceder a ningún sistema.

**Why this priority**: Aunque se roten las credenciales, mientras el patrón siga presente en decenas de archivos y documentos la reincidencia es inevitable; además, los mismos valores siguen siendo publicados como referencia en documentación operativa. Es la corrección de raíz del hallazgo.

**Independent Test**: Una búsqueda estática de los valores comprometidos en todos los archivos versionados devuelve cero resultados; cualquier componente que requiera credenciales falla con un mensaje accionable cuando la configuración externa no está presente.

**Acceptance Scenarios**:

1. **Given** los más de 30 archivos con la contraseña de base de datos como valor por defecto, **When** se busca el literal en el árbol de trabajo versionado, **Then** hay cero coincidencias.
2. **Given** un script que hoy asume un valor por defecto, **When** se ejecuta sin la configuración externa requerida, **Then** termina con un error explícito que indica qué variable falta y cómo configurarla, sin asumir ningún valor.
3. **Given** los documentos y guías que publican credenciales en texto plano, **When** se revisa su contenido, **Then** no contienen contraseñas ni cadenas de conexión con credenciales reales.
4. **Given** scripts de diagnóstico que combinan una URL real de producción con usuario y contraseña, **When** se audita el árbol de trabajo, **Then** ninguno contiene credenciales embebidas (se exigen por configuración externa) o fueron retirados del repositorio.
5. **Given** el propio informe de auditoría, que enumera los literales, **When** se decide versionarlo, **Then** sus valores están enmascarados previamente o el archivo permanece fuera del control de versiones.

---

### User Story 3 (US-03) - Purga del historial de versiones (Priority: P2)

Como responsable de seguridad del sistema, quiero que los secretos y las rutas con datos personales desaparezcan del historial completo del control de versiones, para que un clon nuevo o un commit antiguo no exponga información que todavía pueda ser explotada.

**Why this priority**: Eliminar los valores solo del árbol de trabajo deja el historial intacto desde el 2026-05-25; cualquiera puede recuperarlos de commits antiguos. La purga es indispensable para cerrar el vector, pero es una operación destructiva que exige coordinación del equipo, por eso se ejecuta después de detener la exposición actual.

**Independent Test**: Un clon nuevo del repositorio no contiene los valores comprometidos ni archivos con información personal en ningún commit accesible; la búsqueda sobre todo el historial devuelve cero coincidencias.

**Acceptance Scenarios**:

1. **Given** que el historial contiene los valores comprometidos desde el 2026-05-25, **When** se inspecciona el historial completo de un clon nuevo, **Then** no aparecen en ningún commit, rama ni etiqueta.
2. **Given** las rutas con información personal versionada, **When** se clona el repositorio, **Then** ningún commit contiene las exportaciones ni los documentos con datos reales.
3. **Given** colaboradores con clones antiguos y ramas abiertas, **When** se reescribe el historial, **Then** existe una ventana de coordinación: hubo notificación previa, las ramas activas se reconciliaron o descartaron con confirmación de sus autores, y no hay pérdida silenciosa de trabajo.
4. **Given** la base de datos local que estuvo versionada (hoy vacía), **When** se revisan las versiones anteriores del archivo, **Then** ninguna conserva datos personales.

---

### User Story 4 (US-04) - Prevención de reincidencia mediante detección automatizada (Priority: P2)

Como responsable de calidad del repositorio, quiero que la verificación automática de seguridad detecte estos patrones en cada cambio, para que las credenciales no puedan volver a introducirse después de la remediación.

**Why this priority**: El escáner configurado actualmente no detectó ninguno de los hallazgos porque solo busca formatos conocidos o de alta entropía, y estos secretos son literales cortos de baja entropía. Sin reglas específicas, la remediación se degrada con el tiempo y el problema reaparece.

**Independent Test**: Introducir en una rama de prueba un cambio con un valor señuelo del mismo formato; el escaneo debe detectarlo y bloquear la verificación. Un cambio limpio debe pasar sin falsos positivos.

**Acceptance Scenarios**:

1. **Given** las reglas de detección actualizadas, **When** un cambio introduce un literal de credencial en cualquier archivo versionado (código, documentación o prueba), **Then** el escaneo lo detecta y la verificación falla.
2. **Given** un cambio que solo usa valores señuelo sintéticos o marcadores de posición, **When** pasa el escaneo, **Then** la verificación concluye exitosamente sin falsos positivos.
3. **Given** el flujo de integración continua, **When** se hace push o se abre un PR hacia las ramas principales, **Then** el escaneo se ejecuta de forma obligatoria.

---

### User Story 5 (US-05) - Higiene de datos personales versionados (Priority: P3)

Como responsable de protección de datos, quiero que los archivos con información personal real (exportaciones de personas, contratos, estados de cuenta y liquidaciones) dejen de estar versionados y queden accesibles solo en almacenamiento controlado, para no seguir publicando datos de terceros.

**Why this priority**: No son credenciales, pero es una fuga de datos personales y financieros de clientes reales que puede generar obligaciones legales y daño reputacional; sin embargo, no otorga acceso a los sistemas, por lo que es menos urgente que los hallazgos anteriores.

**Independent Test**: El árbol de trabajo y el historial no contienen archivos con información personal real; las pruebas que necesiten esos datos usan datos sintéticos o anonimizados.

**Acceptance Scenarios**:

1. **Given** las exportaciones de personas con datos reales, **When** se revisa el árbol y el historial, **Then** no están presentes en ninguna versión del repositorio.
2. **Given** los documentos con contratos, estados de cuenta y liquidaciones reales, **When** se clona el repositorio, **Then** no se descargan datos personales.
3. **Given** una necesidad operativa o de pruebas de esos archivos, **When** se generan los datos de prueba, **Then** los datos son sintéticos o anonimizados y residen fuera del control de versiones.
4. **Given** las nuevas reglas de exclusión, **When** aparece un archivo nuevo en las carpetas sensibles, **Then** el control de versiones no lo rastrea por defecto.

---

### Edge Cases

- **Configuración ausente en desarrollo**: un script que antes funcionaba con el valor por defecto ahora debe fallar con un mensaje que indique la variable faltante y cómo configurarla; nunca debe continuar con un valor supuesto.
- **Clones antiguos del equipo**: los colaboradores conservan el historial anterior a la reescritura; deben ser identificados y obligados a re-clonar, sabiendo que mientras tanto la mitigación real es la rotación de credenciales.
- **Ramas y PRs abiertas durante la reescritura**: quedan invalidadas; deben inventariarse y reconciliarse o descartarse con confirmación de sus autores antes de la purga.
- **Rotación sin cortar el servicio**: la sustitución de credenciales en producción debe actualizar todos los consumidores (aplicación, automatizaciones, entornos locales y respaldos) para que no haya interrupciones atribuibles al cambio.
- **Cuenta de prueba sintética**: si se confirma que la cuenta de prueba no tiene privilegios reales, se documenta la verificación y se eliminan igualmente sus referencias.
- **Datos que deben conservarse**: eliminar los archivos con información personal del repositorio no implica destruirlos; si son necesarios para operación, se trasladan a almacenamiento controlado fuera del control de versiones.
- **Falsos positivos del escáner**: se resuelven mediante entradas específicas en la lista de permitidos de la configuración protegida, justificadas, revisadas por el responsable de seguridad y con revisión periódica; los valores de prueba deben ser señuelos claramente sintéticos o marcadores de posición, y la excepción nunca aplica a los valores comprometidos.
- **El propio informe de auditoría contiene los literales**: si se versiona, sus valores deben enmascararse antes de incorporarlo, o mantenerse fuera del control de versiones.
- **Indisponibilidad del escaneo**: si el escaneo no puede ejecutarse, la integración permanece bloqueada hasta completarlo exitosamente; no se admite continuar sin verificación ni excepciones por urgencia.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST invalidar (rotar o eliminar) el 100% de las credenciales identificadas como expuestas: cuenta administradora, cuenta de base de datos de producción y cuenta de prueba.
- **FR-002**: Las credenciales nuevas MUST residir únicamente en configuración externa al control de versiones (variables de entorno y/o gestor de secretos) y MUST NOT tener valores por defecto definidos en el código.
- **FR-003**: Ningún archivo versionado (código, scripts, pruebas, documentación o informes) MAY contener los valores comprometidos, cadenas de conexión con credenciales, ni pares usuario/contraseña en texto plano.
- **FR-004**: Todo componente que consuma credenciales MUST fallar de forma inmediata y explícita cuando la configuración externa no esté presente, indicando la variable faltante y sin exponer valores ni continuar con supuestos.
- **FR-005**: Las pruebas automatizadas y los scripts de diagnóstico que apunten a entornos reales MUST obtener las credenciales exclusivamente de configuración externa; MUST NOT contener usuarios, contraseñas ni URLs de producción combinadas con credenciales embebidas.
- **FR-006**: La documentación operativa MUST describir el uso de la configuración externa sin reimprimir valores reales; puede referenciar nombres de variables y ejemplos enmascarados.
- **FR-007**: El historial completo del control de versiones MUST ser purgado de los valores comprometidos, de modo que un clon nuevo no los contenga en ningún commit, rama ni etiqueta.
- **FR-008**: El historial completo MUST ser purgado de los archivos con información personal real (exportaciones de personas, contratos, estados de cuenta, liquidaciones y la base de datos local si conservó datos en versiones previas).
- **FR-009**: La reescritura del historial MUST ejecutarse en una ventana coordinada: notificación previa a los colaboradores, inventario de ramas activas reconciliadas o descartadas con confirmación, y guía de re-clonado entregada.
- **FR-010**: Los archivos con información personal real MUST dejar de estar versionados; si se requieren para operación, MUST conservarse en almacenamiento controlado fuera del repositorio.
- **FR-011**: Las reglas de exclusión del control de versiones MUST cubrir las rutas de datos sensibles (`assets/exports/`, `assets/pdfs/` y equivalentes futuras) y los archivos de base de datos locales.
- **FR-012**: Las pruebas y los datos de ejemplo MUST usar datos sintéticos o anonimizados; MUST NOT incorporarse datos personales reales de clientes.
- **FR-013**: El escaneo automático de seguridad MUST incorporar reglas que detecten tanto los valores comprometidos como los patrones de riesgo asociados (valores por defecto inseguros al leer configuración y pares usuario/contraseña literales) en cada push y PR a las ramas principales. Las reglas de patrón generalizadas MUST estar versionadas; la lista de valores exactos comprometidos MUST residir en configuración protegida de integración continua (fuera del control de versiones) y MUST inyectarse en tiempo de ejecución.
- **FR-014**: El escaneo MUST bloquear la integración cuando detecte un secreto y MUST estar configurado como verificación requerida en la protección de la rama principal, de modo que ninguna fusión ocurra sin un escaneo exitoso; MUST NOT existir ninguna excepción para los valores comprometidos.
- **FR-015**: MUST revisarse los registros de acceso de las cuentas y servicios afectados desde la primera fecha de exposición conocida (2026-05-25), y documentarse si existió uso no autorizado junto con las acciones tomadas.
- **FR-016**: MUST producirse evidencia verificable de la remediación: fecha de cada rotación, resultado de búsquedas en árbol e historial (en cero), resultado del escaneo posterior y confirmación de re-clonado de los colaboradores. El inventario enmascarado de hallazgos y la evidencia MUST residir en un documento versionado del repositorio, sin reimprimir valores reales.
- **FR-017**: La iniciativa previa de endurecimiento (`specs/066-security-hardening-remediation/`) MUST cerrarse formalmente solo cuando el inventario completo de la auditoría esté en cero; hasta entonces, ambas iniciativas MUST considerarse una sola unidad de riesgo.
- **FR-018**: Los scripts de diagnóstico o auditoría que no sean necesarios en el repositorio MUST eliminarse o moverse fuera de él; los que se conserven MUST cumplir con FR-005.
- **FR-019**: Si el escaneo automático no puede ejecutarse (indisponibilidad del servicio, error del ejecutor o de configuración), la integración MUST permanecer bloqueada hasta completar el escaneo exitosamente; MUST NOT permitirse continuar sin verificación. Cada fallo o indisponibilidad MUST registrarse como evidencia con su causa.
- **FR-020**: El barrido de credenciales MUST incluir, además del repositorio y su historial, los canales externos conocidos donde los valores puedan estar replicados (wiki, runbooks, correos y tickets); la limpieza de cada canal MUST registrarse como evidencia.
- **FR-021**: MUST existir un responsable de seguridad único designado que mantenga el inventario enmascarado con un identificador único por hallazgo, administre la lista protegida de valores y las excepciones del escáner, y valide la evidencia de la remediación.

### Key Entities *(include if feature involves data)*

- **Credencial expuesta**: valor comprometido identificado por un identificador único de hallazgo (nunca reimpreso en documentos nuevos), tipo (cuenta de aplicación, base de datos o cuenta de prueba), sistemas afectados, estado de remediación (pendiente, rotada o eliminada) y fecha de rotación.
- **Ubicación de exposición**: archivo, línea y categoría (código en ejecución, script de diagnóstico, prueba, documentación, informe, historial o canal externo conocido), usada para medir el avance del inventario hacia cero.
- **Cuenta afectada**: identificador lógico de la cuenta o servicio cuya credencial se rota, con su responsable y nivel de privilegios.
- **Dato personal versionado**: ruta del archivo o artefacto con información personal, tipo de dato (identificación, contacto, financiero o contractual), versión y destino de conservación si aplica.
- **Evidencia de verificación**: registro en un documento enmascarado y versionado del repositorio, con fecha y responsable de las rotaciones, los resultados de búsquedas y escaneos, y las confirmaciones del equipo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cero ocurrencias de los valores comprometidos en el árbol de trabajo versionado (código, documentación y pruebas) al cierre de la remediación.
- **SC-002**: Cero ocurrencias de los valores comprometidos en el historial completo; un clon nuevo no los contiene en ningún commit, rama ni etiqueta.
- **SC-003**: El 100% de las credenciales expuestas (tres conjuntos) queda invalidado en un máximo de 72 horas desde la aprobación de esta especificación, priorizando la cuenta administradora dentro de las primeras 24 horas.
- **SC-004**: Cero interrupciones del servicio en producción atribuibles a la rotación, verificando continuidad en inicio de sesión, generación de documentos y liquidaciones.
- **SC-005**: El escaneo automático detecta el 100% de los patrones comprometidos en una prueba controlada de reintroducción y bloquea la verificación.
- **SC-006**: Cero archivos con información personal real en el árbol y en el historial; el 100% de los datos usados en pruebas es sintético o anonimizado.
- **SC-007**: El 100% de los colaboradores tiene su clon actualizado en un máximo de 5 días hábiles tras la reescritura, con confirmación registrada.
- **SC-008**: La verificación final queda documentada: búsquedas en árbol e historial en cero, escaneo sin hallazgos y ausencia de excepciones para los valores comprometidos.
- **SC-009**: La revisión de los registros de acceso desde el 2026-05-25 queda completada y documentada, con o sin hallazgos de uso no autorizado.
- **SC-010**: El 100% de las indisponibilidades o fallos del escaneo resulta en bloqueo de la integración hasta su resolución, sin excepciones.
- **SC-011**: Cero copias de los valores comprometidos en los canales externos conocidos revisados, con la limpieza de cada canal registrada como evidencia.

## Assumptions

- El informe de auditoría del 2026-09-08 (commit auditado `d20f78d2`) es el inventario de referencia; sus apéndices definen el alcance cuantitativo de "cero ocurrencias" (más de 30 archivos con la contraseña de base de datos, 10 con la credencial de administrador, alrededor de una docena con la de prueba, 5 documentos en texto plano y 18 archivos con información personal).
- El repositorio se considera accesible a terceros: todos los valores listados se tratan como comprometidos, aunque no se haya evidenciado uso malicioso.
- La rotación de credenciales la ejecutan los administradores con acceso a la plataforma de producción y a la base de datos; no forma parte de la implementación de código de esta iniciativa, que la prepara, exige y verifica.
- La cuenta de prueba se trata como cuenta real hasta que se confirme lo contrario, por lo que su credencial también se rota.
- La reescritura del historial está autorizada por el propietario del repositorio y se coordina con todos los colaboradores; se asume un equipo pequeño y controlado.
- Eliminar la información personal del repositorio no implica destruirla: se asume la existencia (o creación) de almacenamiento controlado fuera del control de versiones para los respaldos operativos que se necesiten.
- Los valores usados en pruebas y documentación serán siempre señuelos sintéticos o marcadores de posición; no se requieren excepciones al escáner para los valores comprometidos.
- El informe de auditoría no está versionado actualmente; si se incorpora al repositorio, sus valores deberán enmascararse antes.
- Existe acceso a los registros de acceso de producción para la investigación desde el 2026-05-25; si no estuvieran disponibles, la limitación se documentará como evidencia.
- Quedan fuera de alcance los ejes cubiertos por auditorías separadas: inyección SQL, XSS, control de acceso y lógica de negocio.
- La plataforma de integración continua permite almacenar la lista de valores exactos como configuración protegida e inyectarla al ejecutar el escaneo.
- Existe acceso administrativo a la configuración del escáner y a la protección de la rama principal para exigir la verificación requerida.
