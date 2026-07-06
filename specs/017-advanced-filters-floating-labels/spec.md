# Feature Specification: Estandarización de Filtros Avanzados con Floating Labels

**Feature Branch**: `017-advanced-filters-floating-labels`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Ingeniería inversa de nivel Senior/Principal sobre todos los formularios de Filtros Avanzados del sistema, con el objetivo de estandarizar su comportamiento y alinearlos con las mejores prácticas de UI/UX y accesibilidad. Reemplazar placeholders por etiquetas visibles (labels) permanentes o patrón Floating Label."

## User Scenarios & Testing

### User Story 1 - Filtros con Etiquetas Visibles en Módulos Principales (Priority: P1)

Como usuario del sistema inmobiliario, al navegar por los módulos principales (Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos), deseo que cada campo de filtro avance muestre una etiqueta visible permanente que identifique su contenido, para que pueda identificar rápidamente qué información debe ingresar sin depender de la memoria.

**Why this priority**: Es el caso de uso más frecuente. Los usuarios interactúan diariamente con estos módulos para buscar y filtrar registros. Una identificación clara de campos reduce errores y tiempo de búsqueda.

**Independent Test**: Puede probarse navegando a cualquier módulo principal, verificando que cada campo de filtro tenga una etiqueta visible que no desaparezca al ingresar datos.

**Acceptance Scenarios**:

1. **Given** el usuario navega al módulo de Personas, **When** visualiza la sección de Filtros Avanzados, **Then** cada campo (Buscar, Rol, Fecha Desde, Fecha Hasta) muestra su etiqueta permanentemente visible
2. **Given** el usuario ingresa un valor en el campo "Buscar", **When** el campo contiene datos, **Then** la etiqueta "Buscar" se desplaza hacia arriba y permanece visible
3. **Given** el usuario selecciona un valor en el campo "Rol", **When** el campo tiene selección, **Then** la etiqueta "Rol" permanece en posición superior visible
4. **Given** el usuario elimina el contenido de un campo, **When** el campo queda vacío, **Then** la etiqueta regresa a su posición original dentro del campo

---

### User Story 2 - Homologación de Módulos Secundarios (Priority: P2)

Como usuario del sistema, al acceder a módulos secundarios (Desocupaciones, Incidentes, Seguros, Recibos Públicos, Saldos a Favor, Usuarios, Reportes), deseo que los filtros avanzados presenten el mismo patrón visual de etiquetas flotantes que los módulos principales, para que mi experiencia sea uniforme en todo el sistema.

**Why this priority**: Garantiza consistencia en la experiencia de usuario. Los módulos secundarios actualmente usan componentes no homologados (raw `rx.input`/`rx.select` sin estilos neumórficos).

**Independent Test**: Puede probarse verificando que cada módulo secundario tenga filtros con etiquetas visibles y estilos consistentes con el diseño neumórfico.

**Acceptance Scenarios**:

1. **Given** el usuario navega al módulo de Seguros, **When** visualiza los filtros, **Then** los campos de búsqueda y estado muestran etiquetas flotantes con estilo neumórfico consistente
2. **Given** el usuario navega al módulo de Reportes, **When** selecciona un reporte con filtros dinámicos, **Then** los campos filtrados muestran etiquetas visibles para cada filtro aplicado
3. **Given** el usuario navega al módulo de Desocupaciones, **When** visualiza el filtro de estado, **Then** el select muestra una etiqueta visible "Estado" en lugar de un placeholder

---

### User Story 3 - Accesibilidad y Navegación por Teclado (Priority: P3)

Como usuario con necesidades de accesibilidad, deseo que los campos de filtro sean navegables por teclado y que los lectores de pantalla anuncien correctamente el nombre de cada campo, para que pueda usar el sistema independientemente de mis capacidades.

**Why this priority**: Requisito de accesibilidad legal y ético. Afecta a un porcentaje menor de usuarios pero es crítico para inclusión.

**Independent Test**: Puede protestarse navegando con Tab/Shift+Tab entre campos y verificando que los lectores de pantalla anuncien las etiquetas correctamente.

**Acceptance Scenarios**:

1. **Given** el usuario navega por teclado, **When** presiona Tab para avanzar entre campos, **Then** el foco se muestran claramente en cada campo
2. **Given** un lector de pantalla está activo, **When** el foco llega a un campo de filtro, **Then** el lector anuncia el nombre de la etiqueta del campo
3. **Given** el usuario presiona Enter en un campo de select, **When** se abre el dropdown, **Then** las opciones son navegables con flechas del teclado

---

### Edge Cases

- Campos con valores preseleccionados (ej: "Todos") deben mostrar la etiqueta en posición superior desde el inicio
- Campos de tipo select/dropdown con opciones largas deben truncar el texto sin romper el layout
- En dispositivos móviles, las etiquetas deben ser legibles y no interferir con el teclado virtual
- Estados de error deben mantener la etiqueta visible, cambiando su color para indicar validación fallida
- Campos de fecha (type="date") deben aplicar el mismo patrón de etiqueta flotante
- Los filtros dinámicos de Reportes (que cambian según el reporte seleccionado) deben mantener etiquetas visibles
- Módulos con filtros mínimos (Desocupaciones: solo 1 select) deben aplicar el mismo patrón
- El campo de búsqueda general (sidebar) en Reportes debe mantener el mismo patrón de etiqueta

## Requirements

### Functional Requirements

- **FR-01**: Cada campo de filtro debe tener una etiqueta visible que identifique su contenido
- **FR-02**: La etiqueta debe desplazarse hacia arriba cuando el campo recibe foco o contiene datos (patrón Floating Label)
- **FR-03**: La etiqueta nunca debe desaparecer ni ser reemplazada únicamente por un placeholder
- **FR-04**: El patrón Floating Label debe ser consistente en todos los campos de filtro del sistema
- **FR-05**: Las transiciones de la etiqueta deben ser suaves, durar entre 150-300ms y usar curva `cubic-bezier(0.4, 0, 0.2, 1)`
- **FR-06**: Los campos con valores preseleccionados deben mostrar la etiqueta en posición superior
- **FR-07**: El componente debe ser accesible mediante navegación por teclado (Tab, Shift+Tab, Enter, flechas)
- **FR-08**: Los lectores de pantalla deben anunciar correctamente el nombre del campo asociado a cada etiqueta
- **FR-09**: En estado de error, la etiqueta debe cambiar su color para indicar validación fallida manteniendo la legibilidad
- **FR-10**: Los módulos que actualmente usan componentes raw (rx.input/rx.select) deben migrarse a los componentes neumórficos con floating labels
- **FR-11**: Los filtros dinámicos de Reportes deben aplicar etiquetas flotantes a cada campo filtrable
- **FR-12**: Los selects de un solo campo (Desocupaciones, Saldos a Favor) deben aplicar el mismo patrón
- **FR-13**: Los campos de fecha (type="date") deben usar floating_input con etiqueta visible
- **FR-14**: El sidebar de búsqueda en Reportes debe aplicar el mismo patrón de etiqueta flotante

### Key Entities

- **Campo de Filtro**: Elemento de formulario que permite al usuario filtrar datos en una tabla o listado. Puede ser input, select, date o switch.
- **Etiqueta Flotante (Floating Label)**: Texto descriptivo que se desplaza suavemente hacia arriba cuando el campo recibe foco o contiene datos, permaneciendo siempre visible.
- **Estado del Campo**: Representa si el campo está vacío (etiqueta centrada), con foco (etiqueta superior animada), con datos (etiqueta superior estática) o en error (etiqueta en color de error).
- **Componente Reutilizable**: Pieza de código UI que encapsula el comportamiento de floating label para inputs y selects, usada por todos los módulos del sistema.

## Success Criteria

### Measurable Outcomes

- **SC-001**: El usuario puede identificar un campo de filtro en menos de 1 segundo (etiqueta visible permanente)
- **SC-002**: Reducción del 30% en errores de datos ingresados en campos incorrectos
- **SC-003**: Reducción del 20% en tiempo para completar filtros
- **SC-004**: 100% de campos de filtro del sistema muestran etiquetas visibles permanentes
- **SC-005**: Los 14 módulos presentan diseño uniforme en filtros avanzados
- **SC-006**: Puntuación de accesibilidad (WCAG 2.1 AA) mejora en campos de filtro
- **SC-007**: No hay regresiones en funcionalidad de filtrado existente
- **SC-008**: El diseño es completamente responsivo en desktop, tablet y móvil

### Qualitative Measures

- Los usuarios reportan mayor claridad en la identificación de campos
- La interfaz se percibe más profesional y consistente en todos los módulos
- Mejora en la accesibilidad para usuarios con discapacidades visuales
- Los desarrolladores encuentran el código más mantenible gracias a componentes reutilizados

## Assumptions

- El sistema actual utiliza placeholders que desaparecen al ingresar datos, lo cual es la práctica a reemplazar
- Los componentes `floating_input` y `floating_select` existentes en `shared/floating_label.py` son la base técnica a usar
- Los componentes `neuro_floating_input` y `neuro_floating_select` en `neuro_elements.py` son los wrappers neumórficos a emplear
- Los módulos que usan componentes raw (Seguros, Saldos a Favor, Reportes) deben ser migrados a los componentes neumórficos
- La implementación debe ser compatible con la versión actual de Reflex (0.6.x)
- No se requiere soporte para navegadores muy antiguos (IE11)
- El patrón Floating Label existente en el proyecto es el estándar a seguir
- Los estilos neumórficos existentes (`NEU_INPUT_STYLE`, `NEU_SELECT_STYLE`) se mantienen

## Scope

### In Scope

- **Módulos con filtros existentes**: Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos, Desocupaciones, Incidentes, Seguros, Recibos Públicos, Saldos a Favor, Usuarios, Reportes
- **Módulo sin filtros**: Gestión de IPC / Incrementos (no tiene filtros avanzados, solo formulario modal)
- **Tipos de campo**: Input de búsqueda, Select, Date input, Switch/Checkbox
- **Componentes reutilizables**: `floating_input`, `floating_select`, `neuro_floating_input`, `neuro_floating_select`
- **Patrón visual**: Floating Label con transición suave, colores consistentes, espaciado uniforme
- **Accesibilidad**: Navegación por teclado, soporte para lectores de pantalla
- **Responsividad**: Desktop, tablet y móvil

### Out of Scope

- Modificación de la lógica de filtrado existente (back-end/state)
- Cambios en la estructura de datos subyacente
- Modificación de estilos globales del sistema (solo componentes de formulario de filtro)
- Creación de nuevos campos de filtro (solo reemplazar placeholders por labels en campos existentes)
- Módulo de Gestión de IPC / Incrementos (no tiene filtros avanzados)
- Modales de edición/creación de registros (solo sección de filtros)

## Module-to-File Mapping

| # | Module | Page File | Filter Fields |
|---|--------|-----------|---------------|
| 1 | Personas | `pages/personas.py` | Buscar, Rol, Fecha Desde, Fecha Hasta |
| 2 | Propiedades | `pages/propiedades.py` | Buscar, Tipo, Disponibilidad |
| 3 | Contratos | `pages/contratos.py` | Buscar, Asesor, Tipo, Estado |
| 4 | Liquidaciones | `pages/liquidaciones.py` | Buscar, Período, Estado, Ciclo, Asesor |
| 5 | Liquidación de Asesores | `pages/liquidacion_asesores.py` | Buscar, Período |
| 6 | Recaudos | `pages/recaudos.py` | Buscar, Pago Contrato, Estado, Fecha Desde, Fecha Hasta |
| 7 | Desocupaciones | `pages/desocupaciones.py` | Estado (raw rx.select) |
| 8 | Incidentes | `pages/incidentes.py` | Buscar, Prioridad, Estado |
| 9 | Seguros | `pages/seguros.py` | Buscar, Estado (raw rx.input/rx.select) |
| 10 | Recibos Públicos | `pages/recibos.py` | Buscar, Servicio, Estado |
| 11 | Saldos a Favor | `pages/saldos_favor.py` | Tipo, Estado (raw rx.select) |
| 12 | Usuarios | `pages/usuarios.py` | Buscar, Rol, Estado |
| 13 | Reportes | `pages/reportes.py` | Sidebar search + filtros dinámicos por reporte |
