# Refactor Propiedades Module to Use Standard Neuro Elements

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the propiedades module to use standard neuro_elements components, removing local definitions and fixing syntax errors.

**Architecture:** Replace local component definitions with imports from neuro_elements module, add missing imports, and fix syntax errors in modal_form_refactored.py.

**Tech Stack:** Python, Reflex, neuro_elements components

## Global Constraints

- Preserve all existing functionality
- Do not add comments unless requested
- Keep all existing imports and functionality intact
- Only change what's specified in the instructions

---

### Task 1: Refactor modal_form.py

**Files:**
- Modify: `src/presentacion_reflex/components/propiedades/modal_form.py`

**Interfaces:**
- Consumes: neuro_elements module (neuro_button, neuro_icon_action_button)
- Produces: Updated modal_form.py with standard components

- [ ] **Step 1: Remove local neuro_button definition**

Remove lines 25-31 (the local `neuro_button` function definition).

- [ ] **Step 2: Add import for neuro_icon_action_button**

Add to imports section:
```python
from src.presentacion_reflex.components.neuro_elements import neuro_button, neuro_icon_action_button
```

- [ ] **Step 3: Add tooltip_content to Cancel button**

Update line 677-679:
```python
neuro_button(
    "Cancelar",
    on_click=PropiedadesState.close_modal,
    tooltip_content="Cerrar formulario",
),
```

- [ ] **Step 4: Add tooltip_content to Anterior button**

Update line 682-685:
```python
neuro_button(
    "Anterior",
    on_click=PropiedadesState.prev_modal_step,
    tooltip_content="Ir al paso anterior",
),
```

- [ ] **Step 5: Add tooltip_content to Siguiente button**

Update line 689-695:
```python
neuro_button(
    rx.hstack(
        rx.text("Siguiente"),
        rx.icon("chevron-right", size=16),
    ),
    on_click=PropiedadesState.next_modal_step,
    tooltip_content="Ir al siguiente paso",
),
```

- [ ] **Step 6: Add tooltip_content to Guardar button**

Update line 697-706:
```python
neuro_button(
    rx.hstack(
        rx.text("Guardar Propiedad"),
        rx.icon("save", size=16),
    ),
    on_click=PropiedadesState.save_propiedad(
        PropiedadesState.form_data
    ),
    loading=PropiedadesState.is_loading,
    tooltip_content="Guardar los datos de la propiedad",
),
```

- [ ] **Step 7: Replace close icon button**

Replace line 642:
```python
# FROM:
rx.icon_button(rx.icon("x", size=20), variant="ghost", size="2")
# TO:
neuro_icon_action_button("x", tooltip_content="Cerrar", on_click=PropiedadesState.close_modal)
```

- [ ] **Step 8: Commit changes**

```bash
git add src/presentacion_reflex/components/propiedades/modal_form.py
git commit -m "refactor: use standard neuro_elements in modal_form.py"
```

### Task 2: Refactor property_card.py

**Files:**
- Modify: `src/presentacion_reflex/components/propiedades/property_card.py`

**Interfaces:**
- Consumes: neuro_elements module (neuro_button)
- Produces: Updated property_card.py with standard components

- [ ] **Step 1: Remove local neuro_icon_button definition**

Remove lines 30-36 (the local `neuro_icon_button` function definition).

- [ ] **Step 2: Add import for neuro_icon_action_button**

Update imports section:
```python
from src.presentacion_reflex.components.neuro_elements import neuro_button, neuro_icon_action_button
```

- [ ] **Step 3: Verify existing buttons already use tooltip_content**

Check lines 323-377 - they already use `tooltip_content` parameter, so no changes needed.

- [ ] **Step 4: Commit changes**

```bash
git add src/presentacion_reflex/components/propiedades/property_card.py
git commit -m "refactor: use standard neuro_elements in property_card.py"
```

### Task 3: Fix modal_form_refactored.py

**Files:**
- Modify: `src/presentacion_reflex/components/propiedades/modal_form_refactored.py`

**Interfaces:**
- Consumes: neuro_elements module, floating_label module
- Produces: Fixed modal_form_refactored.py with proper imports and syntax

- [ ] **Step 1: Add missing imports**

Add to imports section:
```python
from src.presentacion_reflex.components.shared.floating_label import floating_input, floating_select
from src.presentacion_reflex.components.neuro_elements import neuro_button
```

- [ ] **Step 2: Remove local component definitions**

Remove lines 21-82 (local definitions of `neuro_input`, `neuro_select_root`, `neuro_button`, `neuro_text_area`, `neuro_divider`).

- [ ] **Step 3: Fix extra commas after closing parentheses**

Fix syntax errors at lines:
- Line 103: Remove extra comma after closing parenthesis
- Line 116: Remove extra comma after closing parenthesis
- Line 141: Remove extra comma after closing parenthesis
- Line 157: Remove extra comma after closing parenthesis
- Line 197: Remove extra comma after closing parenthesis
- Line 224: Remove extra comma after closing parenthesis
- Line 244: Remove extra comma after closing parenthesis
- Line 262: Remove extra comma after closing parenthesis
- Line 273: Remove extra comma after closing parenthesis
- Line 288: Remove extra comma after closing parenthesis
- Line 311: Remove extra comma after closing parenthesis
- Line 322: Remove extra comma after closing parenthesis
- Line 333: Remove extra comma after closing parenthesis
- Line 375: Remove extra comma after closing parenthesis
- Line 390: Remove extra comma after closing parenthesis
- Line 425: Remove extra comma after closing parenthesis
- Line 442: Remove extra comma after closing parenthesis
- Line 471: Remove extra comma after closing parenthesis
- Line 487: Remove extra comma after closing parenthesis
- Line 513: Remove extra comma after closing parenthesis
- Line 531: Remove extra comma after closing parenthesis
- Line 552: Remove extra comma after closing parenthesis
- Line 568: Remove extra comma after closing parenthesis

- [ ] **Step 4: Commit changes**

```bash
git add src/presentacion_reflex/components/propiedades/modal_form_refactored.py
git commit -m "fix: resolve syntax errors and use standard neuro_elements in modal_form_refactored.py"
```

### Task 4: Verify empty_state.py and wizard_progress.py

**Files:**
- Read: `src/presentacion_reflex/components/propiedades/empty_state.py`
- Read: `src/presentacion_reflex/components/propiedades/wizard_progress.py`

**Interfaces:**
- Consumes: None
- Produces: Verification that no changes needed

- [ ] **Step 1: Review empty_state.py**

Check if any changes needed - file appears to use standard Reflex components, no local neuro_elements definitions.

- [ ] **Step 2: Review wizard_progress.py**

Check if any changes needed - file appears to use standard Reflex components, no local neuro_elements definitions.

- [ ] **Step 3: No changes needed**

These files don't require modifications.

### Task 5: Run Lint and Typecheck

**Files:**
- None (verification only)

**Interfaces:**
- Consumes: All modified files
- Produces: Verification that code is correct

- [ ] **Step 1: Run linting**

Run: `npm run lint` or appropriate linting command for Python

- [ ] **Step 2: Run typechecking**

Run: `npm run typecheck` or appropriate typechecking command for Python

- [ ] **Step 3: Verify all changes work together**

Ensure no import errors or syntax issues across all modified files.

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-07-05-refactor-propiedades-neuro-elements.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**