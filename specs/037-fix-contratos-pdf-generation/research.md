# Research: Fix Contratos PDF Generation

**Date**: 2026-07-08
**Feature**: 037-fix-contratos-pdf-generation

## R-001: Causa Raíz del Error de Columna

**Decision**: Ejecutar migración para agregar `RESPONSABLE_DEPOSITO_ID` a ambas tablas de contratos.

**Rationale**: El error `column cm.responsable_deposito_id does not exist` se origina en `servicio_contratos.py:925` cuando ejecuta un `LEFT JOIN ASESORES` usando una columna que no existe en la tabla `CONTRATOS_MANDATOS`.

**Análisis de la Consulta Defectuosa**:

```sql
-- Línea 925: JOIN con columna inexistente
LEFT JOIN ASESORES r ON cm.RESPONSABLE_DEPOSITO_ID = r.ID_ASESOR

-- La columna RESPONSABLE_DEPOSITO_ID no existe en CONTRATOS_MANDATOS
-- porque la migración nunca fue ejecutada
```

**Por qué PostgreSQL falla**: La migración `migration_campos_extra_contratos.sql` define la columna `RESPONSABLE_DEPOSITO_ID INTEGER` en `CONTRATOS_MANDATOS`, pero nunca fue ejecutada contra la base de datos de producción.

**Alternatives Considered**:
1. Eliminar el JOIN — Rechazado: el campo es necesario para mostrar el responsable del depósito
2. Hacer el JOIN opcional con COALESCE — Rechazado: solamente pospone el problema real
3. **Ejecutar la migración** — Seleccionado: solución correcta y alineada con la arquitectura

## R-002: Migración Incompleta para Arrendamientos

**Decision**: Actualizar la migración para agregar `RESPONSABLE_DEPOSITO_ID` a `CONTRATOS_ARRENDAMIENTOS`.

**Rationale**: El repositorio `repositorio_contrato_arrendamiento_postgres.py` usa `RESPONSABLE_DEPOSITO_ID` en:
- INSERT (línea 33): `ENLACE_VIDEO, RESPONSABLE_DEPOSITO_ID,`
- UPDATE (línea 395): `RESPONSABLE_DEPOSITO_ID = %s,`
- SELECT (línea 495): `responsable_deposito_id=row_dict.get("responsable_deposito_id")`

Pero la migración original solo agrega `ENLACE_VIDEO` a `CONTRATOS_ARRENDAMIENTOS`, no `RESPONSABLE_DEPOSITO_ID`.

**Impacto sin fix**: Los intentos de INSERT/UPDATE en arrendamientos fallarán con el mismo error de columna inexistente.

**Alternatives Considered**:
1. Remover las referencias del repositorio — Rechazado: el campo es funcional y necesario
2. Crear una segunda migración — Rechazado: más limpio actualizar la existente
3. **Actualizar la migración original** — Seleccionado: solución integral

## R-003: Flujo de Datos del Pipeline de PDF

**Decision**: Documentar el flujo completo para identificar todos los puntos de fallo.

**Rationale**: Understanding the data flow helps identify all potential failure points and validates that the fix addresses the root cause.

**Data Flow**:
```
1. Frontend: tarjeta_contrato.py → on_click → PDFState.generar_contrato_mandato_elite()
2. State: pdf_state.py → _get_datos_contrato_mandato(contrato_id)
3. Service: servicio_contratos.py → obtener_detalle_contrato_ui(contrato_id, "Mandato")
4. Query: SQL con JOIN a ASESORES usando RESPONSABLE_DEPOSITO_ID ← FAILS HERE
5. Transform: _sanitize_data_dict() → clean HTML entities
6. Template: ContratoMandatoElite.build() → ReportLab flowables
7. Generate: ReportLabGenerator.generate() → PDF file
8. Download: /api/pdf/download/{filename} → browser
```

**Failure Point**: Step 4 (SQL query) fails because column doesn't exist.

**Post-Fix Validation**: Steps 1-8 must complete without errors for Mandato, Arrendamiento, and Paz y Salvo.

## R-004: Estrategia de Manejo de Errores

**Decision**: Implementar manejo de errores amigables en `pdf_state.py`.

**Rationale**: Los usuarios actualmente ven errores técnicos de PostgreSQL como "column cm.responsable_deposito_id does not exist". La constitución del proyecto requiere UI profesional.

**Implementation**:
```python
# En pdf_state.py, envolver generación de PDF en try/except
try:
    # Generar PDF
except Exception as e:
    _log.error(f"Error generando PDF: {e}")
    yield rx.toast("Error al generar el PDF. Intente nuevamente.", duration=5000)
```

**Alternatives Considered**:
1. Mantener errores técnicos — Rechazado: mala experiencia de usuario
2. Modal con detalles del error — Rechazado: demasiado complejo para este fix
3. **Toast con mensaje amigable + log técnico** — Seleccionado: balance correcto

## R-005: Validación de No Regresión

**Decision**: Verificar Paz y Salvo después del fix.

**Rationale**: El fix modifica la migración y el manejo de errores. Paz y Salvo usa un pipeline diferente (CertificadoTemplate) pero comparte la misma capa de servicios.

**Módulos a Verificar**:
1. **Contrato Mandato**: Generar PDF completo con datos del contrato
2. **Contrato Arrendamiento**: Generar PDF completo con datos del contrato
3. **Paz y Salvo**: Generar certificado para contrato inactivo

**Criterio de Éxito**: Los 3 tipos de PDF se generan correctamente sin errores.

## R-006: Orden de Ejecución

**Decision**: Ejecutar migración antes de cualquier cambio de código.

**Rationale**: La migración es la causa raíz. Sin ella, ningún fix de código funcionará.

**Execution Order**:
1. Actualizar migración para agregar `RESPONSABLE_DEPOSITO_ID` a `CONTRATOS_ARRENDAMIENTOS`
2. Ejecutar migración contra la base de datos
3. Implementar manejo de errores amigables en UI
4. Verificar generación de PDFs (Mandato + Arrendamiento + Paz y Salvo)
