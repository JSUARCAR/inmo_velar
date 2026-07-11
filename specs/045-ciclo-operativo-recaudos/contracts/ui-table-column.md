# UI Contract: Columna Ciclo Operativo — Tabla Recaudos

**Date**: 2026-07-11

## Column Definition

| Property | Value |
|----------|-------|
| Header | "Ciclo Operativo" |
| Position | Después de "Pago Contrato" (índice 3, 0-based) |
| Sortable | Sí |
| Sort key | `ciclo_operativo` |
| Width | Auto (se ajusta al contenido: "Grupo N") |
| Hidden on mobile | No (visible en todos los viewports) |

## Data Format

```json
{
  "ciclo_operativo": "Grupo 1"
}
```

**Valores válidos**: `"Grupo 1"`, `"Grupo 2"`, `"Grupo 3"`, `"Grupo 4"`, `"Grupo 5"`
**Valor de ausencia**: `"-"`
**Tipo**: String formateado (no numérico)

## Rendering Rules

| Condition | Rendering |
|-----------|-----------|
| `ciclo_operativo` es "Grupo N" | Texto normal, alineado a la izquierda |
| `ciclo_operativo` es "-" | Texto en color gris claro (muted) |
| `ciclo_operativo` es vacío | Se trata como "-" |

## Sort Behavior

- Orden alfanumérico: "Grupo 1" < "Grupo 2" < "Grupo 3" < ... < "Grupo 5" < "-"
- Los valores "-" se ordenan al final tanto en asc como en desc
