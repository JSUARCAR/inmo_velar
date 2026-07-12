# Data Model: Reordenar Columnas Tabla Liquidaciones

**Date**: 2026-07-11

## Entidades Afectadas

Ninguna. Este cambio es puramente de presentación y no modifica el modelo de datos.

## Entidades en Lectura (sin cambios)

### Liquidación (vista individual)

| Campo | Tipo | Column ID | ¿Afectado? |
|-------|------|-----------|------------|
| ID | int | `id` | Solo reordenamiento |
| Periodo | str | `periodo` | Solo reordenamiento |
| Propiedad | str | `contrato` | **ELIMINADO de la tabla** |
| Ciclo Operativo | str | `grupo_operativo` | Solo reordenamiento |
| Canon | str | `canon` | Solo reordenamiento |
| IVA Comisión | str | `iva_comision` | **MOVIDO** de pos. 13 a pos. 5 |
| Otros Ingresos | str | `otros_ingresos` | Solo reordenamiento |
| Gastos Administración | str | `gastos_administracion` | Solo reordenamiento |
| Gastos Servicios | str | `gastos_servicios` | Solo reordenamiento |
| Gastos Reparaciones | str | `gastos_reparaciones` | Solo reordenamiento |
| Valor Incidentes | str | `valor_incidentes` | Solo reordenamiento |
| Pago Predial | str | `pago_predial` | Solo reordenamiento |
| Otros Egresos | str | `otros_egresos` | Solo reordenamiento |
| Neto a Pagar | str | `neto` | Solo reordenamiento |
| Estado Recaudo | str | `estado_recaudo` | Solo reordenamiento |
| Estado | str | `estado` | Solo reordenamiento |
| Acciones | component | N/A | Solo reordenamiento |

### Liquidación Agrupada (vista agrupada)

| Campo | Tipo | Column ID | ¿Afectado? |
|-------|------|-----------|------------|
| Periodo | str | `periodo` | Solo reordenamiento |
| Propietario | str | `propietario` | Solo reordenamiento |
| Propiedades | str | `cantidad_propiedades` | Solo reordenamiento |
| Canon Total | str | `canon` | Solo reordenamiento |
| Total IVA Com. | str | `iva_comision` | **MOVIDO** después de Canon Total |
| Total Otros Ing. | str | `otros_ingresos` | Solo reordenamiento |
| Total Gastos Adm. | str | `gastos_administracion` | Solo reordenamiento |
| Total Gastos Serv. | str | `gastos_servicios` | Solo reordenamiento |
| Total Gastos Rep. | str | `gastos_reparaciones` | Solo reordenamiento |
| Total V. Incid. | str | `valor_incidentes` | Solo reordenamiento |
| Total Predial | str | `pago_predial` | Solo reordenamiento |
| Total Otros Egr. | str | `otros_egresos` | Solo reordenamiento |
| Neto Total | str | `neto` | Solo reordenamiento |
| Estado Recaudo | str | `estado_recaudo` | Solo reordenamiento |
| Estado | str | `estado` | Solo reordenamiento |
| Acciones | component | N/A | Solo reordenamiento |

## Reglas de Validación

Sin cambios. Todas las reglas existentes se mantienen.

## Transiciones de Estado

Sin cambios. No se modifica ningún flujo de estado.
