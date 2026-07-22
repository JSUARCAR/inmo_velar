# Contract: Reglas de Validación de Sincronización

**Date**: 2026-07-22
**Feature**: 061-reverse-engineer-contracts-sync

## Overview

Este contrato define las reglas de validación que el script de auditoría debe verificar. Cada regla tiene un identificador único que se usa en el informe de resultados.

## Validation Rules

### VR-001: Cascada de Renovación - Canon
**Descripción**: Cuando se renueva un contrato de arrendamiento y se modifica el canon, el sistema debe actualizar correctamente el Canon de Mandato y el Canon Estimado de la Propiedad.

**Criterio de Éxito**:
- DADO un contrato de arrendamiento activo con canon = X
- CUANDO se renueva el contrato con canon_nuevo = Y
- ENTONCES el mandato asociado debe tener canon_mandato = Y
- Y la propiedad debe tener canon_arrendamiento_estimado = Y

**Severidad**: CRÍTICA

---

### VR-002: Cascada de Renovación - Historial
**Descripción**: Cada renovación debe crear un registro en RENOVACIONES_CONTRATOS con los valores correctos.

**Criterio de Éxito**:
- DADO un contrato de arrendamiento activo
- CUANDO se renueva el contrato
- ENTONCES se crea un registro en RENOVACIONES_CONTRATOS con:
  - canon_anterior = valor antes de renovación
  - canon_nuevo = valor después de renovación
  - porcentaje_incremento = ((canon_nuevo - canon_anterior) / canon_anterior) * 100

**Severidad**: ALTA

---

### VR-003: Cascada de Renovación - Fechas
**Descripción**: La fecha_fin del mandato debe sincronizarse con la nueva fecha_fin del arrendamiento.

**Criterio de Éxito**:
- DADO un contrato de arrendamiento activo con fecha_fin = F1
- CUANDO se renueva con duración de D meses
- ENTONCES la nueva fecha_fin debe ser F1 + D meses
- Y el mandato debe tener la misma fecha_fin

**Severidad**: ALTA

---

### VR-004: Preservación de Históricos - Liquidaciones
**Descripción**: Las liquidaciones generadas ANTES de una renovación NO deben ser modificadas.

**Criterio de Éxito**:
- DADO una liquidación generada en período P con canon_bruto = X
- CUANDO se renueva el contrato después del período P
- ENTONCES la liquidación del período P debe mantener canon_bruto = X

**Severidad**: CRÍTICA

---

### VR-005: Preservación de Históricos - Recaudos
**Descripción**: Los recaudos generados ANTES de una renovación NO deben ser modificados.

**Criterio de Éxito**:
- DADO un recaudo generado en período P con valor_total = X
- CUANDO se renueva el contrato después del período P
- ENTONCES el recaudo del período P debe mantener valor_total = X

**Severidad**: CRÍTICA

---

### VR-006: Generación con Canon Actualizado - Liquidaciones
**Descripción**: Las liquidaciones generadas DESPUÉS de una renovación deben usar el nuevo canon.

**Criterio de Éxito**:
- DADO un contrato renovado con canon_nuevo = Y
- CUANDO se genera la liquidación del período P (después de renovación)
- ENTONCES el canon_bruto de la liquidación debe ser Y

**Severidad**: ALTA

---

### VR-007: Generación con Canon Actualizado - Recaudos
**Descripción**: Los recaudos generados DESPUÉS de una renovación deben usar el nuevo canon.

**Criterio de Éxito**:
- DADO un contrato renovado con canon_nuevo = Y
- CUANDO se genera el recaudo del período P (después de renovación)
- ENTONCES el valor_total del recaudo debe ser Y

**Severidad**: ALTA

---

### VR-008: Consistencia entre Módulos
**Descripción**: No deben existir discrepancias de datos entre Contratos, Liquidaciones y Recaudos.

**Criterio de Éxito**:
- DADO un contrato activo con su mandato y propiedad asociada
- CUANDO se consultan los valores de canon en los tres módulos
- ENTONCES todos deben mostrar el mismo valor actualizado

**Severidad**: ALTA

---

### VR-009: Ausencia de Actualizaciones Retroactivas
**Descripción**: No debe existir ningún proceso que modifique registros históricos después de su creación.

**Criterio de Éxito**:
- DADO el código fuente del sistema
- CUANDO se analizan todos los procesos de actualización
- ENTONCES no debe existir ningún proceso que modifique:
  - canon_bruto de liquidaciones ya generadas
  - valor_total de recaudos ya generados

**Severidad**: CRÍTICA

---

### VR-010: Respeto de Fecha de Vigencia
**Descripción**: La fecha de vigencia de la renovación debe ser respetada por todos los procesos dependientes.

**Criterio de Éxito**:
- DADO una renovación ejecutada el día D
- CUANDO se generan liquidaciones para períodos antes y después de D
- ENTONCES:
  - Períodos ANTES de D deben usar el canon anterior
  - Períodos DESPUÉS de D deben usar el canon nuevo

**Severidad**: ALTA

---

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| CRÍTICA | Impacto directo en integridad financiera | Bloquea deploy |
| ALTA | Impacto significativo en datos | Requiere fix antes de merge |
| MEDIA | Impacto menor o edge case | Puede diferirse |
| BAJA | Mejora cosmética o documentación | Opcional |

## Report Format

El informe de auditoría debe seguir este formato:

```
========================================
INFORME DE AUDITORÍA - SINCRONIZACIÓN
Fecha: YYYY-MM-DD HH:MM:SS
========================================

VR-001: Cascada de Renovación - Canon
Estado: PASS/FAIL
Detalles: [valores esperados vs encontrados]

VR-002: Cascada de Renovación - Historial
Estado: PASS/FAIL
Detalles: [valores esperados vs encontrados]

...

========================================
RESUMEN
========================================
Total de reglas: 10
Pasaron: X
Fallaron: Y
Tasa de éxito: Z%
========================================
```
