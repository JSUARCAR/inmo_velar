# Research: Estandarización de Filtros Avanzados con Floating Labels

**Date**: 2026-07-05
**Feature**: 017-advanced-filters-floating-labels

## Research Questions

### R1: Component Architecture - Existing Floating Label Support

**Question**: Do the existing `floating_input` and `floating_select` components already implement the Floating Label pattern correctly?

**Finding**: YES. Both components in `shared/floating_label.py` implement CSS-only floating labels:
- `floating_input` (line 14): Uses absolute-positioned `<label>` with `html_for`, transitions via `FL_TRANSITION` token, conditional styles for focused/value/error states
- `floating_select` (line 113): Same pattern applied to `rx.select.root` with trigger placeholder

**Decision**: Use existing components as-is. No modifications needed.

**Alternatives Considered**:
- Building new floating label components: Rejected - existing implementation is correct and follows Material Design easing curve
- Using third-party floating label library: Rejected - adds unnecessary dependency

---

### R2: Neumorphic Wrapper Compatibility

**Question**: Do `neuro_floating_input` and `neuro_floating_select` in `neuro_elements.py` properly wrap the floating label components?

**Finding**: YES. Both wrappers (lines 605-674) simply delegate to the base floating components:
```python
def neuro_floating_input(...):
    return floating_input(label=label, value=value, on_change=on_change, ...)

def neuro_floating_select(...):
    return floating_select(label=label, value=value, on_change=on_change, options=options, ...)
```

**Decision**: Use `neuro_floating_input`/`neuro_floating_select` as the primary API for all filter migrations. They inherit `NEU_INPUT_STYLE` and `NEU_SELECT_STYLE` from the base components.

---

### R3: Migration Pattern - neuro_input → neuro_floating_input

**Question**: What is the exact API difference between `neuro_input` (current) and `neuro_floating_input` (target)?

**Finding**:
- `neuro_input`: Takes `placeholder` as primary label mechanism
- `neuro_floating_input`: Takes `label` as primary visible text, `value`/`on_change` for state binding

**Migration Pattern**:
```python
# BEFORE:
neuro_input(
    placeholder="Buscar por nombre...",
    value=PersonasState.search_query,
    on_change=PersonasState.set_search_query,
)

# AFTER:
neuro_floating_input(
    label="Buscar por nombre",
    value=PersonasState.search_query,
    on_change=PersonasState.set_search_query,
)
```

**Decision**: Straightforward API swap. Label text = former placeholder text (trimmed of "...").

---

### R4: Migration Pattern - neuro_select_root → neuro_floating_select

**Question**: How does `neuro_select_root` differ from `neuro_floating_select`?

**Finding**:
- `neuro_select_root`: Uses `rx.select.root(rx.select.trigger(placeholder=...), rx.select.content(...))` with manual option rendering
- `neuro_floating_select`: Takes `options: list[dict[str, str]]` and handles rendering internally

**Migration Pattern**:
```python
# BEFORE:
neuro_select_root(
    placeholder="Estado",
    value=State.filtro_estado,
    on_change=State.set_filtro_estado,
    options=[{"label": "Activo", "value": "activo"}, ...],
)

# AFTER:
neuro_floating_select(
    label="Estado",
    value=State.filtro_estado,
    on_change=State.set_filtro_estado,
    options=[{"label": "Activo", "value": "activo"}, ...],
)
```

**Decision**: Same API pattern. The `neuro_floating_select` already accepts `options` as `list[dict[str, str]]`.

---

### R5: Raw Component Migration (Seguros, Saldos a Favor, Reportes)

**Question**: What changes are needed for modules using raw `rx.input`/`rx.select`?

**Finding**: These modules need:
1. Import addition: `from ...neuro_elements import neuro_floating_input, neuro_floating_select`
2. Component swap: `rx.input(placeholder=...)` → `neuro_floating_input(label=..., value=..., on_change=...)`
3. Component swap: `rx.select(placeholder=...)` → `neuro_floating_select(label=..., value=..., on_change=..., options=[...])`

**Decision**: Import + component swap. No state changes needed since raw components already use `value`/`on_change`.

---

### R6: State Variable Compatibility

**Question**: Do existing state variables need modification for floating labels?

**Finding**: NO. Floating label components use the same `value`/`on_change` interface as current components. The floating label behavior is purely CSS-driven (label position based on `has_value` check via `rx.cond`).

**Decision**: Zero state changes. All existing `State.filter_*` variables remain unchanged.

---

### R7: Date Input Fields

**Question**: How should `type="date"` inputs be handled?

**Finding**: `neuro_floating_input` accepts `**kwargs` which passes through to `rx.input`. The `type="date"` prop will be passed through correctly. The floating label will work with date inputs the same way as text inputs.

**Decision**: Use `neuro_floating_input(label="Fecha Desde", type="date", value=..., on_change=...)`.

---

### R8: Switch/Checkbox Fields

**Question**: Should `neuro_switch` and `rx.checkbox` fields also get floating labels?

**Finding**: NO. Switches and checkboxes already have visible labels next to them (e.g., "Sin arriendo", "Mostrar inactivos"). Floating labels are designed for text/select inputs where the placeholder disappears. Switches/checkboxes don't have this problem.

**Decision**: Leave switches/checkboxes unchanged. Only migrate text inputs, date inputs, and select dropdowns.

---

## Summary of Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Component API | Use `neuro_floating_input`/`neuro_floating_select` | Existing, tested, consistent with neumorphic design |
| State changes | None | Floating label is CSS-only, same value/on_change interface |
| Raw module migration | Import + component swap | Seguros, Saldos a Favor, Reportes need import additions |
| Date inputs | `neuro_floating_input(type="date")` | Pass-through via **kwargs |
| Switches/checkboxes | Unchanged | Already have visible labels |
| Placeholder strategy | Use `label` param, remove `placeholder` | Labels provide visible text permanently |
