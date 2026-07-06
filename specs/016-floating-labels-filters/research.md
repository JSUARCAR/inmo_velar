# Research: Floating Labels en Filtros Avanzados

**Date**: 2026-07-05 | **Feature**: 016-floating-labels-filters

## Decision Log

### D1: Estrategia de Implementación del Floating Label

**Decision**: Componente wrapper que envuelve `rx.input` existente con CSS puro

**Rationale**:
- No requiere modificar la API de Reflex subyacente
- Compatibilidad total con componentes neumórficos existentes
- CSS transitions ya soportadas por el sistema de estilos del proyecto
- Permite migración incremental (componente opt-in)

**Alternatives Considered**:
- *Custom input component desde cero*: Rechazado - alto esfuerzo, riesgo de incompatibilidad
- *Fork de rx.input*: Rechazado - dificulta actualizaciones de Reflex
- *CSS-only (sin componente)*: Rechazado - requiere JS para detectar foco/valores

### D2: Mecanismo de Detección de Estado

**Decision**: Usar CSS `:focus-within` + `:not(:placeholder-shown)` para estados CSS puros, con `rx.Var` para estado React

**Rationale**:
- `:focus-within` detecta foco nativamente en el contenedor
- `:not(:placeholder-shown)` detecta si hay contenido (requiere placeholder vacío ` `)
- Para React/Reflex: usar `rx.Var` con `on_focus`/`on_blur` para animaciones controladas
- Combinación cubre todos los edge cases (valores preseleccionados, errores)

**Alternatives Considered**:
- *Solo CSS puro*: Insuficiente - no maneja valores preseleccionados dinámicamente
- *Solo React state*: Innecesariamente complejo para animaciones simples
- *MutationObserver*: Overkill para este caso de uso

### D3: Curva de Animación

**Decision**: `cubic-bezier(0.4, 0, 0.2, 1)` (Material Design standard)

**Rationale**:
- Ya definido en la constitución del proyecto (§3)
- Consistente con transiciones existentes (`GLOBAL_TRANSITION`)
- Curva probada en interfaces de producción

**Alternatives Considered**:
- *ease-in-out*: Más simple pero menos natural
- *linear*: Mecánico, pobre experiencia de usuario

### D4: Manejo de Estados de Error

**Decision**: Propiedad `error: bool` que cambia color de etiqueta a `var(--red-9)`

**Rationale**:
- Consistente con sistema semántico de colores del proyecto
- Simple de usar: solo se pasa prop booleana
- Extensible: permite agregar icono de error en futuro

**Alternatives Considered**:
- *Propiedad de color directa*: Menos semántica, más propiedades que mantener
- *Clase CSS externa*: Menos integrado con el sistema de componentes

### D5: Accesibilidad

**Decision**: Usar `<label>` HTML nativo vinculado al input via `htmlFor`/`id`

**Rationale**:
- Soporte nativo de lectores de pantalla
- Navegación por teclado completa (Tab + Enter)
- Cumplimiento WCAG 2.1 AA
- Reflex soporta `html_for` en `rx.text` cuando se usa como label

**Alternatives Considered**:
- *aria-label*: Menos semántico, no muestra texto visible
- *div con role="label"*: No tiene soporte nativo de asociación

## Technical Findings

### Reflex Input API

```python
# Estructura actual de rx.input en Reflex 0.8.x
rx.input(
    placeholder="...",
    value=state_var,
    on_change=handler,
    size="3",
    style={...},
)
```

### CSS Selectors para Floating Label

```css
/* Estado vacío - label posición normal */
.floating-label-group input:not(:focus) + label {
    transform: translateY(0);
    font-size: 1rem;
}

/* Estado foco o con valor - label arriba */
.floating-label-group input:focus + label,
.floating-label-group input:not(:placeholder-shown) + label {
    transform: translateY(-24px);
    font-size: 0.75rem;
}
```

### Integración con neum_elements.py

```python
# Wrapper neumórfico para floating input
def neuro_floating_input(label: str, **kwargs) -> rx.Component:
    return floating_input(
        label=label,
        style=NEU_INPUT_STYLE,
        **kwargs,
    )
```

## Risks & Mitigations

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Incompatibilidad con versiones futuras de Reflex | Baja | Medio | Usar API pública estable, documentar dependencia |
| Performance en campos con muchas transiciones | Baja | Bajo | CSS transitions son eficientes por defecto |
| Conflictos con estilos neumórficos existentes | Media | Medio | Usar specificity alta, testing exhaustivo |

## References

- Reflex Documentation: https://reflex.dev/docs/components/
- Radix UI Primitives: https://www.radix-ui.com/primitives
- Material Design Motion: https://m3.material.io/styles/motion
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
