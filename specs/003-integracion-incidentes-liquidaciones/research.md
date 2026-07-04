# Research: Integración Incidentes y Liquidaciones de Propietarios

**Date**: 2026-06-30
**Feature**: 003-integracion-incidentes-liquidaciones

## Research Tasks

### 1. Arquitectura Existente de Incidentes

**Decision**: Mantener la arquitectura existente con Clean Architecture (domain/infrastructure/application/presentation)

**Rationale**: 
- El códigobase sigue un patrón de arquitectura limpia bien establecido
- Los módulos de incidentes y liquidaciones ya están implementados con este patrón
- Mantener consistencia reduce deuda técnica y facilita mantenimiento

**Alternatives Considered**:
- Arquitectura.hexagonal: Requeriría refactorización significativa
- Microservicios: Inecesario para el alcance de esta feature

**Key Findings**:
- `src/dominio/entidades/incidente.py`: Entidad con 30+ atributos, estados controlados por transiciones
- `src/infraestructura/persistencia/repositorio_incidentes_postgres.py`: Repository con 500+ líneas, maneja cotizaciones e historial
- `src/aplicacion/servicios/servicio_incidentes.py`: Service layer con transacciones y auditoría

### 2. Arquitectura Existente de Liquidaciones

**Decision**: Extender la entidad Liquidacion existente en lugar de crear nueva entidad

**Rationale**:
- La entidad `Liquidacion` ya existe con campos como `gastos_reparaciones`
- Agregar `valor_incidentes` es consistente con el patrón existente
- Evita duplicación de conceptos

**Alternatives Considered**:
- Crear entidad separada `LiquidacionConIncidentes`: Requeriría cambios en múltiples capas
- Tabla de relación exclusiva: Más compleja sin beneficio claro

**Key Findings**:
- `src/dominio/entidades/liquidacion.py`: Entidad con campos financieros completos
- `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`: Repository con 1200+ líneas, maneja consolidación por propietario
- Campo `gastos_reparaciones` ya existe para incidentes - el nuevo `valor_incidentes` será un descuento adicional

### 3. Sistema de Permisos

**Decision**: Reutilizar el sistema de permisos existente con nuevas acciones

**Rationale**:
- `AuthState.check_action()` ya soporta verificación por módulo y acción
- Solo se necesitan registrar nuevas acciones: `DEFINIR_PLAN_PAGO` y `SELECCIONAR_INCIDENTES`
- Consistencia con el patrón de permisos existente

**Alternatives Considered**:
- Sistema de permisos basado en roles: Ya implementado parcialmente
- Permisos a nivel de campo: Demasiado granular para esta feature

**Key Findings**:
- `src/core/auth.py`: Maneja autenticación y permisos
- Permisos registrados en base de datos con estructura (modulo, accion, rol)

### 4. Sistema de Auditoría

**Decision**: Extender AUDITORIA_CAMBIOS con campos adicionales

**Rationale**:
- La tabla AUDITORIA_CAMBIOS ya existe con triggers en LIQUIDACIONES
- Agregar campos `direccion_ip`, `id_sesion`, `justificacion` es no disruptivo
- Mantiene consistencia con auditoría existente

**Alternatives Considered**:
- Tabla separada de auditoría de pagos: Fragmentaría la auditoría
- Sistema de audit log externo: Agregaría dependencia innecesaria

**Key Findings**:
- Tabla AUDITORIA_CAMBIOS: Campos TABLA, ID_REGISTRO, CAMPO_MODIFICADO, VALOR_NUEVO, USUARIO, FECHA_MODIFICACION
- Trigger existente en LIQUIDACIONES captura cambios automáticos

### 5. Mecanismo de Bloqueo Concurrency

**Decision**: Implementar bloqueo pesimista con tabla de locks

**Rationale**:
- El requisito especifica bloqueo pesimista explícito
- Tabla `BLOQUEOS_EDICION` permite tracking de quién edita qué
- Timeout automático previene locks permanentes

**Alternatives Considered**:
- Bloqueo pesimista con FOR UPDATE: Menos transparente para la UI
- Bloqueo optimista con versionado: No cumple requisito de "En edición por [usuario]"

**Key Findings**:
- Necesidad de campo `editado_por` en tabla de incidentes o tabla separada
- Timeout de 5 minutos para liberar locks automáticamente
- UI debe mostrar "En edición por [usuario]" cuando detecte lock activo

### 6. Cálculo Automático de Estado de Pago

**Decision**: Calcular estado de pago en tiempo real via consulta SQL

**Rationale**:
- El estado de pago es derivado del estado de las liquidaciones asociadas
- Almacenarlo como campo持久izado permite consultas eficientes
- Se actualiza cuando cambia estado de liquidación

**Fórmula de cálculo**:
```
Si no hay liquidaciones asociadas → "Pendiente"
Si TODAS las liquidaciones asociadas están en "Pagada" → "Pagado"
Si ALGUNA liquidación está en "Pagada" pero no todas → "Parcialmente Pagado"
Si NINGUNA está en "Pagada" → "Pendiente"
```

**Alternatives Considered**:
- Calcular en cada consulta: Ineficiente para listados
- Trigger en base de datos: Menos mantenible, lógica en application layer preferida

### 7. Estrategia de Migración de Datos

Decision**: Migración incremental sin downtime

**Rationale**:
- Tabla LIQUIDACIONES ya tiene campo `gastos_reparaciones`
- Nuevo campo `valor_incidentes` puede agregarse sin afectar datos existentes
- Tablas nuevas (PLAN_PAGO_INCIDENTE, CUOTA_INCIDENTE, INCIDENTE_LIQUIDACION) son adicionales

**Script de migración**:
```sql
-- 1. Agregar campo a LIQUIDACIONES
ALTER TABLE LIQUIDACIONES ADD COLUMN valor_incidentes INTEGER DEFAULT 0;

-- 2. Agregar campo a INCIDENTES
ALTER TABLE INCIDENTES ADD COLUMN estado_pago TEXT DEFAULT 'Pendiente';

-- 3. Crear tabla de planes de pago
CREATE TABLE PLAN_PAGO_INCIDENTE (...);

-- 4. Crear tabla de cuotas
CREATE TABLE CUOTA_INCIDENTE (...);

-- 5. Crear tabla de relación
CREATE TABLE INCIDENTE_LIQUIDACION (...);

-- 6. Crear tabla de locks (opcional)
CREATE TABLE BLOQUEOS_EDICION (...);
```

### 8. Patrones de UI/UX

**Decision**: Modales siguiendo patrón existente de neuro_elements

**Rationale**:
- Los componentes UI existentes ya manejan modales, formularios, y tablas
- `modal_edit_incidente.py` y `liquidacion_detail_modal.py` son referencia directa
- Consistencia visual con el resto de la aplicación

**Componentes a crear**:
- `modal_plan_pago.py`: Modal para definir plan de pago del incidente
- `modal_seleccion_incidentes.py`: Modal para seleccionar incidentes en liquidación

**Key Findings**:
- Estado de modales manejado en `incidentes_state.py` y `liquidaciones_state.py`
- Patrón: `show_*_modal: bool` + `open_*_modal()` + `close_*_modal()`

## Summary of Decisions

| Area | Decision | Impact |
|------|----------|--------|
| Arquitectura | Mantener Clean Architecture existente | Bajo - solo agregar nuevas entidades |
| Almacenamiento | Extender entidades existentes | Bajo - migración no disruptiva |
| Permisos | Reutilizar sistema existente | Bajo - solo nuevas acciones |
| Auditoría | Extender tabla AUDITORIA_CAMBIOS | Bajo - campos adicionales |
| Concurrency | Bloqueo pesimista con tabla | Medio - nueva tabla + lógica UI |
| Cálculo Estado | Campo persistido + actualización | Bajo - consulta SQL eficiente |
| Migración | Incremental sin downtime | Bajo - scripts SQL |
| UI/UX | Modales siguiendo patrón existente | Bajo - componentes conocidos |
