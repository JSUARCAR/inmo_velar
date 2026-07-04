# Research: Reversar Pago de Liquidación

**Date**: 2026-06-30
**Feature**: 001-reversar-pago

## R1: Existing Reversal Pattern Analysis

**Decision**: Extend the existing `reversar()` method pattern (Aprobada→En Proceso) to create a new `reversar_pago()` method (Pagada→Aprobada).

**Rationale**: The codebase already has a well-established reversal pattern in `RepositorioLiquidacionPostgres.reversar()` (line 589). The new `reversar_pago()` follows the identical structure: state check → UPDATE with cleanup → commit. This minimizes risk and cognitive load for developers.

**Alternatives considered**:
- Generic `cambiar_estado()` method: Rejected because it would lose the specific business logic (payment field cleanup) that makes reversar_pago unique.
- Event-driven approach: Rejected as over-engineering for a single state transition within an existing module.

## R2: Idempotency Implementation

**Decision**: Implement idempotency via state check — if `ESTADO_LIQUIDACION != 'Pagada'`, return silently without error.

**Rationale**: The spec (FR-009, clarified) requires silent no-op for already-reversed payments. This is the standard pattern in financial systems. The existing `reversar()` already uses a WHERE clause with state check (`AND ESTADO_LIQUIDACION = 'Aprobada'`), so `cursor.rowcount == 0` would normally raise ValueError. For idempotency, we simply catch this case and return success instead.

**Alternatives considered**:
- Database-level idempotency key: Rejected as unnecessary complexity for this use case.
- Application-level lock: Rejected as overkill — the state check is sufficient.

## R3: Audit Trail for Motivo

**Decision**: Insert a separate AUDITORIA_CAMBIOS record with `CAMPO_MODIFICADO = 'MOTIVO_REVERSION'` and `VALOR_NUEVO = motivo_text`.

**Rationale**: The existing trigger on LIQUIDACIONES captures field changes automatically, but doesn't capture the motivo. The AUDITORIA_CAMBIOS table structure supports this pattern (tabla, id_registro, tipo_operacion, campo_modificado, valor_anterior, valor_nuevo, usuario). This avoids modifying database triggers.

**Alternatives considered**:
- Modify the trigger to accept motivo: Rejected because it requires DB migration and the trigger function is shared across all tables.
- Create a new table: Rejected as unnecessary schema change when the existing table supports the pattern.

## R4: Bulk Reversal Selectivity

**Decision**: In bulk reversal, iterate through liquidations, check state, and only reverse those in 'Pagada' state. Track reversed/ignored counts and return both.

**Rationale**: The spec (clarified) requires selective behavior — reverse only 'Pagada' liquidations, ignore others. This matches the existing `reversar_masivamente()` pattern (line 634) but adds state filtering.

**Alternatives considered**:
- Transactional all-or-nothing: Rejected per spec clarification.
- SQL bulk UPDATE with WHERE IN: Rejected because we need per-record audit trail for each reversal.

## R5: Permission Registration

**Decision**: Register "REVERSAR_PAGO" action in the Liquidaciones module permissions. The existing `AuthState.check_action("Liquidaciones", "REVERSAR_PAGO")` pattern handles this automatically.

**Rationale**: The permission system already supports per-module action checks. Adding a new action string follows the same pattern as existing CREAR, EDITAR, APROBAR, PAGAR, CANCELAR actions.

**Alternatives considered**:
- Reuse existing REVERSAR permission: Rejected because the spec explicitly names "REVERSAR_PAGO" as a distinct permission (reversing approval vs. reversing payment are different operations).

## R6: Confirmation Dialog Component

**Decision**: Create a new `reverse_pago_confirm_dialog.py` component following the existing `reverse_confirm_dialog.py` pattern, with added fields for motivo input and impact summary.

**Rationale**: The existing dialog is minimal (53 lines). The new dialog needs: propietario, dirección, período, monto, fecha_pago, and a required motivo field. Creating a separate component keeps concerns isolated.

**Alternatives considered**:
- Extend existing dialog with conditional content: Rejected because it would make the existing dialog complex and violate SRP.
