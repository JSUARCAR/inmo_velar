# Feature Specification: Sincronización y Diagnóstico de Filtro de Estado de Pago en Producción

**Feature Branch**: `feat/desarrollo-experto-elite` -> `main`

**Created**: 2026-07-06

**Status**: Draft

**Input**: User description: "/speckit-specify Quiero que realices un proceso de ingeniería inversa..."

## Diagnóstico Técnico

La inconsistencia descrita entre el entorno **local** y el entorno de **producción** en el filtro **Estado de Pago** del módulo de Incidentes ha sido diagnosticada mediante análisis del control de versiones.

**Causa Raíz Identificada:**
Un despliegue incompleto originado por la falta de sincronización (merge) entre las ramas del repositorio.
- Los cambios que implementan y corrigen el filtro de Estado de Pago (`14f8704`, `82d5753`, `575b54a`, `2fa1002`) existen actualmente en la rama de desarrollo **local y remota** `feat/desarrollo-experto-elite`.
- La rama **`main`**, la cual se utiliza para el despliegue automático en Railway, no contiene estos commits. El entorno local se ejecuta sobre `feat/desarrollo-experto-elite`, mientras que producción se ejecuta sobre `main`.
- En conclusión: el código en producción no posee la implementación del filtro de Estado de Pago ni sus correspondientes correcciones.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sincronización del Filtro de Estado de Pago (Priority: P1)

Como usuario administrador, quiero poder filtrar los incidentes por su estado de pago en el entorno de producción, de la misma manera que puedo hacerlo en el entorno local, para gestionar eficientemente las cuentas por cobrar asociadas a incidentes.

**Why this priority**: Es la funcionalidad core reportada como faltante en producción.

**Independent Test**: Can be fully tested by merging the changes to `main`, waiting for Railway deployment, and verifying the filter options at `https://extraordinary-joy-production-2fd2.up.railway.app/incidentes`.

**Acceptance Scenarios**:

1. **Given** el sistema en producción desplegado con la última versión de `main`, **When** accedo al módulo de Incidentes, **Then** el filtro de Estado de Pago debe mostrar las opciones: "Todos", "Pendiente", "Asociada" y "Pagada".
2. **Given** un incidente con cuotas pendientes en producción, **When** selecciono la opción "Pendiente" en el filtro, **Then** el listado debe mostrar únicamente los incidentes en dicho estado de pago.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El repositorio MUST sincronizar la rama `feat/desarrollo-experto-elite` hacia la rama `main` de manera segura (vía Merge Commit o Pull Request).
- **FR-002**: La plataforma de despliegue continuo (Railway) MUST desencadenar un build automático al actualizarse la rama `main`.
- **FR-003**: El código desplegado MUST incluir la lógica del componente `ComboBox` que provee las opciones de los estados en `src/dominio/entidades/cuota_incidente.py`.
- **FR-004**: Los cambios de inicialización del filtro ("Todos" por defecto) MUST persistir en producción para evitar glitches en la UI.

### Key Entities

- **Incidente**: Entidad principal que presenta un estado de pago.
- **CuotaIncidente**: Representa el estado financiero del incidente que alimenta las opciones del filtro (Pendiente, Asociada, Pagada).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de paridad en las opciones del filtro de Estado de Pago entre el entorno local (`localhost:3000`) y producción (`extraordinary-joy-...railway.app`).
- **SC-002**: El historial de Git en `main` contiene los commits relacionados a la feature `filtro por estado de pago en listado de incidentes`.
- **SC-003**: No existen errores en consola en producción al cambiar entre las distintas opciones del filtro.

## Assumptions

- Se asume que el backend y la base de datos de producción (PostgreSQL) ya están preparados para procesar la consulta SQL que filtra por estado de pago, dado que no ha habido reportes de errores de esquema.
- El despliegue de Railway se realiza automáticamente desde la rama `main`.
