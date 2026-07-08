# Agent Context: Restore Search Input in Advanced Filters

## Feature Overview

**Problem**: The search input field was removed from the Advanced Filters section of 7 modules due to a regression.

**Root Cause**: The `advanced_filter_bar` component accepts search-related props but does not render a search input. The search input needs to be added inside the component.

**Solution**: Add the search input rendering inside `advanced_filter_bar` using the existing props that all 7 modules already pass.

## Key Files

| File | Purpose |
|------|---------|
| `src/presentacion_reflex/components/shared/advanced_filter_bar.py` | Target file - add search input rendering |
| `src/presentacion_reflex/styles.py` | Style tokens (`NEU_FILTER_INPUT_STYLE`, `NEU_FILTER_LABEL_STYLE`) |
| `src/presentacion_reflex/pages/personas.py` | Verification target (line 305) |
| `src/presentacion_reflex/pages/propiedades.py` | Verification target (line 243) |
| `src/presentacion_reflex/pages/contratos.py` | Verification target (line 467) |
| `src/presentacion_reflex/pages/liquidaciones.py` | Verification target (line 71) |
| `src/presentacion_reflex/pages/liquidacion_asesores.py` | Verification target (line 104) |
| `src/presentacion_reflex/pages/recaudos.py` | Verification target (line 41) |
| `src/presentacion_reflex/pages/incidentes.py` | Verification target (line 22) |

## Implementation Notes

1. **Do NOT modify module pages** - they already pass correct search props
2. **Use existing styles** - `NEU_FILTER_INPUT_STYLE` for input, `NEU_FILTER_LABEL_STYLE` for label
3. **Maintain responsive behavior** - search input appears in both desktop and mobile views
4. **Position**: Search input should be the first element in the filter content container

## Verification Checklist

- [ ] Search input visible in Personas module
- [ ] Search input visible in Propiedades module
- [ ] Search input visible in Contratos module
- [ ] Search input visible in Liquidaciones module
- [ ] Search input visible in Liquidación de Asesores module
- [ ] Search input visible in Recaudos module
- [ ] Search input visible in Incidentes module
- [ ] Search functionality works in all modules
- [ ] UI dimensions match existing filter controls
- [ ] Mobile responsive behavior preserved
- [ ] No regressions to existing filters
