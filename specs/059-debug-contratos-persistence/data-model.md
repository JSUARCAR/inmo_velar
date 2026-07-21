# Data Model: Contratos Module Persistence Audit

**Date**: 2026-07-21
**Feature**: 059-debug-contratos-persistence

## Entity: ContratoMandato

**Table**: `CONTRATOS_MANDATOS`
**Entity file**: `src/dominio/entidades/contrato_mandato.py`

### Fields with Persistence Status

| Field | Entity Attr | DB Column | INSERT | UPDATE | READ | Status |
|-------|-------------|-----------|--------|--------|------|--------|
| id_contrato_m | id_contrato_m | ID_CONTRATO_M | ✅ | WHERE | ✅ | OK |
| id_propiedad | id_propiedad | ID_PROPIEDAD | ✅ | ✅ | ✅ | OK |
| id_propietario | id_propietario | ID_PROPIETARIO | ✅ | ✅ | ✅ | OK |
| id_asesor | id_asesor | ID_ASESOR | ✅ | ✅ | ✅ | OK |
| fecha_inicio | fecha_inicio_contrato_m | FECHA_INICIO_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| fecha_fin | fecha_fin_contrato_m | FECHA_FIN_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| duracion | duracion_contrato_m | DURACION_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| canon | canon_mandato | CANON_MANDATO | ✅ | ✅ | ✅ | OK |
| comision % | comision_porcentaje_contrato_m | COMISION_PORCENTAJE_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| iva | iva_contrato_m | IVA_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| estado | estado_contrato_m | ESTADO_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| motivo_cancelacion | motivo_cancelacion | MOTIVO_CANCELACION | ✅ | ✅ | ✅ | OK |
| alerta_vencimiento | alerta_vencimiento_contrato_m | ALERTA_VENCIMIENTO_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| fecha_renovacion | fecha_renovacion_contrato_m | FECHA_RENOVACION_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| fecha_pago | fecha_pago | FECHA_PAGO | ✅ | ✅ | ✅ | OK |
| grupo_operativo | grupo_operativo | GRUPO_OPERATIVO | ✅ | ✅ | ✅ | OK |
| banco_propietario | banco_propietario | BANCO_PROPIETARIO | ✅ | ✅ | ✅ | OK |
| numero_cuenta | numero_cuenta_propietario | NUMERO_CUENTA_PROPIETARIO | ✅ | ✅ | ✅ | OK |
| tipo_cuenta | tipo_cuenta | TIPO_CUENTA | ✅ | ✅ | ✅ | OK |
| consignatario | consignatario | CONSIGNATARIO | ✅ | ✅ | ❌ | **BUG** |
| documento_consignatario | documento_consignatario | DOCUMENTO_CONSIGNATARIO | ✅ | ✅ | ❌ | **BUG** |
| enlace_video | enlace_video | ENLACE_VIDEO | ✅ | ❌ | ❌ | **BUG** |
| created_at | created_at | CREATED_AT | auto | — | ✅ | OK |
| updated_at | updated_at | UPDATED_AT | auto | auto | ✅ | OK |

### Bugs Identified

**BUG #1 — UPDATE missing ENLACE_VIDEO**
- Location: `repositorio_contrato_mandato_postgres.py:actualizar()` line 281-305
- Fix: Add `ENLACE_VIDEO = %s` to SET clause, add `contrato.enlace_video` to parameter tuple

**BUG #2 — READ missing uppercase fallback**
- Location: `repositorio_contrato_mandato_postgres.py:_row_to_entity()` lines 402-404
- Fix: Change to `row_dict.get("consignatario") or row_dict.get("CONSIGNATARIO")` pattern

## Entity: ContratoArrendamiento

**Table**: `CONTRATOS_ARRENDAMIENTOS`
**Entity file**: `src/dominio/entidades/contrato_arrendamiento.py`

### Fields with Persistence Status

| Field | Entity Attr | DB Column | INSERT | UPDATE | READ | Status |
|-------|-------------|-----------|--------|--------|------|--------|
| id_contrato_a | id_contrato_a | ID_CONTRATO_A | ✅ | WHERE | ✅ | OK |
| id_propiedad | id_propiedad | ID_PROPIEDAD | ✅ | ✅ | ✅ | OK |
| id_arrendatario | id_arrendatario | ID_ARRENDATARIO | ✅ | ✅ | ✅ | OK |
| id_codeudor | id_codeudor | ID_CODEUDOR | ✅ | ✅ | ✅ | OK |
| fecha_inicio | fecha_inicio_contrato_a | FECHA_INICIO_CONTRATO_A | ✅ | ✅ | ✅ | OK |
| fecha_fin | fecha_fin_contrato_a | FECHA_FIN_CONTRATO_A | ✅ | ✅ | ✅ | OK |
| duracion | duracion_contrato_a | DURACION_CONTRATO_A | ✅ | ✅ | ✅ | OK |
| canon | canon_arrendamiento | CANON_ARRENDAMIENTO | ✅ | ✅ | ✅ | OK |
| deposito | deposito | DEPOSITO | ✅ | ✅ | ✅ | OK |
| fecha_pago | fecha_pago | FECHA_PAGO | ✅ | ✅ | ✅ | OK |
| grupo_operativo | grupo_operativo | GRUPO_OPERATIVO | ✅ | ✅ | ✅ | OK |
| alerta_ipc | alerta_ipc | ALERTA_IPC | ✅ | ✅ | ✅ | OK |
| id_seguro | id_seguro | ID_SEGURO | ✅ | ✅ | ✅ | OK |
| nombre_seguro | nombre_seguro | NOMBRE_SEGURO | ✅ | ✅ | ✅ | OK |
| porcentaje_seguro | porcentaje_seguro | PORCENTAJE_SEGURO | ✅ | ✅ | ✅ | OK |
| comision % | comision_porcentaje_contrato_m | COMISION_PORCENTAJE_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| id_contrato_m | id_contrato_m | ID_CONTRATO_M | ✅ | ✅ | ✅ | OK |
| direccion_propiedad | direccion_propiedad | DIRECCION_PROPIEDAD | ✅ | ✅ | ✅ | OK |
| enlace_video | enlace_video | ENLACE_VIDEO | ✅ | ✅ | ✅ | OK |
| responsable_deposito | responsable_deposito_id | RESPONSABLE_DEPOSITO_ID | ✅ | ✅ | ✅ | OK |

**Arrendamiento Status**: All fields persist correctly. No bugs found.

## Relationships

```
CONTRATOS_MANDATOS (1) ←── (N) CONTRATOS_ARRENDAMIENTOS
    via ID_CONTRATO_M FK

CONTRATOS_MANDATOS (N) ──→ (1) PROPIEDADES
    via ID_PROPIEDAD FK

CONTRATOS_MANDATOS (N) ──→ (1) PROPIETARIOS
    via ID_PROPIETARIO FK

CONTRATOS_ARRENDAMIENTOS (N) ──→ (1) PERSONAS (arrendatario)
    via ID_ARRENDATARIO FK

CONTRATOS_ARRENDAMIENTOS (N) ──→ (1) ASESORES (responsable_deposito)
    via RESPONSABLE_DEPOSITO_ID FK
```
