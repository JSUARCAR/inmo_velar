# Research: Recaudos - Filtros Avanzados y Ordenamiento de Tabla

**Date**: 2026-07-05
**Feature**: 015-recaudos-filtros-sort

## Research Questions

### RQ-001: Infraestructura de filtros y sorting en RecaudosState

**Decision**: Reutilizar la infraestructura existente sin cambios al backend.

**Rationale**: El reverse engineering confirmó que:
- `RecaudosState.filter_contrato` (línea 69) ya existe como variable de estado
- `FiltrosRecaudo.id_contrato` (repositorio, líneas 17-34) ya soporta filtrado por contrato
- `toggle_sort()` (línea 204-213) ya implementa la alternancia asc/desc
- `SORT_COLUMNS` (repositorio, líneas 554-567) ya mapea las 8 columnas ordenables

**Alternatives considered**:
- Agregar nuevos filtros al backend → Rechazado: la infraestructura ya existe
- Crear un componente de toolbar compartido → Rechazado: fuera de alcance, alto riesgo de regresión

---

### RQ-002: Patrón de toolbar homologado con Liquidaciones

**Decision**: Seguir la estructura de `liquidaciones_toolbar()` (líneas 68-205) como referencia de diseño.

**Rationale**: La toolbar de Liquidaciones tiene una estructura de 2 grupos:
1. Grupo de filtros: `rx.flex` con `gap="5"`, `align="center"`, `flex_wrap="wrap"`
2. Grupo de acciones: `rx.hstack` con `spacing="5"`, `align="center"`, `wrap="wrap"`

La toolbar de Recaudos actual (líneas 38-140) tiene una estructura plana con todos los elementos en un solo `rx.flex`. Se debe reorganizar en 2 grupos para homologar.

**Alternatives considered**:
- Mantener la estructura actual de Recaudos → Rechazado: no cumple el requisito de homologación
- Crear un componente `ToolbarFiltros` compartido → Rechazado: fuera de alcance para esta feature

---

### RQ-003: Carga de opciones del filtro Pago Contrato

**Decision**: Cargar contratos activos desde la base de datos usando la misma lógica que `load_filter_options()` en `RecaudosState`.

**Rationale**: El método `load_filter_options()` (líneas 155-175 de `recaudos_state.py`) ya carga `contratos_options` y `contratos_select_options` desde el servicio. Solo se necesita renderizar un `neuro_select_root` con estas opciones usando `rx.foreach`.

**Alternatives considered**:
- Hardcodear las opciones → Rechazado: no escala, inconsistente con el patrón existente
- Usar un endpoint API separado → Rechazado: innecesario, los datos ya se cargan

---

### RQ-004: Componente de empty state (sin resultados)

**Decision**: Usar `rx.callout` con icono "search" y mensaje "No se encontraron recaudos", siguiendo el patrón de Liquidaciones.

**Rationale**: La clarificación del usuario definió este componente. El `rx.callout` es un componente nativo de Reflex que ya se usa en Liquidaciones para estados vacíos.

**Alternatives considered**:
- Mensaje inline en tabla → Rechazado: menos visible, inconsistente con Liquidaciones
- Toast temporal → Rechazado: no persiste, el usuario puede no verlo

---

### RQ-005: Botón de limpiar filtros

**Decision**: Agregar un `neuro_button` con icono "filter-x" o "x" que restablezca todos los filtros a valores por defecto.

**Rationale**: El FR-007 especifica este componente. Actualmente no existe en ninguno de los dos módulos. Se agregará solo en Recaudos (nuevo comportamiento).

**Valores por defecto**:
- `search_text`: `""`
- `filter_estado`: `"Todos"`
- `filter_contrato`: `""` (o `"Todos"` si se agrega como opción)
- `filter_fecha_desde`: `""`
- `filter_fecha_hasta`: `""`
- `sort_by`: `"fecha_pago"`
- `sort_order`: `"desc"`
- `current_page`: `1`

**Alternatives considered**:
- No agregar botón → Rechazado: FR-007 lo requiere explícitamente
- Usar icono "rotate-ccw" → Rechazado: "filter-x" o "x" es más semántico para limpiar filtros

---

### RQ-006: Ordenamiento de la columna "Método de Pago"

**Decision**: La columna "Método de Pago" NO es ordenable (actualmente no lo es y el spec solo menciona excluir "Acciones").

**Rationale**: El spec dice "con excepción de la columna Acciones". Sin embargo, "Método de Pago" es una columna de badge con variantes de color que no tiene un orden natural semántico. El reverse engineering confirmó que SORT_COLUMNS no incluye esta columna.

**Alternatives considered**:
- Hacer ordenable "Método de Pago" → Rechazado: no tiene orden natural, el spec no lo requiere
- Mantener como no ordenable → Seleccionado: consistente con la implementación actual

---

## Summary of Decisions

| # | Decision | Impact |
|---|----------|--------|
| RQ-001 | Reutilizar infraestructura existente | Sin cambios backend |
| RQ-002 | Seguir patrón de toolbar de Liquidaciones | Reorganizar UI en 2 grupos |
| RQ-003 | Cargar contratos desde DB existente | Solo agregar componente UI |
| RQ-004 | `rx.callout` para empty state | Componente nuevo en Recaudos |
| RQ-005 | Botón `neuro_button` para limpiar filtros | Handler nuevo en State |
| RQ-006 | "Método de Pago" no es ordenable | Solo 8 columnas ordenables |
