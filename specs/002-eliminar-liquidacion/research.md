# Research: Eliminar Liquidación de Propietario

**Date**: 2026-06-30 | **Feature**: 002-eliminar-liquidacion

## R1: Soft Delete Pattern in Codebase

**Decision**: Use boolean-based soft delete with `ELIMINADA` column (BOOLEAN DEFAULT FALSE)

**Rationale**: The codebase consistently uses boolean/integer soft delete for all major entities:
- `USUARIOS.ESTADO_USUARIO` (BOOLEAN) - `eliminar()` sets to FALSE
- `PERSONAS.ESTADO_REGISTRO` (BOOLEAN) - `inactivar()` sets to FALSE
- `PROPIEDADES.ESTADO_REGISTRO` (INTEGER 1/0) - `desactivar_propiedad()` sets to 0
- `PROVEEDORES.ESTADO_REGISTRO` (INTEGER 1/0) - `eliminar()` sets to FALSE

**Alternatives considered**:
- Physical DELETE: Rejected - financial data requires permanent retention
- Status-based (ESTADO_LIQUIDACION = 'Eliminada'): Rejected - would conflict with existing state machine and CHECK constraint
- Separate audit table: Rejected - adds unnecessary complexity; existing AUDITORIA_CAMBIOS suffices

**Pattern for LIQUIDACIONES**:
```python
# Repository method
def eliminar(self, id_liquidacion: int, usuario_sistema: str) -> None:
    cursor.execute(f"""
        UPDATE LIQUIDACIONES SET
            ELIMINADA = TRUE,
            UPDATED_AT = {placeholder},
            UPDATED_BY = {placeholder}
        WHERE ID_LIQUIDACION = {placeholder} AND ELIMINADA = FALSE
    """, (datetime.now().isoformat(), usuario_sistema, id_liquidacion))
```

## R2: Audit Trail Strategy

**Decision**: Application-level audit via `RepositorioAuditoria` + `RepositorioAuditoriaPostgres`

**Rationale**: The personas module (closest pattern) uses application-level audit:
- `servicio_personas.py` calls `_auditar_accion()` which writes to AUDITORIA_CAMBIOS
- Database triggers exist but only track specific columns (ESTADO_USUARIO, ESTADO_REGISTRO)
- Application-level gives more control over the audit record format

**Audit Record Structure**:
```
TABLA: 'LIQUIDACIONES'
ID_REGISTRO: <id_liquidacion>
TIPO_OPERACION: 'DELETE'
CAMPO_MODIFICADO: 'ELIMINADA'
VALOR_ANTERIOR: 'FALSE'
VALOR_NUEVO: 'TRUE'
USUARIO: <usuario_sistema>
FECHA_CAMBIO: <timestamp>
MOTIVO_CAMBIO: 'Eliminación de liquidación - estado anterior: <estado>'
```

**Alternatives considered**:
- Database trigger only: Rejected - trigger only tracks specific columns, not full context
- Custom audit table: Rejected - AUDITORIA_CAMBIOS already exists and is used system-wide
- No audit: Rejected - violates FR-006 and compliance requirements

## R3: Query Filtering for Soft-Deleted Records

**Decision**: Add `AND ELIMINADA = FALSE` (or equivalent) to all existing queries

**Rationale**: Existing patterns show:
- Personas: `solo_activos=True` parameter default, appends `p.ESTADO_REGISTRO = TRUE`
- Propiedades: `solo_activas=True` parameter default, appends `p.ESTADO_REGISTRO = TRUE`
- Proveedores: Hardcoded `WHERE ESTADO_REGISTRO = TRUE` in `listar()`

**Queries to update in `repositorio_liquidacion_postgres.py`**:
1. `listar_todas()` - line ~307: Add `AND l.ELIMINADA = FALSE`
2. `listar_por_contrato()` - line ~294: Add `AND ELIMINADA = FALSE`
3. `obtener_por_id()` - line ~239: No change needed (returns entity with eliminada field)
4. `obtener_por_contrato_y_periodo()` - line ~255: Add `AND ELIMINADA = FALSE`
5. `listar_por_propietario_y_periodo()` - line ~838: Add `AND l.ELIMINADA = FALSE`
6. `listar_agrupadas_por_propietario_paginado()` - line ~883: Add `AND l.ELIMINADA = FALSE`
7. `contar_con_filtros()` - Add `AND ELIMINADA = FALSE`
8. `obtener_datos_para_pdf()` - line ~1111: Add `AND l.ELIMINADA = FALSE`
9. `obtener_consolidado_propietario()` - line ~1246: Add `AND l.ELIMINADA = FALSE`
10. All `cancelar_por_propietario_y_periodo()` type queries: Add `AND ELIMINADA = FALSE`

**Pattern**: Follow personas pattern with optional `solo_activas` parameter, but default to True.

## R4: Permission System Integration

**Decision**: Register new action "ELIMINAR" for module "Liquidaciones" in PERMISOS table

**Rationale**: Existing permission system uses:
- `PERMISOS` table with `MODULO`, `ACCION` columns
- `ROL_PERMISOS` junction table
- `AuthState.check_action(module, action)` for UI checks
- `AuthState.backend_check_action(module, action)` for backend checks

**Registration**:
```sql
INSERT INTO PERMISOS (MODULO, RUTA, ACCION, DESCRIPCION, CATEGORIA)
VALUES ('Liquidaciones', '/liquidaciones', 'ELIMINAR', 'Eliminar liquidaciones', 'Gestión');
```

**UI Pattern** (from existing code):
```python
rx.cond(
    (liq["estado"] != "Pagada") & AuthState.check_action("Liquidaciones", "ELIMINAR"),
    rx.tooltip(
        rx.icon_button(rx.icon("trash-2", size=18), ...),
        content="Eliminar liquidación",
    ),
    rx.box(),
)
```

## R5: Confirmation Dialog Pattern

**Decision**: Follow existing `cancel_modal.py` pattern with checkbox instead of text area

**Rationale**: The cancel modal pattern is well-established:
- `rx.dialog.root` with `open=State.show_cancel_modal`
- State variables: `show_X_modal`, `X_motivo`, `liquidacion_id_for_action`
- Open handler: Sets ID, resets fields, opens modal
- Close handler: Resets all fields
- Confirm handler: Validates, calls service, closes, reloads, toasts

**Key difference**: Cancel modal uses `rx.text_area` for motivo. Delete dialog uses `rx.checkbox` for confirmation.

**Dialog Content** (from spec clarification):
- Summary: propietario, dirección, período, neto a pagar, estado
- Financial breakdown: ingresos, comisión, IVA, gastos detail
- Checkbox: "Confirmo que deseo eliminar esta liquidación permanentemente"
- Warning: "Esta acción es irreversible"

## R6: Document Orphaning Strategy

**Decision**: Mark documents as orphans (preserve but unlink from liquidation)

**Rationale**: Spec clarification agreed on orphaning over deletion:
- Financial documents may be needed for audits
- Orphaning preserves data while removing broken references
- Documents can be manually cleaned up later if needed

**Implementation**: In the same transaction as liquidation deletion:
```python
# Unlink documents
cursor.execute(f"""
    UPDATE DOCUMENTOS SET
        ID_ENTIDAD_REFERENCIA = NULL,
        UPDATED_AT = {placeholder}
    WHERE TABLA_REFERENCIA = 'LIQUIDACIONES' AND ID_ENTIDAD_REFERENCIA = {placeholder}
""", (datetime.now().isoformat(), id_liquidacion))
```

**Risk**: If DOCUMENTOS table has NOT NULL constraint on ID_ENTIDAD_REFERENCIA, this will fail. Need to verify schema.
