# Auditoría e Ingeniería Inversa: Módulo de Propiedad Horizontal

**Fecha de Auditoría**: 2026-07-25
**Estado**: En progreso

## Resumen Ejecutivo

Este informe detalla los hallazgos de una auditoría exhaustiva y no destructiva al módulo de "Propiedad Horizontal". El módulo es estructuralmente robusto, adhiriéndose a Clean Architecture (Reflex + PostgreSQL), pero presenta oportunidades de mejora en el manejo de estado masivo y consultas N+1 en facturación. El riesgo principal radica en la escalabilidad a futuro debido a la falta de paginación del lado del servidor en las pantallas principales.

## Análisis Funcional Integral

El módulo de Propiedad Horizontal opera como el núcleo de la gestión de inmuebles dentro del sistema inmobiliario. Su flujo de trabajo primario abarca desde la creación de propiedades y contratos hasta la liquidación y recaudo de cuotas u obligaciones.

### Flujo de Trabajo y Ciclo de Vida
1. **Gestión de Propiedades y Contratos**: Los inmuebles se registran con sus características, propietarios y residentes. Los contratos asocian entidades (inquilinos/propietarios) a obligaciones financieras.
2. **Ciclo de Liquidación**: Periódicamente (o bajo demanda), se generan **Liquidaciones**. Este proceso está acoplado a la generación de estados de cuenta (PDFs).
3. **Gestión de Incidentes (PQRs)**: Permite registrar eventos, quejas o mantenimientos asociados a propiedades, los cuales pueden tener un impacto financiero.
4. **Ciclo de Recaudo**: Se registran los pagos contra las liquidaciones generadas, actualizando el estado de cuenta y el saldo del contrato.

### Validaciones y Reglas de Negocio
- La generación de liquidaciones requiere contratos activos y dependencias financieras correctas.
- Los recaudos no pueden exceder los saldos pendientes sin generar alertas.
- Existen restricciones operativas ligadas al control de acceso (RBAC) para acciones destructivas.

## Inventario de Funcionalidades

A continuación se catalogan las capacidades implementadas asociadas al ecosistema de Propiedad Horizontal:

| Funcionalidad | Descripción | Estado Actual |
| --- | --- | --- |
| **CRUD de Propiedades** | Creación y edición de inmuebles, locales y unidades residenciales. | **Operativa** |
| **Gestión de Contratos** | Asignación de arrendatarios, propietarios y condiciones. | **Operativa** |
| **Liquidaciones** | Generación de cobros masivos o individuales. | **Candidata a refactorización** (Mejoras en rendimiento) |
| **Generación de Estado de Cuenta (PDF)** | Exportación de PDF usando infraestructura nativa. | **Operativa** |
| **Gestión de Recaudos** | Registro de ingresos y conciliación de saldos. | **Operativa** |
| **Gestión de Incidentes** | Control de requerimientos y tickets. | **Operativa** |

## Análisis Técnico y Arquitectónico

La arquitectura técnica se adhiere a la **Clean Architecture** promovida en las normativas del proyecto (`GEMINI.md`), dividiendo el código en Dominio, Aplicación, Infraestructura y Presentación (Reflex).

### Frontend (Reflex)
- **Componentes y Estados**: La UI está fuertemente modularizada en `src/presentacion_reflex/components/`. Existe un uso riguroso de componentes atómicos.
- **Manejo de Estado**: Se apoya fuertemente en mutaciones atómicas a través de clases de Estado (ej. `state/incidentes`).

### Backend y Persistencia
- **Repositorios**: Se utiliza un patrón de repositorio puro (ej. `repositorio_propiedades.py`) que interactúa con PostgreSQL usando `psycopg2` y/o SQLAlchemy.
- **Reglas Transaccionales**: Uso estricto de placeholders `%s` y sentencias `RETURNING id`. Ausencia de Flet y SQLite en los flujos principales.

### Dependencias
- Externas: Base de datos alojada en Railway (PostgreSQL). Servicios de generación PDF.
- Internas: El módulo de Propiedad Horizontal está fuertemente acoplado a Contratos y Liquidaciones.

## Ingeniería Inversa de Base de Datos

### Modelo Lógico y Tablas Principales
Las siguientes entidades primarias conforman la columna vertebral del módulo:

1. `propiedades`: Tabla central, almacena inmuebles (ID, tipo, dirección, dimensiones, estado).
2. `contratos`: Enlaza `propiedades` con `personas` (inquilinos/propietarios), definiendo responsabilidades financieras (cánones).
3. `liquidaciones`: Registros contables generados por contrato y ciclo.
4. `recaudos`: Abonos financieros contra `liquidaciones`.
5. `incidentes`: Tickets asociados a `propiedades`.

### Hallazgos de BD
- **Consistencia**: Alta adherencia a integridad referencial con claves foráneas explícitas.
- **Anomalías**: La búsqueda de propiedades podría beneficiarse de índices full-text o índices compuestos para agilizar filtros complejos.

## Deuda Técnica

Tras la auditoría estática, se identifica la siguiente deuda técnica:

1. **Rendimiento (N+1)**: El módulo de liquidaciones realiza múltiples consultas iterativas a la BD para calcular los cobros (problema clásico N+1).
2. **Duplicidad Funcional**: La lógica de cálculo de recargos por mora está presente tanto en la capa de frontend (para preview) como en el servicio de backend.
3. **Paginación**: Las tablas en el frontend de Propiedades no cuentan con paginación optimizada desde el backend, cargando el 100% de los datos a memoria (escalabilidad limitada).
4. **Acoplamiento**: Algunos componentes en `src/presentacion_reflex/components/liquidaciones/` están directamente importando consultas SQL en lugar de usar los servicios de dominio.

## Diagnóstico de Riesgos

| Categoría | Riesgo Identificado | Nivel de Criticidad | Impacto |
| --- | --- | --- | --- |
| **Escalabilidad** | Carga completa de datos (Sin Paginación DB) | **Alto** | Degrada severamente la experiencia de usuario si el número de inmuebles supera los 1,000 registros. |
| **Operativo** | Duplicidad lógica de cálculo de mora | **Medio** | Inconsistencia entre lo que ve el usuario vs. lo facturado. |
| **Rendimiento** | Consultas N+1 en liquidaciones | **Medio** | Tiempos de timeout durante la facturación masiva. |
| **Técnico** | Acoplamiento de UI y DB | **Bajo** | Dificulta las pruebas unitarias y el re-uso de componentes. |

## Plan de Evolución

Con base en la deuda técnica y riesgos detectados, se recomienda el siguiente roadmap:

### Corto Plazo (Fixes Críticos)
- **Implementar Paginación Backend**: Modificar `repositorio_propiedades.py` para soportar `LIMIT` y `OFFSET`.
- **Eliminar Consultas N+1**: Usar JOINs y cargas eager (Eager Loading) en el cálculo masivo de liquidaciones.

### Mediano Plazo (Refactorización)
- **Centralizar Lógica de Negocio**: Trasladar toda la lógica financiera de UI a la capa de Aplicación/Dominio. Exponer APIs puras para Reflex.
- **Desacoplar Componentes UI**: Limpiar los imports en la capa `presentacion_reflex` garantizando que no existan llamadas a la capa de persistencia.

### Largo Plazo (Modernización)
- **Optimización de BD**: Añadir índices en campos de búsqueda frecuentes.
- **Observabilidad**: Implementar un middleware para rastrear los tiempos de las transacciones (Tracing) en los procesos más lentos (liquidaciones).
