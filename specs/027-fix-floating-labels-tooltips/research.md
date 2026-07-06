# Research: Corrección de Floating Labels y Tooltips

**Date**: 2026-07-05
**Feature**: 027-fix-floating-labels-tooltips

## Research Tasks Completed

### 1. Estado Actual de Floating Labels

**Decision**: Los componentes base existen en `components/shared/floating_label.py`

**Hallazgos**:
- `floating_input()` — Implementado con label CSS que se desplaza al enfocar
- `floating_select()` — Implementado con label siempre en posición superior
- `neuro_floating_input()` y `neuro_floating_select()` — Wrappers en `neuro_elements.py`
- Tokens definidos en `styles.py`: `FL_LABEL_COLOR`, `FL_LABEL_FOCUS_COLOR`, `FL_LABEL_ERROR_COLOR`, `FL_TRANSITION`
- CSS selectors en `BASE_STYLE`: `.floating-input:focus ~ .floating-label`, `.floating-input:not(:placeholder-shown) ~ .floating-label`

**Razón**: Componentes ya implementados, requieren corrección de consistencia

**Alternativas consideradas**:
- Usar componentes nativos de Reflex → Rechazado: pierde el estilo neumórfico
- Crear nuevos componentes desde cero → Rechazado: innecesario, los base funcionan

### 2. Tooltips Existentes

**Decision**: Tooltips implementados via `neuro_tooltip()` usando `rx.hover_card`

**Hallazgos**:
- `neuro_tooltip()` en `neuro_elements.py` usa `rx.hover_card.root/trigger/content`
- `NEU_TOOLTIP_STYLE` definido en `styles.py` con `z_index: Z_TOOLTIP`
- `neuro_button()` y `neuro_icon_action_button()` aceptan `tooltip_content` parameter
- No existe archivo centralizado de textos de tooltips

**Razón**: Tooltips funcionales pero sin centralización de contenido

**Alternativas consideradas**:
- Usar `rx.tooltip` nativo → Rechazado: solo soporta strings simples
- Mantener `rx.hover_card` → Seleccionado: soporta contenido complejo

### 3. Z-Index Conflicts

**Decision**: Z-index actual es consistente pero puede haber conflictos en modales

**Hallazgos**:
- `Z_MODAL = "1000"`, `Z_POPOVER = "1050"`, `Z_TOOLTIP = "1100"`
- `BASE_STYLE` configura `rx.dialog.content` con `z_index: Z_MODAL`
- `rx.hover_card.content` usa `z_index: Z_TOOLTIP`
- Potencial conflicto: tooltip dentro de modal puede quedar detrás

**Razón**: Tooltip (1100) > Modal (1000), pero portal puede causar issues

**Alternativas consideradas**:
- Aumentar Z_TOOLTIP global → Rechazado: puede afectar otros usos
- Usar Z contextual (mayor que modal) → Seleccionado: más seguro

### 4. Contenido de Tooltips

**Decision**: Contenido hardcodeado en cada uso, sin centralización

**Hallazgos**:
- No existe archivo `tooltips_text.py` o similar
- Cada módulo define sus tooltips inline
- Difícil mantener consistencia de messaging

**Razón**: Centralizar mejora mantenibilidad y facilita traducción

**Alternativas consideradas**:
- Base de datos → Rechazado: over-engineering para textos estáticos
- Constantes inline → Rechazado: dificulta mantenimiento
- Archivo de constantes → Seleccionado: balance mantenibilidad/simplicidad

## Summary of Decisions

| Área | Decisión | Rationale |
|------|----------|-----------|
| Floating Labels | Corregir componentes existentes | Base sólida, solo necesita ajustes |
| Tooltips | Mantener rx.hover_card + centralizar textos | Soporte contenido complejo |
| Z-Index | Crear Z contextual para modales | Evitar conflictos de portal |
| Contenido | Archivo de constantes | Mantenibilidad y traducción |
| Accesibilidad | ATRIBUTOS ARIA básicos | Cumplimiento mínimo WCAG |
