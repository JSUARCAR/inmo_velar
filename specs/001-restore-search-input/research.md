# Research: Restore Search Input in Advanced Filters

## Decision Log

### D1: Search Input Location

**Decision**: Add search input inside `advanced_filter_bar` component (not in individual pages)

**Rationale**:
- The component already accepts search-related props (`search_placeholder`, `on_search`, `search_value`)
- All 7 module pages already pass these props correctly
- Single-point change ensures consistency across all modules
- No modifications needed to individual module pages

**Alternatives Considered**:
1. Add search input as child in each page → Rejected: Would require changes to 7 files, risk inconsistency
2. Create separate search component → Rejected: Unnecessary complexity, props already exist

### D2: Search Input Styling

**Decision**: Use existing `NEU_FILTER_INPUT_STYLE` from `styles.py`

**Rationale**:
- Maintains visual consistency with other filter controls
- Already defined and tested in the design system
- Matches the styling pattern used in date filter inputs within the same component

**Alternatives Considered**:
1. Create new search-specific style → Rejected: Unnecessary, existing style fits requirements
2. Use `NEU_INPUT_STYLE` → Rejected: Wrong dimensions (not 40px height)

### D3: Search Input Position

**Decision**: Place search input as the first element in the filter content container

**Rationale**:
- Follows common UX pattern: search first, then specific filters
- Maintains left-to-right reading order on desktop
- On mobile (drawer), search will appear at top of filter list
- Consistent with the component's existing `*children` rendering pattern

### D4: Search Behavior

**Decision**: Preserve existing behavior (no automatic filtering on keystroke)

**Rationale**:
- All module states implement `set_search()` which stores the value but doesn't trigger reload
- Search is applied on next data fetch (e.g., after pressing Enter or other filter changes)
- This is the established pattern across all 7 modules
- Changing behavior would require state modifications in all modules

## Technical Analysis

### Current Component Signature
```python
def advanced_filter_bar(
    *children,
    search_placeholder: str = "Buscar...",
    on_search: Callable = None,
    search_value: str = "",
    on_clear: Callable = None,
    action_buttons: List[rx.Component] = None,
    **props
) -> rx.Component
```

### Proposed Component Signature
No change - the existing signature is sufficient. The search input will be rendered internally using the existing props.

### Implementation Details

The search input will be rendered as:
```python
rx.box(
    rx.text("Buscar", style=styles.NEU_FILTER_LABEL_STYLE),
    rx.input(
        placeholder=search_placeholder,
        value=search_value,
        on_change=on_search,
        style=styles.NEU_FILTER_INPUT_STYLE,
    ),
    width=["100%", "100%", "250px"]
)
```

This will be inserted as the first element in both `desktop_filter_content` and `mobile_filter_content`.

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing filter layout | Medium | Use existing styles, test responsive behavior |
| Search props not connected | Low | Props already defined and passed by all pages |
| Visual inconsistency | Low | Use existing `NEU_FILTER_INPUT_STYLE` |

## Dependencies

- `src/presentacion_reflex/styles.py` - Contains style tokens
- `src/presentacion_reflex/components/shared/advanced_filter_bar.py` - Target file
- All 7 module pages - Verification targets (no changes needed)
