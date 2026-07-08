# Research: standardize-advanced-filters

**Date**: 2026-07-07

## Current State Analysis

### Inconsistencies Identified

| Aspect | Current State (Per Module) | Target State |
|--------|---------------------------|--------------|
| **Container type** | Personas: `rx.card`, Propiedades: `rx.box` + `NEU_PANEL_STYLE`, Contratos: `neuro_panel`, Liquidaciones: bare `rx.flex` + `NEU_SHADOW`, Liquidación Asesores: `rx.card`, Recaudos: `rx.flex` + `NEU_SHADOW`, Incidentes: `rx.flex` + `NEU_SHADOW` | Single `AdvancedFilterBar` component with `NEU_PANEL_STYLE` |
| **Filter spacing** | Personas: `spacing="3"` (12px), Propiedades: `gap="4"` (16px), Contratos: `gap="4"`, Liquidaciones: `gap="5"` (20px), Liquidación Asesores: `gap="3"`, Recaudos: varies, Incidentes: `gap="4"` | Uniform `gap="4"` (16px) horizontal, `gap="3"` (12px) vertical |
| **Container padding** | Personas: default card padding, Propiedades: `padding="1.5rem"` from NEU_PANEL_STYLE, Contratos: panel default, Liquidaciones: `padding="1rem"`, Liquidación Asesores: card default, Recaudos: `padding="4"` (16px), Incidentes: `padding="4"` | Uniform `padding="1.5rem"` (24px) via `NEU_PANEL_STYLE` |
| **Container background** | Personas: card default (white), Propiedades: `BG_PANEL` (warm), Contratos: panel default, Liquidaciones: none (transparent), Liquidación Asesores: card default, Recaudos: none, Incidentes: none | White background `#FFFFFF` per clarification |
| **Container border** | Personas: card border, Propiedades: `BORDER_DEFAULT`, Contratos: panel border, Liquidaciones: none, Liquidación Asesores: card border, Recaudos: none, Incidentes: none | Light gray border `#E5E7EB` per clarification |
| **Container shadow** | Personas: card shadow, Propiedades: `SHADOW_WHISPER`, Contratos: panel shadow, Liquidaciones: `NEU_SHADOW`, Liquidación Asesores: card shadow, Recaudos: `NEU_SHADOW`, Incidentes: `NEU_SHADOW` | No shadow per clarification |
| **Responsive layout** | Personas: `rx.breakpoints(initial="column", md="row")`, Propiedades: `gap` + `wrap`, Contratos: nested flex, Liquidaciones: two-row manual, Liquidación Asesores: `rx.breakpoints`, Recaudos: `rx.breakpoints`, Incidentes: `gap="4"` + `wrap="wrap"` | Consistent `rx.breakpoints` + `wrap="wrap"` |
| **Action buttons** | Personas: `neuro_button` icons, Propiedades: `neuro_button` icons, Contratos: `neuro_button` icons, Liquidaciones: mixed `neuro_button` + text, Liquidación Asesores: `neuro_button` + text, Recaudos: mixed, Incidentes: `rx.segmented_control` + `rx.button` | All icon-only `neuro_button` with tooltip |
| **Filter labels** | Personas: floating labels on Select, Propiedades: floating labels, Contratos: floating labels, Liquidaciones: floating labels, Liquidación Asesores: floating labels, Recaudos: floating labels, Incidentes: floating labels | Consistent: search=placeholder only, Select/DatePicker=label above, Toggle/Checkbox=label right |
| **Clear button badge** | None of the modules have this | Badge with active filter count on clear button |
| **Auto-apply** | Most modules auto-apply on change, some require manual action | All modules auto-apply on filter value change |

### Existing Design Tokens (from `styles.py`)

| Token | Value | Usage |
|-------|-------|-------|
| `NEU_INPUT_STYLE` | height: 44px, border-radius: 12px, padding: 0.75rem 1rem | Text inputs |
| `NEU_SELECT_STYLE` | height: 44px, border-radius: 12px, padding: 0 1rem | Select dropdowns |
| `NEU_BUTTON_STYLE` | height: 44px, border-radius: 12px | Action buttons |
| `NEU_ICON_BUTTON_STYLE` | height: 40px, border-radius: 10px | Icon-only buttons |
| `NEU_PANEL_STYLE` | padding: 1.5rem, border-radius: 16px | Panel containers |
| `BORDER_DEFAULT` | var(--border-default) ~#f0eee6 | Default borders |

### Decision: Component Height Adjustment

**Decision**: Change component height from current 44px to 40px per spec FR-001.

**Rationale**: The spec explicitly requires 40px height for all filter components. The current 44px is close but not matching. The 4px reduction makes components more compact and aligns with modern filter bar conventions.

**Alternatives considered**:
- Keep 44px: Rejected because spec requires 40px and the reference images show more compact components.
- Use 36px: Rejected because it would make components too small for touch targets.

### Decision: Border Radius Adjustment

**Decision**: Change border-radius from current 12px to 8px per spec FR-001.

**Rationale**: The spec requires 8px border-radius. The current 12px is more rounded. The 8px creates a slightly sharper look that matches the reference images.

**Alternatives considered**:
- Keep 12px: Rejected because spec requires 8px.
- Use 4px: Rejected because it would look too sharp for the neumorphic design language.

### Decision: Container Styling Override

**Decision**: Create a new `NEU_FILTER_BAR_STYLE` token that overrides `NEU_PANEL_STYLE` for filter containers.

**Rationale**: The spec requires white background (#FFFFFF), light gray border (#E5E7EB), and no shadow. This differs from the existing `NEU_PANEL_STYLE` which uses warm-toned `BG_PANEL` and `SHADOW_WHISPER`.

**Alternatives considered**:
- Modify `NEU_PANEL_STYLE` globally: Rejected because it would affect all panels, not just filter bars.
- Use inline styles per module: Rejected because it would duplicate styles across 7 modules.

### Decision: Active Filter Badge

**Decision**: Add a small numeric badge to the "Limpiar" (clear) button showing the count of active (non-default) filters.

**Rationale**: Per clarification Q4, users need visual feedback when filters are active. A badge on the clear button is the most intuitive location.

**Alternatives considered**:
- Badge on container border: Rejected because it would be harder to position consistently.
- Color change on container: Rejected because it could clash with the design language.

### Decision: Shared Component Architecture

**Decision**: Create `AdvancedFilterBar` as a wrapper component that accepts filter slots and action buttons as children.

**Rationale**: Each module has different filters with different state variables. A slot-based architecture allows each module to pass its specific filters while the wrapper handles layout, spacing, and styling.

**Alternatives considered**:
- Create separate components per filter type: Rejected because it would still require per-module layout code.
- Use CSS classes only: Rejected because Reflex component-level styling is more maintainable.
