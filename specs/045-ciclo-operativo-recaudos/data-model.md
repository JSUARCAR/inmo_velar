# Data Model: Ciclo Operativo en Módulo Recaudos

**Date**: 2026-07-11

## Entidades Involucradas

### RECAUDOS (existente — sin cambios en schema)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID_RECAUDO | INTEGER PK | Identificador único del recaudo |
| ID_CONTRATO_A | INTEGER FK | FK → CONTRATOS_ARRENDAMIENTOS |
| FECHA_PAGO | TEXT | Fecha de pago del recaudo |
| VALOR_TOTAL | INTEGER | Valor total del pago |
| METODO_PAGO | TEXT | Método de pago |
| ESTADO_RECAUDO | TEXT | Estado: Pendiente/Aplicado/Reversado/Vencido |

### CONTRATOS_ARRENDAMIENTOS (existente — sin cambios)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID_CONTRATO_A | INTEGER PK | PK del contrato de arrendamiento |
| ID_PROPIEDAD | INTEGER FK | FK → PROPIEDADES |
| GRUPO_OPERATIVO | INTEGER | Grupo operativo del arrendamiento (independiente del mandato) |

### CONTRATOS_MANDATOS (existente — sin cambios)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID_CONTRATO_M | INTEGER PK | PK del contrato de mandato |
| ID_PROPIEDAD | INTEGER FK | FK → PROPIEDADES |
| GRUPO_OPERATIVO | INTEGER | **Campo fuente del ciclo operativo** (Grupo 1-5) |
| ESTADO_CONTRATO_M | TEXT | Estado del contrato (ACTIVO/INACTIVO) |
| FECHA_INICIO | DATE | Fecha de inicio del contrato |

### PROPIEDADES (existente — sin cambios)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID_PROPIEDAD | INTEGER PK | PK de la propiedad |
| DIRECCION_PROPIEDAD | TEXT | Dirección de la propiedad |

## Cadena de Relación (Nueva)

```
RECAUDOS (ID_CONTRATO_A)
    → CONTRATOS_ARRENDAMIENTOS (ID_CONTRATO_A → ID_PROPIEDAD)
        → PROPIEDADES (ID_PROPIEDAD)
        → CONTRATOS_MANDATOS (ID_PROPIEDAD, ESTADO_CONTRATO_M = 'ACTIVO')
            → GRUPO_OPERATIVO ← Este es el valor que se muestra
```

**NOTA**: La entidad RECAUDO no se modifica. El campo `ciclo_operativo` es un valor derivado de la consulta, no un atributo de dominio del recaudo.

## DTO: RecaudoDTO (modificado)

Se agrega un campo al DTO existente:

```python
class RecaudoDTO(BaseModel):
    # ... campos existentes ...
    ciclo_operativo: str = ""  # NUEVO: "Grupo 1", "Grupo 2", etc. o "-"
```

**Valor por defecto**: `""` (string vacío) — se formatea como `"-"` en la UI cuando no hay datos.

## Mapeo de Consulta SQL → Dict de Salida

```python
# Campo SQL nuevo en SELECT:
"cm.GRUPO_OPERATIVO"

# Mapeo en dict de salida:
"ciclo_operativo": f"Grupo {row['GRUPO_OPERATIVO']}" if row.get("GRUPO_OPERATIVO") else "-"
```

## Reglas de Formato

| Valor en DB | Valor mostrado en UI |
|-------------|---------------------|
| 1 | Grupo 1 |
| 2 | Grupo 2 |
| 3 | Grupo 3 |
| 4 | Grupo 4 |
| 5 | Grupo 5 |
| NULL o 0 | - |

## Restricciones de Integridad

- El campo `GRUPO_OPERATIVO` en `CONTRATOS_MANDATOS` es un entero positivo (1-5).
- No se permite NULL en `GRUPO_OPERATIVO` para contratos con estado ACTIVO.
- La consulta debe filtrar `ESTADO_CONTRATO_M = 'ACTIVO'` para evitar duplicados.
