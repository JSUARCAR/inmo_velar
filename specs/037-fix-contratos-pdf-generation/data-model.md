# Data Model: Fix Contratos PDF Generation

**Date**: 2026-07-08
**Feature**: 037-fix-contratos-pdf-generation

## Entity: CONTRATOS_MANDATOS

### Current Schema (pre-fix)
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| ID_CONTRATO_M | INTEGER | PK | Auto-generated |
| ID_PROPIEDAD | INTEGER | FK → PROPIEDADES | Required |
| ID_MANDATARIO | INTEGER | FK → MANDATARIOS | Required |
| FECHA_INICIO_CONTRATO_M | DATE | Required | |
| FECHA_FIN_CONTRATO_M | DATE | Required | |
| DURACION_CONTRATO_M | VARCHAR(50) | Required | |
| COMISION_PORCENTAJE | DECIMAL(5,2) | Required | |
| ESTADO_CONTRATO_M | VARCHAR(20) | Required | ACTIVO/INACTIVO |
| CREATED_AT | TIMESTAMP | Required | |
| CREATED_BY | VARCHAR(100) | Required | |

### Target Schema (post-fix)
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| ID_CONTRATO_M | INTEGER | PK | Auto-generated |
| ID_PROPIEDAD | INTEGER | FK → PROPIEDADES | Required |
| ID_MANDATARIO | INTEGER | FK → MANDATARIOS | Required |
| FECHA_INICIO_CONTRATO_M | DATE | Required | |
| FECHA_FIN_CONTRATO_M | DATE | Required | |
| DURACION_CONTRATO_M | VARCHAR(50) | Required | |
| COMISION_PORCENTAJE | DECIMAL(5,2) | Required | |
| ESTADO_CONTRATO_M | VARCHAR(20) | Required | ACTIVO/INACTIVO |
| ENLACE_VIDEO | TEXT | Nullable | **NEW** |
| RESPONSABLE_DEPOSITO_ID | INTEGER | Nullable | **NEW** - FK → ASESORES |
| CREATED_AT | TIMESTAMP | Required | |
| CREATED_BY | VARCHAR(100) | Required | |

**Constraints to Add**:
```sql
ALTER TABLE CONTRATOS_MANDATOS
ADD CONSTRAINT fk_mandatos_responsable_deposito
FOREIGN KEY (RESPONSABLE_DEPOSITO_ID)
REFERENCES ASESORES(ID_ASESOR)
ON DELETE SET NULL;
```

## Entity: CONTRATOS_ARRENDAMIENTOS

### Current Schema (pre-fix)
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| ID_CONTRATO_A | INTEGER | PK | Auto-generated |
| ID_PROPIEDAD | INTEGER | FK → PROPIEDADES | Required |
| ID_ARRENDATARIO | INTEGER | FK → ARRENDATARIOS | Required |
| ID_CODEUDOR | INTEGER | FK → CODEUDORES | Nullable |
| FECHA_INICIO_CONTRATO_A | DATE | Required | |
| FECHA_FIN_CONTRATO_A | DATE | Required | |
| DURACION_CONTRATO_A | VARCHAR(50) | Required | |
| CANON_ARRENDAMIENTO | DECIMAL(12,2) | Required | |
| DEPOSITO | DECIMAL(12,2) | Required | |
| ESTADO_CONTRATO_A | VARCHAR(20) | Required | ACTIVO/INACTIVO |
| CREATED_AT | TIMESTAMP | Required | |
| CREATED_BY | VARCHAR(100) | Required | |

### Target Schema (post-fix)
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| ID_CONTRATO_A | INTEGER | PK | Auto-generated |
| ID_PROPIEDAD | INTEGER | FK → PROPIEDADES | Required |
| ID_ARRENDATARIO | INTEGER | FK → ARRENDATARIOS | Required |
| ID_CODEUDOR | INTEGER | FK → CODEUDORES | Nullable |
| FECHA_INICIO_CONTRATO_A | DATE | Required | |
| FECHA_FIN_CONTRATO_A | DATE | Required | |
| DURACION_CONTRATO_A | VARCHAR(50) | Required | |
| CANON_ARRENDAMIENTO | DECIMAL(12,2) | Required | |
| DEPOSITO | DECIMAL(12,2) | Required | |
| ESTADO_CONTRATO_A | VARCHAR(20) | Required | ACTIVO/INACTIVO |
| ENLACE_VIDEO | TEXT | Nullable | **NEW** |
| RESPONSABLE_DEPOSITO_ID | INTEGER | Nullable | **NEW** - FK → ASESORES |
| MOTIVO_CANCELACION | TEXT | Nullable | Existing |
| ALERTA_VENCIMIENTO_CONTRATO_A | DATE | Nullable | Existing |
| FECHA_RENOVACION_CONTRATO_A | DATE | Nullable | Existing |
| FECHA_PAGO | VARCHAR(10) | Nullable | Existing |
| CREATED_AT | TIMESTAMP | Required | |
| CREATED_BY | VARCHAR(100) | Required | |

**Constraints to Add**:
```sql
ALTER TABLE CONTRATOS_ARRENDAMIENTOS
ADD CONSTRAINT fk_arrendamientos_responsable_deposito
FOREIGN KEY (RESPONSABLE_DEPOSITO_ID)
REFERENCES ASESORES(ID_ASESOR)
ON DELETE SET NULL;
```

## Entity: ASESORES (referenced)

### Existing Schema
| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| ID_ASESOR | INTEGER | PK | Auto-generated |
| NOMBRE_COMPLETO | VARCHAR(200) | Required | |
| ... | ... | ... | Other fields |

**Relationship**: Both `CONTRATOS_MANDATOS.RESPONSABLE_DEPOSITO_ID` and `CONTRATOS_ARRENDAMIENTOS.RESPONSABLE_DEPOSITO_ID` reference `ASESORES.ID_ASESOR`.

## Migration Script

### Updated `migration_campos_extra_contratos.sql`
```sql
-- Migración para añadir campos de enlace_video y responsable_deposito a contratos

-- 1. Añadir campos a CONTRATOS_MANDATOS
ALTER TABLE CONTRATOS_MANDATOS
ADD COLUMN ENLACE_VIDEO TEXT,
ADD COLUMN RESPONSABLE_DEPOSITO_ID INTEGER;

-- 2. Añadir foreign key para responsable_deposito_id hacia ASESORES
ALTER TABLE CONTRATOS_MANDATOS
ADD CONSTRAINT fk_mandatos_responsable_deposito
FOREIGN KEY (RESPONSABLE_DEPOSITO_ID)
REFERENCES ASESORES(ID_ASESOR)
ON DELETE SET NULL;

-- 3. Añadir campos a CONTRATOS_ARRENDAMIENTOS
ALTER TABLE CONTRATOS_ARRENDAMIENTOS
ADD COLUMN ENLACE_VIDEO TEXT,
ADD COLUMN RESPONSABLE_DEPOSITO_ID INTEGER;

-- 4. Añadir foreign key para responsable_deposito_id hacia ASESORES
ALTER TABLE CONTRATOS_ARRENDAMIENTOS
ADD CONSTRAINT fk_arrendamientos_responsable_deposito
FOREIGN KEY (RESPONSABLE_DEPOSITO_ID)
REFERENCES ASESORES(ID_ASESOR)
ON DELETE SET NULL;
```

## Query Impact Analysis

### Affected Queries (servicio_contratos.py)

| Line | Method | Query | Uses RESPONSABLE_DEPOSITO_ID |
|------|--------|-------|------------------------------|
| 925 | obtener_detalle_contrato_ui | Mandato SELECT | ✅ Yes - JOIN to ASESORES |
| 1407 | listar_mandatos | Mandato SELECT | ✅ Yes - SELECT column |
| 1415 | listar_mandatos | Mandato SELECT | ✅ Yes - JOIN to ASESORES |

### Affected Queries (repositorio_contrato_arrendamiento_postgres.py)

| Line | Method | Query | Uses RESPONSABLE_DEPOSITO_ID |
|------|--------|-------|------------------------------|
| 33 | crear | INSERT | ✅ Yes - INSERT column |
| 395 | actualizar | UPDATE | ✅ Yes - UPDATE column |
| 495 | obtener_por_id | SELECT | ✅ Yes - SELECT column |
