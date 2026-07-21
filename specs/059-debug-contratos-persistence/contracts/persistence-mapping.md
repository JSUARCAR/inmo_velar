# Persistence Mapping: Contratos Module

**Date**: 2026-07-21
**Feature**: 059-debug-contratos-persistence

This document maps every field in both contract forms to its full persistence path through the system.

## Contrato de Mandato — Full Field Mapping

### Datos del Contrato

| UI Label | Form Field | State Key | Entity Attr | Service Param | DB Column | Type |
|----------|-----------|-----------|-------------|---------------|-----------|------|
| Propiedad | propiedad_select | form_data["id_propiedad"] | id_propiedad | id_propiedad | ID_PROPIEDAD | INTEGER FK |
| Propietario | propietario_select | form_data["id_propietario"] | id_propietario | id_propietario | ID_PROPIETARIO | INTEGER FK |
| Asesor | asesor_select | form_data["id_asesor"] | id_asesor | id_asesor | ID_ASESOR | INTEGER FK |
| Fecha Inicio | fecha_inicio | form_data["fecha_inicio_contrato_m"] | fecha_inicio_contrato_m | fecha_inicio_contrato_m | FECHA_INICIO_CONTRATO_M | TEXT |
| Fecha Fin | fecha_fin | form_data["fecha_fin_contrato_m"] | fecha_fin_contrato_m | fecha_fin_contrato_m | FECHA_FIN_CONTRATO_M | TEXT |
| Duracion | duracion (readonly) | form_data["duracion_contrato_m"] | duracion_contrato_m | duracion_contrato_m | DURACION_CONTRATO_M | INTEGER |
| Canon Estimado | canon (readonly) | form_data["canon_mandato"] | canon_mandato | canon_mandato | CANON_MANDATO | NUMERIC |
| Comision % | comision | form_data["comision_porcentaje_contrato_m"] | comision_porcentaje_contrato_m | comision_porcentaje_contrato_m | COMISION_PORCENTAJE_CONTRATO_M | NUMERIC |
| IVA % | iva | form_data["iva_contrato_m"] | iva_contrato_m | iva_contrato_m | IVA_CONTRATO_M | NUMERIC |
| Fecha Pago | fecha_pago (readonly) | form_data["fecha_pago"] | fecha_pago | fecha_pago | FECHA_PAGO | TEXT |
| Grupo Operativo | grupo (readonly) | form_data["grupo_operativo"] | grupo_operativo | grupo_operativo | GRUPO_OPERATIVO | INTEGER |

### Información para Pagos

| UI Label | Form Field | State Key | Entity Attr | Service Param | DB Column | Type |
|----------|-----------|-----------|-------------|---------------|-----------|------|
| Banco | banco | form_data["banco_propietario"] | banco_propietario | banco_propietario | BANCO_PROPIETARIO | TEXT |
| Numero de Cuenta | numero_cuenta | form_data["numero_cuenta_propietario"] | numero_cuenta_propietario | numero_cuenta_propietario | NUMERO_CUENTA_PROPIETARIO | TEXT |
| Tipo de Cuenta | tipo_cuenta | form_data["tipo_cuenta"] | tipo_cuenta | tipo_cuenta | TIPO_CUENTA | TEXT |
| Nombre Consignatario | consignatario | form_data["consignatario"] | consignatario | consignatario | CONSIGNATARIO | TEXT |
| Documento Consignatario | documento_consignatario | form_data["documento_consignatario"] | documento_consignatario | documento_consignatario | DOCUMENTO_CONSIGNATARIO | TEXT |

### Recepción e Inventario

| UI Label | Form Field | State Key | Entity Attr | Service Param | DB Column | Type |
|----------|-----------|-----------|-------------|---------------|-----------|------|
| Enlace Video Recibo | enlace_video | form_data["enlace_video"] | enlace_video | enlace_video | ENLACE_VIDEO | TEXT |

**⚠️ BUG**: `ENLACE_VIDEO` missing from UPDATE query + missing uppercase fallback in READ

## Contrato de Arrendamiento — Full Field Mapping

### Datos del Contrato

| UI Label | Form Field | State Key | Entity Attr | Service Param | DB Column | Type |
|----------|-----------|-----------|-------------|---------------|-----------|------|
| Propiedad | propiedad_select | form_data["id_propiedad"] | id_propiedad | id_propiedad | ID_PROPIEDAD | INTEGER FK |
| Arrendatario | arrendatario_select | form_data["id_arrendatario"] | id_arrendatario | id_arrendatario | ID_ARRENDATARIO | INTEGER FK |
| Codeudor | codeudor_select | form_data["id_codeudor"] | id_codeudor | id_codeudor | ID_CODEUDOR | INTEGER FK |
| Fecha Inicio | fecha_inicio | form_data["fecha_inicio_contrato_a"] | fecha_inicio_contrato_a | fecha_inicio_contrato_a | FECHA_INICIO_CONTRATO_A | TEXT |
| Fecha Fin | fecha_fin | form_data["fecha_fin_contrato_a"] | fecha_fin_contrato_a | fecha_fin_contrato_a | FECHA_FIN_CONTRATO_A | TEXT |
| Duracion | duracion (readonly) | form_data["duracion_contrato_a"] | duracion_contrato_a | duracion_contrato_a | DURACION_CONTRATO_A | INTEGER |
| Canon Arriendo | canon | form_data["canon_arrendamiento"] | canon_arrendamiento | canon_arrendamiento | CANON_ARRENDAMIENTO | NUMERIC |
| Deposito | deposito | form_data["deposito"] | deposito | deposito | DEPOSITO | NUMERIC |
| Fecha Pago | fecha_pago | form_data["fecha_pago"] | fecha_pago | fecha_pago | FECHA_PAGO | TEXT |
| Grupo Operativo | grupo (readonly) | form_data["grupo_operativo"] | grupo_operativo | grupo_operativo | GRUPO_OPERATIVO | INTEGER |

### Recepción e Inventario

| UI Label | Form Field | State Key | Entity Attr | Service Param | DB Column | Type |
|----------|-----------|-----------|-------------|---------------|-----------|------|
| Enlace Video Entrega | enlace_video | form_data["enlace_video"] | enlace_video | enlace_video | ENLACE_VIDEO | TEXT |
| Responsable Deposito | responsable_select | form_data["responsable_deposito_id"] | responsable_deposito_id | responsable_deposito_id | RESPONSABLE_DEPOSITO_ID | INTEGER FK |

**Status**: All Arrendamiento fields persist correctly ✅
