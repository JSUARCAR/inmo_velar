# PROPUESTA COMERCIAL

---

## PORTADA

**Propuesta Comercial**

**Proyecto:** Plataforma de Gestión Inmobiliaria - Módulos Adicionales

**Cliente:** Inmobiliaria Velar SAS

**Fecha:** _______________

**Versión:** 1.4

---

## 1. RESUMEN EJECUTIVO

Inmobiliaria Velar SAS requiere el desarrollo de nuevas funcionalidades y mejoras sobre la plataforma existente de gestión inmobiliaria. El proyecto abarca desde correcciones en módulos actuales hasta la implementación de nuevos módulos que fortalecerán la operación del negocio, incluyendo notificaciones por WhatsApp, generación de documentos PDF, control de seguros y un módulo centralizado de consulta de propiedades.

La propuesta incluye **14 módulos funcionales** con un total de **24 requerimientos** clasificados como ARREGLO (mejoras a funcionalidades existentes) y NUEVO (nuevas funcionalidades).

**Tarifas:**
- Desarrollo general: $2,500 COP/hora
- Integración WhatsApp: $3,000 COP/hora

---

## 2. ALCANCE

### 2.1 Módulos con ARREGLOS (Mejoras a Funcionalidades Existentes)

Nuestro equipo realizará ajustes estratégicos en los módulos actualmente operativos, garantizando una experiencia más fluida, precisa y funcional para los usuarios finales. Cada mejora está diseñada para resolver puntos específicos que impactan directamente la productividad y satisfacción del usuario.

| Módulo | Descripción Detallada |
|--------|----------------------|
| **Dashboard** | Revisaremos y optimizaremos el botón **RESOLVER**, verificando que cada acción ejecutada genere el flujo de trabajo esperado. Además, analizaremos el comportamiento completo del sistema para identificar y corregir cualquier desviación que pueda afectar la toma de decisiones en tiempo real. |
| **Personas** | Implementaremos un sistema de **sincronización automática** que garantice que cuando se actualice cualquier dato de una persona (nombre, teléfono, email, dirección), todos los módulos asociados (contratos de mandato, liquidaciones, incidentes, recaudos) reflejen los cambios instantáneamente. Esto elimina inconsistencias y reduce errores operativos. |
| **Contratos** | Eliminaremos el tooltip innecesario en la columna **FECHA DE PAGO** de los contratos de arrendamiento, ya que esta información solo aplica para contratos de mandato. Esta corrección mejora la claridad visual y evita confusión entre diferentes tipos de contratos. |
| **Propiedad Horizontal** | En el panel de Asambleas, habilitaremos el botón **"No sé"** exclusivamente cuando existan listas en blanco y el botón sea visible, facilitando la gestión de asistencia. Además, en el modal de nueva asistencia, el selector de propiedad mostrará la **dirección completa** en lugar del ID, permitiendo una selección más intuitiva y sin errores. En el panel de pagos administrativos, agregaremos el botón para registrar pagos y validaremos la columna **Link** para asegurar la integridad de la información. |
| **Liquidaciones Propietario** | Configuraremos el filtro de ciclo para permitir **únicamente la eliminación de los últimos 5 ciclos**, protegiendo la integridad histórica de los datos. Asimismo, habilitaremos la funcionalidad de **carga de anexos** (imágenes, PDFs, documentos adjuntos) para que los propietarios puedan respaldar sus gestiones con documentación de soporte. |
| **Recaudos Arrendatario** | Agregaremos una columna que mostrará el **codeudor asociado** a cada contrato de arrendamiento, proporcionando información clave para la gestión de cobros y seguimiento de pagos. |
| **Desocupaciones** | Permitiremos el registro completo de una terminación de contrato con **fecha de solicitud de retiro** y **fecha de entrega del inmueble**. El sistema ejecutará automáticamente la finalización del contrato, eliminará la liquidación y el recaudo del período correspondiente, y permitirá cargar anexos que documenten el estado del inmueble al momento de la entrega. |
| **Incidentes** | Mejoraremos significativamente la **paginación** para mostrar todos los incidentes de manera fluida, optimizando la vista de la tabla con carga progresiva y filtros avanzados que permitan encontrar información específica en segundos. |
| **Usuarios** | Implementaremos un proceso de eliminación de usuarios con **mensaje de confirmación** que muestre claramente las consecuencias de la acción, incluyendo un resumen de los datos que serán eliminados y una opción de deshacer antes de confirmar. |
| **Reportes** | Realizaremos una validación exhaustiva de todos los reportes del sistema, asegurando que la información visualizada coincida exactamente con los datos almacenados en la base de datos. Verificaremos que la exportación a diferentes formatos (PDF, Excel, CSV) mantenga la integridad y el formato original de la información. |

### 2.2 Módulos NUEVOS (Nuevas Funcionalidades)

Desarrollaremos desde cero funcionalidades que transformarán la forma en que Inmobiliaria Velar SAS gestiona sus operaciones, incorporando tecnologías modernas y automatizaciones que generarán un impacto positivo inmediato en la productividad y satisfacción de clientes.

| Módulo | Descripción Detallada |
|--------|----------------------|
| **Contratos** | Crearemos un sistema completo para la **generación automática de actas de entrega**, permitiendo definir si se requiere un PDF con plantilla personalizada o un formulario interactivo con generación de PDF en tiempo real. Además, implementaremos **notificaciones por WhatsApp** para informar a propietarios, arrendatarios, habitantes y codeudores sobre novedades críticas del contrato: nuevo contrato de mandato, nuevo contrato de arrendamiento, renovación y incremento de IPC. Cada notificación incluirá un mensaje profesional con los detalles relevantes y un enlace al documento correspondiente. |
| **Propiedad Horizontal** | Asociaremos el valor de la **cuota de administración y extraordinaria** directamente a la liquidación del propietario, permitiendo que estos valores se **descuenten automáticamente** al momento de generar el estado de cuenta. Esto elimina cálculos manuales, reduce errores y agiliza el proceso de conciliación financiera. |
| **Liquidaciones Propietario** | Implementaremos un sistema de **notificación por WhatsApp** que enviará al propietario el **Estado de Cuenta en formato PDF** cuando se genere y envíe desde el sistema. El mensaje incluirá un resumen ejecutivo del período, el detalle de ingresos y deducciones, y el saldo a favor o en contra. |
| **Recaudos Arrendatario** | Crearemos un sistema de **confirmación automática por WhatsApp** que enviará a cada arrendatario un comprobante de recibido del canon de arrendamiento, incluyendo el monto, la fecha de pago, el período cubierto y cualquier saldo pendiente. Esto genera tranquilidad y transparencia en la relación arrendador-arrendatario. |
| **Incidentes** | Desarrollaremos un sistema de **notificación por WhatsApp** para informar al propietario sobre incidentes reportados en su propiedad, incluyendo el envío del **PDF detallado** con la descripción del problema, las acciones tomadas, el estado actual y los pasos a seguir. Esto garantiza comunicación inmediata y documentada. |
| **Seguros** | Crearemos un módulo completo para el **control integral de seguros de arrendatarios**, incluyendo: fecha de ingreso del seguro, tipo de póliza, monto cubierto, fecha de vencimiento, y un **sistema de recordatorios automáticos** un mes antes del vencimiento. El módulo permitirá gestionar pólizas activas, vencidas y pendientes de renovación, con reportes y alertas proactivas. |
| **Recibos Públicos** | Implementaremos un algoritmo que **calcula automáticamente** qué porcentaje del recibo de servicios públicos (agua, luz, gas) corresponde al propietario y cuál al arrendatario, basándose en criterios configurables (porcentaje de área, días de ocupación, acuerdo contractual). Esto elimina disputas y agiliza la distribución de costos. |
| **Documentos** | Crearemos un módulo para **generar documentos PDF profesionales mediante plantillas personalizadas** para propietarios y arrendatarios. Incluiremos plantillas predefinidas como: autorización de mudanza por ingreso y salida, cartas de aviso, constancias de residencia, y permitiremos crear nuevas plantillas con un editor visual intuitivo. |
| **VELAR** | Desarrollaremos un **módulo centralizado de consulta de propiedades** que permitirá buscar por cualquier criterio (dirección, propietario, arrendatario, estado) y mostrar de manera integral: propietario activo, arrendatario activo, historial completo de arrendatarios, codeudores, estado de diferentes módulos (activo, información del contrato de mandato, contrato de arrendamiento, detalle del historial de liquidaciones de propietario, historial de recaudos de arrendatario, historial de desocupaciones, historial de incidentes, historial de recibos públicos, etc.). Este módulo será la **ventana única** que centraliza toda la información de la propiedad, eliminando la necesidad de navegar entre múltiples pantallas. |

---

## 3. METODOLOGÍA

El proyecto será ejecutado bajo metodología **SCRUM**, con ciclos de desarrollo de 2 semanas:

- **Product Backlog:** Priorización de requerimientos según valor de negocio
- **Sprint Planning:** Planificación de funcionalidades por sprint
- **Sprint Review:** Entrega y demostración de funcionalidades completadas
- **Sprint Retrospective:** Mejora continua del proceso
- **Entregas Incrementales:** Funcionalidades entregadas progresivamente

---

## 4. ESTIMACIÓN POR MÓDULO

### 4.1 Dashboard

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Dashboard | ARREGLO | Revisión botón RESOLVER | 8 | $2,500 | $0 |
| Dashboard | ARREGLO | Análisis de flujo de trabajo | 6 | $2,500 | $0 |
| Dashboard | ARREGLO | Desarrollo Backend | 12 | $2,500 | $0 |
| Dashboard | ARREGLO | Desarrollo Frontend | 10 | $2,500 | $0 |
| Dashboard | ARREGLO | Pruebas funcionales | 6 | $2,500 | $0 |
| Dashboard | ARREGLO | Documentación | 4 | $2,500 | $0 |
| **Subtotal Dashboard** | | | **46** | | **$0** |

### 4.2 Personas

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Personas | ARREGLO | Análisis de sincronización | 8 | $2,500 | $0 |
| Personas | ARREGLO | Diseño de flujo | 6 | $2,500 | $0 |
| Personas | ARREGLO | Desarrollo Backend | 16 | $2,500 | $0 |
| Personas | ARREGLO | Desarrollo Frontend | 8 | $2,500 | $0 |
| Personas | ARREGLO | Pruebas de integración | 8 | $2,500 | $0 |
| Personas | ARREGLO | Documentación | 4 | $2,500 | $0 |
| **Subtotal Personas** | | | **50** | | **$0** |

### 4.3 Contratos

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Contratos | ARREGLO | Eliminación tooltip | 4 | $2,500 | $0 |
| Contratos | ARREGLO | Desarrollo Frontend | 6 | $2,500 | $0 |
| Contratos | ARREGLO | Pruebas | 4 | $2,500 | $0 |
| Contratos | NUEVO | Análisis acta de entrega | 12 | $2,500 | $30,000 |
| Contratos | NUEVO | Diseño UI/UX | 16 | $2,500 | $40,000 |
| Contratos | NUEVO | Desarrollo Backend | 32 | $2,500 | $80,000 |
| Contratos | NUEVO | Desarrollo Frontend | 24 | $2,500 | $60,000 |
| Contratos | NUEVO | Integración API | 16 | $2,500 | $40,000 |
| Contratos | NUEVO | Pruebas | 12 | $2,500 | $30,000 |
| Contratos | NUEVO | Documentación | 8 | $2,500 | $20,000 |
| Contratos | NUEVO | Notificaciones WhatsApp | 40 | $3,000 | $120,000 |
| Contratos | NUEVO | Integración WhatsApp API | 24 | $3,000 | $72,000 |
| Contratos | NUEVO | Pruebas WhatsApp | 16 | $3,000 | $48,000 |
| Contratos | NUEVO | Documentación WhatsApp | 8 | $3,000 | $24,000 |
| **Subtotal Contratos** | | | **226** | | **$564,000** |

### 4.4 Propiedad Horizontal

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| PH | ARREGLO | Botón "No sé" asambleas | 8 | $2,500 | $0 |
| PH | ARREGLO | Selector de propiedad | 6 | $2,500 | $0 |
| PH | ARREGLO | Desarrollo Frontend | 10 | $2,500 | $0 |
| PH | ARREGLO | Botón pagos administrativos | 8 | $2,500 | $0 |
| PH | ARREGLO | Validación columna Link | 6 | $2,500 | $0 |
| PH | ARREGLO | Pruebas | 8 | $2,500 | $0 |
| PH | NUEVO | Análisis cuotas a liquidación | 12 | $2,500 | $30,000 |
| PH | NUEVO | Diseño de esquema | 8 | $2,500 | $20,000 |
| PH | NUEVO | Desarrollo Backend | 24 | $2,500 | $60,000 |
| PH | NUEVO | Desarrollo Frontend | 16 | $2,500 | $40,000 |
| PH | NUEVO | Pruebas | 12 | $2,500 | $30,000 |
| PH | NUEVO | Documentación | 8 | $2,500 | $20,000 |
| **Subtotal PH** | | | **126** | | **$200,000** |

### 4.5 Liquidaciones Propietario

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Liq. Prop. | ARREGLO | Filtro por ciclo (últimos 5) | 8 | $2,500 | $0 |
| Liq. Prop. | ARREGLO | Desarrollo Backend | 10 | $2,500 | $0 |
| Liq. Prop. | ARREGLO | Desarrollo Frontend | 6 | $2,500 | $0 |
| Liq. Prop. | ARREGLO | Carga de anexos | 12 | $2,500 | $0 |
| Liq. Prop. | ARREGLO | Desarrollo Backend anexos | 16 | $2,500 | $0 |
| Liq. Prop. | ARREGLO | Desarrollo Frontend anexos | 10 | $2,500 | $0 |
| Liq. Prop. | ARREGLO | Pruebas | 8 | $2,500 | $0 |
| Liq. Prop. | NUEVO | Notificación WhatsApp | 24 | $3,000 | $72,000 |
| Liq. Prop. | NUEVO | Integración WhatsApp API | 16 | $3,000 | $48,000 |
| Liq. Prop. | NUEVO | Generación PDF | 20 | $2,500 | $50,000 |
| Liq. Prop. | NUEVO | Pruebas | 12 | $2,500 | $30,000 |
| Liq. Prop. | NUEVO | Documentación | 8 | $2,500 | $20,000 |
| **Subtotal Liq. Prop.** | | | **150** | | **$220,000** |

### 4.6 Recaudos Arrendatario

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Rec. Arrend. | ARREGLO | Columna codeudor | 6 | $2,500 | $0 |
| Rec. Arrend. | ARREGLO | Desarrollo Backend | 8 | $2,500 | $0 |
| Rec. Arrend. | ARREGLO | Desarrollo Frontend | 6 | $2,500 | $0 |
| Rec. Arrend. | ARREGLO | Pruebas | 4 | $2,500 | $0 |
| Rec. Arrend. | NUEVO | Notificación WhatsApp | 24 | $3,000 | $72,000 |
| Rec. Arrend. | NUEVO | Integración WhatsApp API | 16 | $3,000 | $48,000 |
| Rec. Arrend. | NUEVO | Pruebas | 12 | $2,500 | $30,000 |
| Rec. Arrend. | NUEVO | Documentación | 8 | $2,500 | $20,000 |
| **Subtotal Rec. Arrend.** | | | **84** | | **$170,000** |

### 4.7 Desocupaciones

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Desocup. | ARREGLO | Registro con fechas | 12 | $2,500 | $0 |
| Desocup. | ARREGLO | Finalización automática | 16 | $2,500 | $0 |
| Desocup. | ARREGLO | Eliminación liquidación/recaudo | 14 | $2,500 | $0 |
| Desocup. | ARREGLO | Carga de anexos | 10 | $2,500 | $0 |
| Desocup. | ARREGLO | Desarrollo Backend | 20 | $2,500 | $0 |
| Desocup. | ARREGLO | Desarrollo Frontend | 12 | $2,500 | $0 |
| Desocup. | ARREGLO | Pruebas | 10 | $2,500 | $0 |
| Desocup. | ARREGLO | Documentación | 6 | $2,500 | $0 |
| **Subtotal Desocup.** | | | **100** | | **$0** |

### 4.8 Incidentes

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Incidentes | ARREGLO | Mejora paginación | 10 | $2,500 | $0 |
| Incidentes | ARREGLO | Optimización tabla | 8 | $2,500 | $0 |
| Incidentes | ARREGLO | Desarrollo Backend | 12 | $2,500 | $0 |
| Incidentes | ARREGLO | Desarrollo Frontend | 10 | $2,500 | $0 |
| Incidentes | ARREGLO | Pruebas | 8 | $2,500 | $0 |
| Incidentes | ARREGLO | Documentación | 4 | $2,500 | $0 |
| Incidentes | NUEVO | Notificación WhatsApp | 24 | $3,000 | $72,000 |
| Incidentes | NUEVO | Integración WhatsApp API | 16 | $3,000 | $48,000 |
| Incidentes | NUEVO | Generación PDF | 20 | $2,500 | $50,000 |
| Incidentes | NUEVO | Pruebas | 12 | $2,500 | $30,000 |
| Incidentes | NUEVO | Documentación | 8 | $2,500 | $20,000 |
| **Subtotal Incidentes** | | | **132** | | **$220,000** |

### 4.9 Seguros

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Seguros | NUEVO | Análisis de requerimientos | 12 | $2,500 | $30,000 |
| Seguros | NUEVO | Diseño UI/UX | 16 | $2,500 | $40,000 |
| Seguros | NUEVO | Diseño de base de datos | 12 | $2,500 | $30,000 |
| Seguros | NUEVO | Desarrollo Backend | 32 | $2,500 | $80,000 |
| Seguros | NUEVO | Desarrollo Frontend | 24 | $2,500 | $60,000 |
| Seguros | NUEVO | Sistema de recordatorios | 20 | $2,500 | $50,000 |
| Seguros | NUEVO | Pruebas | 16 | $2,500 | $40,000 |
| Seguros | NUEVO | Documentación técnica | 8 | $2,500 | $20,000 |
| Seguros | NUEVO | Documentación usuario | 6 | $2,500 | $15,000 |
| **Subtotal Seguros** | | | **152** | | **$365,000** |

### 4.10 Recibos Públicos

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Rec. Púb. | NUEVO | Análisis de cálculos | 12 | $2,500 | $30,000 |
| Rec. Púb. | NUEVO | Diseño de algoritmo | 10 | $2,500 | $25,000 |
| Rec. Púb. | NUEVO | Desarrollo Backend | 24 | $2,500 | $60,000 |
| Rec. Púb. | NUEVO | Desarrollo Frontend | 16 | $2,500 | $40,000 |
| Rec. Púb. | NUEVO | Pruebas | 12 | $2,500 | $30,000 |
| Rec. Púb. | NUEVO | Documentación | 8 | $2,500 | $20,000 |
| **Subtotal Rec. Púb.** | | | **82** | | **$205,000** |

### 4.11 Usuarios

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Usuarios | ARREGLO | Confirmación eliminación | 6 | $2,500 | $0 |
| Usuarios | ARREGLO | Desarrollo Frontend | 8 | $2,500 | $0 |
| Usuarios | ARREGLO | Desarrollo Backend | 6 | $2,500 | $0 |
| Usuarios | ARREGLO | Pruebas | 4 | $2,500 | $0 |
| Usuarios | ARREGLO | Documentación | 2 | $2,500 | $0 |
| **Subtotal Usuarios** | | | **26** | | **$0** |

### 4.12 Reportes

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Reportes | ARREGLO | Validación visualización | 8 | $2,500 | $0 |
| Reportes | ARREGLO | Validación exportación | 8 | $2,500 | $0 |
| Reportes | ARREGLO | Correcciones Backend | 12 | $2,500 | $0 |
| Reportes | ARREGLO | Correcciones Frontend | 10 | $2,500 | $0 |
| Reportes | ARREGLO | Pruebas | 8 | $2,500 | $0 |
| Reportes | ARREGLO | Documentación | 4 | $2,500 | $0 |
| **Subtotal Reportes** | | | **50** | | **$0** |

### 4.13 Documentos

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| Documentos | NUEVO | Análisis de requerimientos | 12 | $2,500 | $30,000 |
| Documentos | NUEVO | Diseño de plantillas | 20 | $2,500 | $50,000 |
| Documentos | NUEVO | Diseño UI/UX | 16 | $2,500 | $40,000 |
| Documentos | NUEVO | Desarrollo Backend | 32 | $2,500 | $80,000 |
| Documentos | NUEVO | Desarrollo Frontend | 24 | $2,500 | $60,000 |
| Documentos | NUEVO | Generación PDF | 20 | $2,500 | $50,000 |
| Documentos | NUEVO | Pruebas | 16 | $2,500 | $40,000 |
| Documentos | NUEVO | Documentación técnica | 8 | $2,500 | $20,000 |
| Documentos | NUEVO | Documentación usuario | 6 | $2,500 | $15,000 |
| **Subtotal Documentos** | | | **154** | | **$385,000** |

### 4.14 VELAR

| Módulo | Clasificación | Actividad | Horas | Tarifa | Valor |
|--------|---------------|-----------|-------|--------|-------|
| VELAR | NUEVO | Análisis de requerimientos | 16 | $2,500 | $40,000 |
| VELAR | NUEVO | Diseño de arquitectura | 20 | $2,500 | $50,000 |
| VELAR | NUEVO | Diseño UI/UX | 24 | $2,500 | $60,000 |
| VELAR | NUEVO | Desarrollo Backend | 48 | $2,500 | $120,000 |
| VELAR | NUEVO | Desarrollo Frontend | 36 | $2,500 | $90,000 |
| VELAR | NUEVO | Integración de módulos | 32 | $2,500 | $80,000 |
| VELAR | NUEVO | Pruebas de integración | 24 | $2,500 | $60,000 |
| VELAR | NUEVO | Pruebas funcionales | 16 | $2,500 | $40,000 |
| VELAR | NUEVO | Documentación técnica | 12 | $2,500 | $30,000 |
| VELAR | NUEVO | Documentación usuario | 8 | $2,500 | $20,000 |
| **Subtotal VELAR** | | | **236** | | **$590,000** |

---

## 5. RESUMEN GENERAL

| Módulo | Horas | Valor |
|--------|-------|-------|
| Dashboard | 46 | $0 |
| Personas | 50 | $0 |
| Contratos | 226 | $564,000 |
| Propiedad Horizontal | 126 | $200,000 |
| Liquidaciones Propietario | 150 | $220,000 |
| Recaudos Arrendatario | 84 | $170,000 |
| Desocupaciones | 100 | $0 |
| Incidentes | 132 | $220,000 |
| Seguros | 152 | $365,000 |
| Recibos Públicos | 82 | $205,000 |
| Usuarios | 26 | $0 |
| Reportes | 50 | $0 |
| Documentos | 154 | $385,000 |
| VELAR | 236 | $590,000 |
| **TOTAL** | **1,614** | **$2,919,000** |

---

## 6. COSTOS ADICIONALES

| Concepto | Porcentaje | Valor |
|----------|------------|-------|
| Riesgos del proyecto | 5% | $145,950 |
| Utilidad | 10% | $291,900 |
| **Total Costos Adicionales** | | **$437,850** |

---

## 7. VALOR TOTAL DEL PROYECTO

| Concepto | Valor |
|----------|-------|
| Horas totales | 1,614 |
| Valor base | $2,919,000 |
| Riesgos (5%) | $145,950 |
| Utilidad (10%) | $291,900 |
| **VALOR FINAL** | **$3,356,850** |

---

## 8. CRONOGRAMA GENERAL

| Módulo | Inicio | Fin | Duración | Dependencias |
|--------|--------|-----|----------|--------------|
| Dashboard | 20/ago/2026 | 26/ago/2026 | 1 semana | - |
| Personas | 20/ago/2026 | 02/sep/2026 | 2 semanas | - |
| Usuarios | 20/ago/2026 | 26/ago/2026 | 1 semana | - |
| Reportes | 27/ago/2026 | 09/sep/2026 | 2 semanas | - |
| Contratos (ARREGLO) | 27/ago/2026 | 02/sep/2026 | 1 semana | - |
| Desocupaciones | 10/sep/2026 | 30/sep/2026 | 3 semanas | - |
| Propiedad Horizontal (ARREGLOS) | 10/sep/2026 | 30/sep/2026 | 3 semanas | - |
| Recaudos Arrendatario (ARREGLO) | 01/oct/2026 | 14/oct/2026 | 2 semanas | - |
| Incidentes (ARREGLO) | 01/oct/2026 | 21/oct/2026 | 3 semanas | - |
| Liquidaciones Propietario (ARREGLOS) | 15/oct/2026 | 04/nov/2026 | 3 semanas | - |
| Contratos (NUEVOS) | 22/oct/2026 | 09/dic/2026 | 7 semanas | Contratos ARREGLO |
| Propiedad Horizontal (NUEVO) | 22/oct/2026 | 18/nov/2026 | 4 semanas | PH ARREGLOS |
| Liquidaciones Propietario (NUEVO) | 05/nov/2026 | 02/dic/2026 | 4 semanas | Liq. Prop. ARREGLOS |
| Recaudos Arrendatario (NUEVO) | 22/oct/2026 | 18/nov/2026 | 4 semanas | Rec. Arrend. ARREGLO |
| Incidentes (NUEVO) | 22/oct/2026 | 18/nov/2026 | 4 semanas | Incidentes ARREGLO |
| Seguros | 05/nov/2026 | 09/dic/2026 | 5 semanas | - |
| Recibos Públicos | 19/nov/2026 | 16/dic/2026 | 4 semanas | - |
| Documentos | 26/nov/2026 | 30/dic/2026 | 5 semanas | - |
| VELAR | 10/dic/2026 | 11/feb/2027 | 9 semanas | Todos los módulos |

---

## 9. ENTREGABLES

La propuesta incluye:

1. Levantamiento de requerimientos
2. Diseño de la solución
3. Arquitectura de software
4. Desarrollo Backend
5. Desarrollo Frontend
6. Diseño y ajustes de Base de Datos
7. Desarrollo de API REST
8. Implementación de autenticación y autorización
9. Controles de seguridad
10. Pruebas unitarias
11. Pruebas funcionales
12. Pruebas de integración
13. Pruebas de regresión
14. Documentación técnica
15. Manual de usuario
16. Despliegue en ambiente productivo
17. Capacitación funcional
18. Garantía sobre los desarrollos
19. Soporte posterior (si aplica)

---

## 10. SUPUESTOS

1. El cliente proporcionará acceso a la plataforma existente para análisis
2. Se contará con un punto de contacto disponible para reuniones de revisión
3. Los requerimientos están clarificados y no cambiarán durante el desarrollo
4. El ambiente de desarrollo y producción estarán disponibles
5. Se asume uso de servicios externos (API WhatsApp) con costos adicionales no incluidos
6. Las pruebas se realizarán con datos de prueba proporcionados por el cliente

---

## 11. EXCLUSIONES

1. Costos de hosting o infraestructura de nube
2. Licencias de software de terceros
3. Costos de API externas (WhatsApp, servicios de PDF)
4. Mantenimiento posterior a la garantía
5. Capacitación avanzada o soporte técnico continuo
6. Cambios en requerimientos no contemplados en esta propuesta
7. Desarrollo de funcionalidades no especificadas

---

## 12. OBSERVACIONES

1. **Tecnología:** El desarrollo se realizará sobre la plataforma existente de Reflex (Python)
2. **Integraciones:** Se requiere configuración de cuentas en servicios de WhatsApp Business API
3. **Seguridad:** Se implementarán controles de acceso y auditoría en todos los nuevos módulos
4. **Escalabilidad:** La arquitectura permitirá futuras ampliaciones sin cambios estructurales
5. **Calidad:** Se aplicarán prácticas de código limpio y revisiones de código
6. **Documentación:** Se entregará documentación técnica y de usuario completa
7. **Garantía:** Se ofrece garantía de 3 meses sobre los desarrollos realizados

---

**Fin de la Propuesta Comercial**

---

## RESUMEN DE TARIFAS

| Tipo de Desarrollo | Tarifa por Hora |
|--------------------|-----------------|
| Desarrollo General | $2,500 COP |
| Integración WhatsApp | $3,000 COP |

**Horas por tipo de tarifa:**
- Horas a $2,500: 1,286 horas (Desarrollo General)
- Horas a $3,000: 328 horas (Integración WhatsApp)

---

## RESUMEN FINANCIERO FINAL

| Concepto | Valor |
|----------|-------|
| Valor base (1,614 horas) | $2,919,000 |
| Riesgos (5%) | $145,950 |
| Utilidad (10%) | $291,900 |
| **VALOR TOTAL PROYECTO** | **$3,356,850** |
