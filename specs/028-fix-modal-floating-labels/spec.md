# Specification: Fix Modal Floating Labels

## 1. Description
The user noticed that the floating label components (`neuro_floating_input` and `neuro_floating_select`) have only been fully implemented in the toolbars/filter bars, leaving the forms inside the Modals with legacy input styles. This causes visual bugs such as labels overlapping placeholders or text (e.g., in the "Nueva Persona" modal's "Número Documento" field) across multiple modules.

The goal is to update the forms inside the Modals across 14 modules to properly use the floating label components to ensure consistent Neumorphic UI design throughout the application.

## 2. Scope
The following modules have modals whose inputs need to be refactored to `neuro_floating_input` and `neuro_floating_select`:
- Personas
- Propiedades
- Contratos
- Liquidaciones
- Liquidación Asesores
- Recaudos
- Desocupaciones
- Incidentes
- Seguros
- Recibos Públicos
- Saldos a Favor
- Usuarios
- IPC/Incrementos
- Reportes

**In Scope:**
- Identifying all modal components (e.g. `modal_form` in `personas.py` or separate components) in the mentioned modules.
- Replacing legacy inputs and selects inside these modals with their floating equivalents.
- Ensuring `value` and `on_change` properties are correctly bound in the floating components.

**Out of Scope:**
- Backend logic changes.
- Changes to the filter bars (already done in previous spec).

## 3. Assumptions
- The floating label components `neuro_floating_input` and `neuro_floating_select` are fully functional and ready to be used inside modals.
- The state bindings for the modal forms are currently correct and just need to be adapted to the new UI components.

## 4. User Scenarios & Testing
**Scenario 1: Creating/Editing an Entity**
- **Given** a user is on the Personas module
- **When** they click "Nueva Persona" to open the creation modal
- **Then** all input fields in the modal should have the floating label style, without any text overlapping issues when interacting or entering data.

## 5. Functional Requirements
1. The modal forms across the 14 modules must utilize `neuro_floating_input` instead of `rx.input` or `neuro_input`.
2. The modal forms across the 14 modules must utilize `neuro_floating_select` instead of `rx.select` or `neuro_select_root`.
3. Labels must correctly transition and not overlap user input or placeholders.

## 6. Success Criteria
1. **Visual Consistency:** 100% of the modals in the listed 14 modules use the new floating components.
2. **Usability:** No visual overlap between labels and inputted text inside modal forms.
3. **Compilation:** The Reflex application successfully compiles (`reflex export --frontend-only --no-zip`) after the changes without missing argument errors.
