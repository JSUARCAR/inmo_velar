# Specification: Fix Contratos PDF Generation

**Feature**: Fix PDF generation errors in the Contratos module
**ID**: 037-fix-contratos-pdf-generation
**Created**: 2026-07-08
**Status**: Draft

---

## Executive Summary

The Contratos module currently fails to generate PDF documents for both Contratos de Mandato (Mandate Contracts) and Contratos de Arrendamiento (Lease Contracts). This specification defines the requirements to diagnose and fix the root cause of these failures, while ensuring the Paz y Salvo (Clearance Certificate) functionality remains operational without regressions.

---

## Problem Statement

Users attempting to generate PDF contracts from the Contratos module encounter a PostgreSQL error that prevents successful PDF creation.

### Root Cause Identified

**Error Message**: `column cm.responsable_deposito_id does not exist LINE 42: LEFT JOIN ASESORES r ON cm.RESPONSABLE_DEPOSITO_...`

**Root Cause**: The database table `CONTRATOS_MANDATOS` is missing the column `RESPONSABLE_DEPOSITO_ID`. The migration file `migration_campos_extra_contratos.sql` defines this column but was never executed in the production database. The query in `servicio_contratos.py:925` references this non-existent column when retrieving contract details for PDF generation.

**Affected Query Location**: `src/aplicacion/servicios/servicio_contratos.py` line 925:
```sql
LEFT JOIN ASESORES r ON cm.RESPONSABLE_DEPOSITO_ID = r.ID_ASESOR
```

**Impact**: Both Mandato and Arrendamiento PDF generation fail at the data retrieval step before any PDF rendering occurs.

### System Should Generate

- **Contrato de Mandato**: Administrative mandate contract between property owner and real estate company
- **Contrato de Arrendamiento**: Lease agreement between property owner, tenant, and co-debtor
- **Paz y Salvo**: Clearance certificate confirming contract termination and no outstanding obligations

The PDF generation pipeline involves frontend event handlers, data retrieval from PostgreSQL, data transformation, template-based PDF generation using ReportLab, and file download via API.

---

## User Scenarios & Testing

### Primary User Flows

**Scenario 1: Generate Mandate Contract PDF**
1. User navigates to Contratos module
2. User locates a Mandato contract in the list or grid view
3. User clicks the "Contrato Oficial" button (purple file-check icon)
4. System retrieves contract data from PostgreSQL
5. System transforms data to PDF template format
6. System generates PDF using ContratoMandatoElite template
7. System triggers browser download of the generated PDF
8. User receives PDF file with all required legal clauses and signatures

**Scenario 2: Generate Lease Contract PDF**
1. User navigates to Contratos module
2. User locates an Arrendamiento contract in the list or grid view
3. User clicks the "Contrato Oficial" button (purple file-check icon)
4. System retrieves contract data from PostgreSQL
5. System transforms data to PDF template format
6. System generates PDF using ContratoArrendamientoElite template
7. System triggers browser download of the generated PDF
8. User receives PDF file with all 25 legal clauses and signature blocks

**Scenario 3: Generate Paz y Salvo Certificate**
1. User navigates to Contratos module
2. User locates an inactive (terminated) contract
3. User clicks the "Generar Paz y Salvo" button (teal shield-check icon)
4. System retrieves contract data from PostgreSQL
5. System generates certificate PDF using CertificadoTemplate
6. System triggers browser download of the generated PDF
7. User receives clearance certificate with owner, tenant, property details

### Edge Cases

- Contract with missing optional fields (e.g., no co-debtor, missing phone number)
- Contract with special characters in names or addresses (e.g., accented characters, ampersands)
- Contract with very long address or description text
- Contract where property data is incomplete in database
- Network interruption during PDF generation
- Concurrent PDF generation requests for the same contract

### Test Scenarios

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| T1 | Generate Mandato PDF with complete data | PDF downloads successfully with all clauses |
| T2 | Generate Arrendamiento PDF with complete data | PDF downloads successfully with all 25 clauses |
| T3 | Generate Paz y Salvo for active contract | Certificate generates with correct data |
| T4 | Generate Paz y Salvo for inactive contract | Certificate generates with correct data |
| T5 | Generate PDF with missing co-debtor data | PDF generates with graceful fallback values |
| T6 | Generate PDF with special characters in names | PDF renders characters correctly without errors |
| T7 | Generate PDF when database is unavailable | User sees clear error message |
| T8 | Generate PDF for contract with zero canon value | Validation handles edge case gracefully |

---

## Functional Requirements

### FR-01: PDF Generation for Mandato Contracts
**Priority**: Critical
**Description**: The system shall generate PDF documents for Contratos de Mandato containing all required legal clauses, party information, property details, commission terms, and signature blocks.

**Acceptance Criteria**:
- PDF is generated using ContratoMandatoElite template
- All 15+ legal clauses are included with correct placeholder replacement
- Mandante (owner) information is displayed correctly
- Mandatario (company) information is displayed correctly
- Property address and registration details are included
- Commission percentage and payment terms are included
- Signature blocks for both parties are rendered
- PDF file downloads successfully to user's browser

### FR-02: PDF Generation for Arrendamiento Contracts
**Priority**: Critical
**Description**: The system shall generate PDF documents for Contratos de Arrendamiento containing all 25 legal clauses, party information, property details, lease terms, and signature blocks.

**Acceptance Criteria**:
- PDF is generated using ContratoArrendamientoElite template
- All 25 legal clauses are included with correct placeholder replacement
- Arrendador (owner) information is displayed correctly
- Arrendatario (tenant) information is displayed correctly
- Codeudor (co-debtor) information is included when present
- Property address and registration details are included
- Canon de arrendamiento (rent amount) is formatted correctly in text and numbers
- Duration and date fields are calculated and displayed correctly
- Signature blocks for all parties are rendered
- PDF file downloads successfully to user's browser

### FR-03: Paz y Salvo Certificate Generation
**Priority**: High
**Description**: The system shall generate clearance certificate PDFs for terminated contracts without introducing regressions from Contratos module fixes.

**Acceptance Criteria**:
- Certificate is generated using CertificadoTemplate
- Owner (propietario) name and document number are displayed
- Tenant (arrendatario) name and document number are displayed
- Property address is included
- Contract reference number is included
- Certificate text confirms no outstanding obligations
- Representative legal signature block is included
- PDF file downloads successfully to user's browser
- Behavior is consistent for both active and inactive contracts per business rules

### FR-04: Data Retrieval and Transformation
**Priority**: Critical
**Description**: The system shall retrieve contract data from PostgreSQL and transform it to the format expected by PDF templates.

**Acceptance Criteria**:
- Contract data is fetched using existing service layer (ServicioContratos)
- All required fields for each template type are included in the transformation
- Missing optional fields have sensible default values
- Data types match template expectations (strings, numbers, dates)
- Company configuration data (logo, NIT, address) is included from ServicioConfiguracion

### FR-05: Error Handling and User Feedback
**Priority**: High
**Description**: The system shall provide clear error messages when PDF generation fails, and log sufficient detail for debugging.

**Acceptance Criteria**:
- Validation errors display specific missing field information
- PDF generation errors show user-friendly toast messages
- Backend logs include full stack traces for debugging
- ExpatError (XML parsing) errors are caught and reported with context
- Network/API errors during download are handled gracefully

### FR-06: Regression Prevention
**Priority**: High
**Description**: Fixes to Contratos PDF generation shall not break existing Paz y Salvo, Estado de Cuenta, or other PDF generation functionalities.

**Acceptance Criteria**:
- Paz y Salvo generation continues to work for all contract types
- Estado de Cuenta PDF generation is unaffected
- Recibo de Pago PDF generation is unaffected
- Batch ZIP generation for liquidaciones is unaffected
- All existing PDF types maintain their current behavior

---

## Key Entities

### ContratoMandato (Mandate Contract)
- **Purpose**: Administrative contract where property owner delegates property management to real estate company
- **Key Fields**: mandante (owner), inmueble (property), condiciones (terms), comision (commission %)
- **PDF Template**: ContratoMandatoElite

### ContratoArrendamiento (Lease Contract)
- **Purpose**: Standard lease agreement between owner, tenant, and co-debtor
- **Key Fields**: arrendador (owner), arrendatario (tenant), codeudor (co-debtor), inmueble (property), condiciones (terms)
- **PDF Template**: ContratoArrendamientoElite

### CertificadoPazYSalvo (Clearance Certificate)
- **Purpose**: Official document confirming contract termination and no outstanding obligations
- **Key Fields**: beneficiario (beneficiary), contenido (content text), firmante (signer)
- **PDF Template**: CertificadoTemplate

### PDF Generation Pipeline
- **Frontend**: Reflex event handlers in PDFState
- **Data Layer**: ServicioContratos + PostgreSQL repositories
- **Transformation**: Data mapping in _get_datos_contrato / _get_datos_contrato_mandato
- **PDF Engine**: ReportLab via BaseDocumentTemplate hierarchy
- **Download**: FastAPI endpoint /api/pdf/download/{filename}

---

## Assumptions

1. The PostgreSQL database contains valid contract data for the contracts being tested
2. The ReportLab library is properly installed and configured
3. The membrete (letterhead) image file exists at the expected path
4. The FastAPI PDF download endpoint is functioning correctly
5. The browser has network access to the API endpoint for downloading generated PDFs
6. Company configuration data (ServicioConfiguracion) is populated in the database
7. The existing template files (CLAUSULAS_TEXTO) contain valid HTML markup for ReportLab

---

## Success Criteria

### Quantitative Metrics
- PDF generation success rate: 100% for contracts with complete data
- PDF generation success rate: >95% for contracts with partial data (missing optional fields)
- PDF download success rate: 100% when PDF file is generated
- No increase in backend error logs for PDF-related operations
- No increase in ExpatError exceptions

### Qualitative Measures
- Generated PDFs contain all required legal clauses without missing content
- Placeholder values are replaced with actual data (no literal [PLACEHOLDER] text visible)
- PDF formatting is professional and matches expected layout
- User experience is smooth with appropriate success/error feedback
- Paz y Salvo functionality remains fully operational after fixes

---

## Clarifications

### Session 2026-07-08

- Q: Root cause identified: missing database column `RESPONSABLE_DEPOSITO_ID` in `CONTRATOS_MANDATOS` table. Migration exists but wasn't executed. → A: Ejecutar la migración `migration_campos_extra_contratos.sql` para agregar la columna faltante

- Q: Migration file is incomplete - it only adds `ENLACE_VIDEO` to `CONTRATOS_ARRENDAMIENTOS` but the repository code uses `RESPONSABLE_DEPOSITO_ID` in INSERT/UPDATE/SELECT for Arrendamiento contracts → A: Actualizar la migración para agregar `RESPONSABLE_DEPOSITO_ID INTEGER` a `CONTRATOS_ARRENDAMIENTOS` con FK a `ASESORES`

- Q: Error handling UX: user currently sees raw PostgreSQL errors → A: Mostrar mensajes amigables al usuario (ej: "Error al generar PDF") + log técnico detallado

- Q: Validation approach after fix → A: Verificación manual: generar 1 Mandato + 1 Arrendamiento + 1 Paz y Salvo

---

## Dependencies

- ReportLab PDF library
- num2words library (for number-to-text conversion)
- PostgreSQL database with contract data
- FastAPI backend with PDF download endpoint
- Reflex frontend framework
- Company configuration data in database

---

## Out of Scope

- Redesign of PDF templates or legal clause content
- Changes to the database schema or migrations
- New PDF document types
- PDF digital signature integration
- PDF encryption or password protection
- Batch PDF generation improvements
- Performance optimization of PDF generation
