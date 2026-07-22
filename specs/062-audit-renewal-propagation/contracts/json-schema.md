# JSON Output Schema: Auditoría de Propagación de Renovaciones

**Feature**: 062-audit-renewal-propagation
**Date**: 2026-07-22
**Status**: Complete

## Overview

This document defines the JSON output schema for the audit report. The structure is flexible but must include all required fields.

## Complete Schema

```json
{
  "metadata": {
    "fecha_ejecucion": "2026-07-22T14:30:25.123456",
    "duracion_segundos": 12.5,
    "total_renovaciones": 15,
    "total_inconsistencias": 8,
    "total_fallas_diseno": 4,
    "version_script": "1.0.0",
    "entorno": "staging"
  },
  "resumen_ejecutivo": {
    "total_renovaciones": 15,
    "inconsistencias_encontradas": 8,
    "porcentaje_inconsistencias": 53.33,
    "estado_sincronizacion": "INCONSISTENTE",
    "contratos_ok": 7,
    "contratos_inconsistentes": 8,
    "contratos_error": 0,
    "monto_total_discrepancia": 1500000.00
  },
  "inconsistencias": [
    {
      "contrato_id": "uuid-1234",
      "contrato_codigo": "CA-2024-001",
      "tipo": "LIQUIDACION",
      "entidad_afectada": "LIQUIDACION",
      "entidad_id": "uuid-5678",
      "canon_esperado": 1500000.00,
      "canon_encontrado": 1200000.00,
      "diferencia": -300000.00,
      "fecha_registro": "2026-07-22T14:30:25.123456",
      "periodo": "2026-08",
      "causa_raiz": "Liquidación generada antes de la renovación del contrato",
      "severidad": "ALTA"
    }
  ],
  "analisis_codigo": [
    {
      "archivo": "src/aplicacion/servicios/servicio_contrato_arrendamiento.py",
      "linea_inicio": 278,
      "linea_fin": 467,
      "funcion_clase": "sincronizar_cascada_contrato",
      "descripcion": "Función de sincronización en cascada",
      "problema": "Solo actualiza Mandato y Propiedad, no Liquidaciones ni Recaudos",
      "impacto": "Inconsistencias en datos financieros cuando se renueva un contrato",
      "recomendacion": "Agregar lógica para actualizar liquidaciones y recaudos futuros",
      "categoria": "SINCRONIZACION"
    }
  ],
  "recomendaciones": [
    {
      "prioridad": 1,
      "titulo": "Implementar sincronización de liquidaciones en cascada",
      "descripcion": "Modificar servicio_contrato_arrendamiento.py para actualizar liquidaciones futuras al renovar contrato",
      "categoria": "CORRECCION_INMEDIATA",
      "esfuerzo_estimado": "MEDIO",
      "impacto_estimado": "ALTO",
      "archivos_afectados": [
        "src/aplicacion/servicios/servicio_contrato_arrendamiento.py",
        "src/aplicacion/servicios/servicio_financiero.py"
      ]
    }
  ],
  "contratos_procesados": [
    {
      "contrato_id": "uuid-1234",
      "contrato_codigo": "CA-2024-001",
      "arrendatario_nombre": "Juan Pérez",
      "mandato_id": "uuid-mandato-1",
      "propiedad_id": "uuid-propiedad-1",
      "canon_anterior": 1200000.00,
      "canon_nuevo": 1500000.00,
      "fecha_renovacion": "2026-07-15T10:30:00",
      "fecha_inicio_renovacion": "2026-08-01",
      "estado": "ACTIVA"
    }
  ],
  "historial_verificacion": {
    "liquidaciones_verificadas": 50,
    "liquidaciones_modificadas": 0,
    "recaudos_verificados": 75,
    "recaudos_modificados": 0,
    "integridad": "PRESERVADA",
    "detalles": []
  }
}
```

## Required Fields by Section

### metadata (FR-010)
- `fecha_ejecucion`: ISO 8601 datetime
- `duracion_segundos`: float
- `total_renovaciones`: int
- `total_inconsistencias`: int
- `total_fallas_diseno`: int
- `version_script`: string
- `entorno`: string (staging/produccion)

### resumen_ejecutivo (FR-011)
- `total_renovaciones`: int
- `inconsistencias_encontradas`: int
- `porcentaje_inconsistencias`: float (0-100)
- `estado_sincronizacion`: enum (OK/INCONSISTENTE/CRITICO)
- `contratos_ok`: int
- `contratos_inconsistentes`: int
- `contratos_error`: int
- `monto_total_discrepancia`: decimal

### inconsistencias (FR-012)
- `contrato_id`: string (UUID)
- `contrato_codigo`: string
- `tipo`: enum (LIQUIDACION/RECAUDO/MANDATO/PROPIEDAD)
- `entidad_afectada`: string
- `entidad_id`: string (UUID)
- `canon_esperado`: decimal
- `canon_encontrado`: decimal
- `diferencia`: decimal
- `fecha_registro`: ISO 8601 datetime
- `periodo`: string (YYYY-MM)
- `causa_raiz`: string
- `severidad`: enum (CRITICA/ALTA/MEDIA/BAJA)

### analisis_codigo (FR-013)
- `archivo`: string (relative path)
- `linea_inicio`: int
- `linea_fin`: int (optional)
- `funcion_clase`: string
- `descripcion`: string
- `problema`: string
- `impacto`: string
- `recomendacion`: string
- `categoria`: enum (SINCRONIZACION/VALIDACION/MANEJO_ERRORES)

### recomendaciones (FR-014)
- `prioridad`: int (1 = highest)
- `titulo`: string
- `descripcion`: string
- `categoria`: enum (CORRECCION_INMEDIATA/MEJORA/PREVENCION)
- `esfuerzo_estimado`: enum (BAJO/MEDIO/ALTO)
- `impacto_estimado`: enum (BAJO/MEDIO/ALTO)
- `archivos_afectados`: array of strings

## Validation Rules

1. **JSON Validity**: Output must be valid JSON parseable by `json.loads()`
2. **Required Sections**: All 6 sections must be present
3. **Required Fields**: All required fields must be non-null
4. **Enum Values**: Must match defined enumerations
5. **Decimal Precision**: 2 decimal places for monetary values
6. **Datetime Format**: ISO 8601 with timezone

## Error Output Schema

If script fails, output error JSON:

```json
{
  "error": {
    "tipo": "ERROR_CONEXION_BD",
    "mensaje": "No se pudo conectar a la base de datos",
    "detalle": "Connection refused on host:port",
    "timestamp": "2026-07-22T14:30:25.123456"
  }
}
```
