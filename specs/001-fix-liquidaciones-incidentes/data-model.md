# Data Model: Corrección de Selección de Incidentes en Liquidaciones

**Date**: 2026-07-06

## Entidades Principales

### Liquidación

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| ID_LIQUIDACION | INTEGER | Identificador único | PK, AUTO_INCREMENT |
| ID_CONTRATO_M | INTEGER | Referencia al contrato de mandato | FK → CONTRATOS_MANDATOS |
| PERIODO | VARCHAR(7) | Período de la liquidación (YYYY-MM) | NOT NULL |
| ESTADO | VARCHAR(20) | Estado de la liquidación | ENUM: 'En Proceso', 'Aprobada', 'Pagada', 'Cancelada' |
| CANON | DECIMAL(12,2) | Canon del mandato | >= 0 |
| NETO | DECIMAL(12,2) | Neto a pagar | Calculado |
| VALOR_INCIDENTES | DECIMAL(12,2) | Total de descuentos por incidentes | >= 0, default 0 |
| OBSERVACIONES | TEXT | Notas adicionales | NULL permitido |
| CREATED_AT | TIMESTAMP | Fecha de creación | DEFAULT NOW() |
| CREATED_BY | VARCHAR(100) | Usuario creador | NOT NULL |

**Relaciones**:
- 1:N con INCIDENTE_LIQUIDACION (una liquidación puede tener múltiples incidentes)
- N:1 con CONTRATOS_MANDATOS (una liquidación pertenece a un contrato)

### Incidente

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| ID_INCIDENTE | INTEGER | Identificador único | PK, AUTO_INCREMENT |
| ID_PROPIEDAD | INTEGER | Propiedad del incidente | FK → PROPIEDADES |
| ID_CONTRATO_M | INTEGER | Contrato asociado | FK → CONTRATOS_MANDATOS, NULL permitido |
| DESCRIPCION_INCIDENTE | TEXT | Descripción del incidente | NOT NULL |
| COSTO_INCIDENTE | DECIMAL(12,2) | Costo total del incidente | >= 0 |
| ESTADO | VARCHAR(20) | Estado del incidente | ENUM: 'Aprobado', 'En Reparacion', 'Finalizado', 'Cancelado' |
| ESTADO_PAGO | VARCHAR(20) | Estado de pago | ENUM: 'Pendiente', 'Parcialmente Pagado', 'Pagado' |

**Relaciones**:
- N:1 con PROPIEDADES (un incidente pertenece a una propiedad)
- N:1 con CONTRATOS_MANDATOS (un incidente puede estar asociado a un contrato)
- 1:N con INCIDENTE_LIQUIDACION (un incidente puede asociarse a múltiples liquidaciones)

### IncidenteLiquidación (Tabla de Relación)

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| ID | INTEGER | Identificador único | PK, AUTO_INCREMENT |
| ID_INCIDENTE | INTEGER | Referencia al incidente | FK → INCIDENTES |
| ID_LIQUIDACION | INTEGER | Referencia a la liquidación | FK → LIQUIDACIONES |
| NUMERO_CUOTA | INTEGER | Número de cuota asociada | NOT NULL |
| VALOR_DESCUENTO | DECIMAL(12,2) | Valor del descuento | >= 0 |
| ASOCIADO_POR | VARCHAR(100) | Usuario que asoció | NOT NULL |
| JUSTIFICACION | TEXT | Motivo de la asociación | NULL permitido |
| CREATED_AT | TIMESTAMP | Fecha de asociación | DEFAULT NOW() |

**Restricciones**:
- UNIQUE(ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA) - Un incidente no puede asociarse dos veces a la misma liquidación con la misma cuota

**Relaciones**:
- N:1 con INCIDENTES
- N:1 con LIQUIDACIONES

### Propiedad

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| ID_PROPIEDAD | INTEGER | Identificador único | PK |
| MATRICULA_INMOBILIARIA | VARCHAR(50) | Matrícula de la propiedad | UNIQUE |
| DIRECCION_PROPIEDAD | VARCHAR(255) | Dirección de la propiedad | NOT NULL |
| VALOR_ADMINISTRACION | DECIMAL(12,2) | Valor de administración | >= 0 |

### ContratoMandato

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| ID_CONTRATO_M | INTEGER | Identificador único | PK |
| ID_PROPIEDAD | INTEGER | Propiedad del contrato | FK → PROPIEDADES |
| ID_PROPIETARIO | INTEGER | Propietario del contrato | FK → PROPIETARIOS |
| CANON_MANDATO | DECIMAL(12,2) | Canon del mandato | >= 0 |
| ESTADO_CONTRATO_M | VARCHAR(20) | Estado del contrato | ENUM: 'ACTIVO', 'INACTIVO', 'CANCELADO' |

## Diagrama de Relaciones

```
┌─────────────────┐
│   PROPIEDADES   │
├─────────────────┤
│ ID_PROPIEDAD PK │
│ MATRICULA       │
│ DIRECCION       │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐      ┌─────────────────┐
│ CONTRATOS_MANDA │◄─────│   LIQUIDACIONES │
├─────────────────┤      ├─────────────────┤
│ ID_CONTRATO_M PK│      │ ID_LIQUIDACION PK│
│ ID_PROPIEDAD FK │      │ ID_CONTRATO_M FK │
│ ID_PROPIETARIO FK│      │ VALOR_INCIDENTES │
│ CANON_MANDATO   │      │ OBSERVACIONES    │
└────────┬────────┘      └────────┬────────┘
         │                        │
         │                        │ 1:N
         │                        ▼
         │              ┌─────────────────────┐
         │              │ INCIDENTE_LIQUIDACION│
         │              ├─────────────────────┤
         │              │ ID_INCIDENTE FK     │
         │              │ ID_LIQUIDACION FK   │
         │              │ NUMERO_CUOTA        │
         │              │ VALOR_DESCUENTO     │
         │              └─────────────────────┘
         │                        ▲
         │                        │ N:1
         ▼                        │
┌─────────────────┐               │
│   INCIDENTES    │───────────────┘
├─────────────────┤
│ ID_INCIDENTE PK │
│ ID_PROPIEDAD FK │
│ ID_CONTRATO_M FK│
│ COSTO_INCIDENTE │
│ ESTADO          │
│ ESTADO_PAGO     │
└─────────────────┘
```

## Reglas de Negocio

### RB1: Filtrado de Incidentes por Propiedad

**Regla**: El modal "Seleccionar Incidentes" DEBE mostrar únicamente los incidentes asociados a la propiedad de la liquidación que se está editando.

**Implementación**: 
1. Obtener `ID_PROPIEDAD` desde `CONTRATOS_MANDATOS` usando `ID_CONTRATO_M` de la liquidación
2. Filtrar consulta SQL con `WHERE i.ID_PROPIEDAD = %s`

### RB2: Selección Múltiple

**Regla**: El usuario puede seleccionar múltiples incidentes de una vez en el modal.

**Implementación**: 
- Checkbox en cada fila de incidente
- Acumulación de selecciones en estado `seleccion_incidentes_seleccionados`
- Cálculo total de descuentos

### RB3: Edición Concurrente

**Regla**: Última escritura con notificación.

**Implementación**:
- No se implementa bloqueo pesimista
- Al guardar, se sobrescriben los datos anteriores
- Opcionalmente: comparar timestamps para notificar cambios

### RB4: Cardinalidad 1:N

**Regla**: Una liquidación puede tener múltiples incidentes asociados.

**Implementación**:
- Tabla intermedia `INCIDENTE_LIQUIDACION`
- Relación N:M resuelta a 1:N desde la perspectiva de liquidación

## Validaciones

| Entidad | Campo | Validación | Error Message |
|---------|-------|------------|---------------|
| Liquidación | VALOR_INCIDENTES | >= 0 | "El valor de incidentes no puede ser negativo" |
| Liquidación | OBSERVACIONES | Longitud <= 1000 | "Las observaciones no pueden exceder 1000 caracteres" |
| Incidente | ESTADO | IN ('Aprobado', 'En Reparacion', 'Finalizado') | "Estado no válido para asociación" |
| Incidente | ESTADO_PAGO | != 'Pagado' | "El incidente ya está pagado" |
| IncidenteLiquidación | VALOR_DESCUENTO | > 0 | "El valor del descuento debe ser mayor a 0" |