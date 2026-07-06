# Research: fix-floating-label

## Decision 1: Triggering the Floating State for Date Pickers

**Decision**: Pass an `always_float` argument internally or detect `type == 'date'` to enforce the floating state for labels associated with these inputs.

**Rationale**: When an HTML `<input type="date">` is rendered, browsers (like Chrome) display a native placeholder (e.g., `dd/mm/aaaa`) even if the `value` is empty. Reflex's current implementation relies on `has_value = (value != "") & (value != None)`. Since `value` is empty initially, `has_value` is `False`, causing the label to position itself centrally. This results in the label overlapping with the native date placeholder. By explicitly recognizing date inputs (or allowing a flag), we can apply `label_with_value_style` by default to avoid overlap.

**Alternatives considered**: 
- Trying to use raw CSS `:not(:placeholder-shown)` or `:focus-within`. This is complex because Reflex's `floating_input` heavily relies on inline styles and `rx.cond` based on state variables (`value`), rather than raw CSS pseudoclasses. Adapting the whole component to use CSS classes instead of inline styles would be a much larger refactor with potential regressions for the rest of the application.
