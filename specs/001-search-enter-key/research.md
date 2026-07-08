# Research: Búsqueda con Tecla ENTER

**Date**: 2026-07-08
**Feature**: 001-search-enter-key

## R1: Cómo funciona `on_key_down` en Reflex `rx.input`

**Decision**: Usar el parámetro `on_key_down` de `rx.input` que recibe el nombre de la tecla presionada como string.

**Rationale**: Reflex expone `on_key_down` como evento nativo de `rx.input`. El handler recibe un string con el nombre de la tecla (ej. `"Enter"`, `"Escape"`). Esto es el estándar de la librería y no requiere workarounds.

**Alternatives considered**:
- `on.KeyPress` (React nativo) — No expuesto directamente por Reflex, requiere JS interop innecesario.
- `on_blur` + timer — Anti-patrón, no confiable.
- Custom JavaScript via `rx.script` — Complejidad innecesaria para un caso de uso estándar.

**Source**: Documentación oficial de Reflex para `rx.input`: https://reflex.dev/docs/library/forms/input/

## R2: Patrón existente de `handle_search_key_down` en el códigobase

**Decision**: Reutilizar el patrón exacto ya implementado en 3 estados (Personas, Liquidaciones, Recaudos).

**Rationale**: Ya existe código funcional que implementa esta lógica:
```python
def handle_search_key_down(self, key: str):
    if key == "Enter":
        return self.search_<modulo>()
```
Este patrón es correcto, testeado, y consistente. Solo necesita ser conectado al input y replicado en los estados que faltan.

**Alternatives considered**:
- Crear un mixin o clase base para el handler — Over-engineering para un handler de 3 líneas.
- Usar un evento global de teclado — Complejidad innecesaria, pierde el contexto del input específico.

## R3: Inconsistencia en comportamiento de `set_search`

**Decision**: Para el handler ENTER, invocar siempre el método de búsqueda explícito (`search_<modulo>` o `load_<modulo>`), independientemente de si `set_search` ya dispara recarga.

**Rationale**: El comportamiento actual es inconsistente:
- **Recarga en set_search**: Propiedades, Liquidaciones, Recaudos, Incidentes, Liquidación Asesores
- **Solo almacena valor**: Personas, Contratos

El handler ENTER debe ser idéntico al clic del botón "Buscar" (que siempre ejecuta búsqueda explícita). Esto garantiza consistencia sin alterar el comportamiento existente de `set_search`.

**Alternatives considered**:
- Unificar `set_search` para que siempre recargue — Cambio de comportamiento existente, riesgo de regresión.
- No hacer nada en ENTER si `set_search` ya recarga — Inconsiciente con el requisito de "mismo resultado que el botón".

## R4: Componente `advanced_filter_bar` — Cómo agregar `on_key_down`

**Decision**: Agregar parámetro `on_key_down: Callable = None` al componente y pasarlo al `rx.input`.

**Rationale**: El componente ya acepta `on_search` (para `on_change`). Agregar `on_key_down` sigue el mismo patrón de parámetros callback. Si es `None`, simplemente no se asigna al input (comportamiento backward-compatible).

**Implementation pattern**:
```python
def advanced_filter_bar(
    *children,
    search_placeholder: str = "Buscar...",
    on_search: Callable = None,
    on_key_down: Callable = None,  # NUEVO
    search_value: str = "",
    on_clear: Callable = None,
    action_buttons: List[rx.Component] = None,
    **props
) -> rx.Component:
    # ...
    input_props = {
        "placeholder": search_placeholder,
        "value": search_value,
        "on_change": on_search,
        "style": NEU_FILTER_INPUT_STYLE,
        "width": "100%",
    }
    if on_key_down is not None:
        input_props["on_key_down"] = on_key_down
    
    search_box = rx.box(
        rx.text("Buscar", style=NEU_FILTER_LABEL_STYLE),
        rx.input(**input_props),
        width=["100%", "100%", "250px"]
    )
```

**Alternatives considered**:
- Agregar `**props` al `rx.input` — Menos explícito, pierde type safety.
- Crear un sub-componente `SearchInput` — Complejidad innecesaria para un parámetro más.

## R5: Módulos que necesitan nuevo handler vs. los que ya lo tienen

**Decision**: Clasificación por estado:

| Estado | ¿Tiene `handle_search_key_down`? | ¿Tiene `search_<modulo>`? | Acción |
|--------|----------------------------------|---------------------------|--------|
| PersonasState | ✅ Sí | ✅ Sí (`search_personas`) | Solo wiring en página |
| PropiedadesState | ❌ No | ❌ No | Crear handler + método |
| ContratosState | ❌ No | ❌ No | Crear handler + método |
| LiquidacionesState | ✅ Sí | ✅ Sí (`search_liquidaciones`) | Solo wiring en página |
| LiquidacionFiltrosState | ❌ No | ❌ No (usa `_trigger_reload`) | Crear handler |
| RecaudosState | ✅ Sí | ✅ Sí (`search_recaudos`) | Solo wiring en página |
| IncidentesState | ❌ No | ❌ No | Crear handler + método |

**Rationale**: 3 estados ya tienen el handler completo. 4 estados necesitan crear el handler. Para los que no tienen `search_<modulo>`, se crea un método que resetea página y llama a `load_<modulo>` (patrón idéntico al de Personas/Liquidaciones/Recaudos).

## R6: Prevención de ejecuciones múltiples

**Decision**: No se requiere debounce adicional. El handler `on_key_down` de `rx.input` solo dispara un evento por pulsación de tecla. La ejecución múltiple solo ocurriría si el usuario presiona ENTER repetidamente, pero cada pulsación es un evento independiente que invoca el mismo handler.

**Rationale**: En Reflex, cada `on_key_down` es un evento stateful que se encola. Si el usuario presiona ENTER 3 veces rápido, se encolan 3 eventos. El primero inicia la carga, los otros repiten la misma operación. Esto es aceptable porque:
1. La búsqueda es idempotente (mismos parámetros = mismos resultados)
2. El `load_<modulo>` resetea paginación y recarga
3. No hay riesgo de corrupción de datos

**Alternatives considered**:
- Flag `_search_in_progress` en state — Complejidad innecesaria, bloquearía búsquedas legítimas secuenciales.
- Debounce en el input — Retrasa la respuesta del usuario, anti-patrón para SEARCH.

**NOTA**: Si en testing se detecta que las búsquedas repetidas causan problemas de rendimiento, se puede agregar un flag `self._buscando: bool` como mejora futura.
