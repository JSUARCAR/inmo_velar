# Specification: Auditoría y Restauración de Componentes UI (Floating Labels y Tooltips)

## 1. Introduction

### 1.1 Purpose
Este documento define los requerimientos para investigar, auditar y restaurar el funcionamiento de las **Etiquetas Flotantes (Floating Labels)** y los **Tooltips** en todos los módulos de la plataforma Inmobiliaria Velar. El objetivo es garantizar una experiencia de usuario (UX) homogénea, profesional y acorde al Sistema de Diseño de la aplicación.

### 1.2 Background
Aunque recientemente se implementaron los estándares globales de Floating Labels (vía CSS centralizado) y Tooltips (a través de `neuro_button` y `neuro_icon_action_button`), se ha reportado que **no se visualizan correctamente** en una lista extensa de módulos de la aplicación. Esto probablemente se deba a que dichos módulos utilizan componentes nativos (`rx.input`, `rx.select`, `rx.button`) en lugar de los componentes estandarizados del sistema de diseño (ej. `neuro_floating_input`, `neuro_button`).

### 1.3 Scope
**In Scope**:
- Auditoría técnica para identificar la causa de la ausencia de Tooltips y Floating Labels en los 14 módulos listados.
- Refactorización de las vistas de los módulos afectados para que consuman los componentes estándar (`neuro_elements.py` y `floating_label.py`).
- Módulos afectados: Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos, Desocupaciones, Incidentes, Seguros, Recibos Públicos, Saldos a Favor, Usuarios, Gestión de IPC / Incrementos, Reportes.

**Out of Scope**:
- Creación de nuevos componentes de diseño no especificados.
- Rediseño estructural de los formularios o vistas (solo se aplica reemplazo de componentes).

## 2. User Scenarios & Use Cases

### 2.1 Primary User Flow
1. El usuario navega a cualquiera de los 14 módulos listados (ej. Propiedades o Contratos).
2. El usuario observa un formulario de creación o edición. Los campos de texto y selección muestran etiquetas consistentes que flotan al recibir el foco o al contener información.
3. El usuario pasa el ratón (hover) sobre los botones de acción (guardar, editar, eliminar, etc.).
4. El sistema despliega un tooltip descriptivo con alta legibilidad y superposición correcta (z-index adecuado), guiando al usuario sobre la acción.

## 3. Functional Requirements

### 3.1 Auditoría e Ingeniería Inversa
- **FR-01**: El equipo debe analizar el código de los módulos mencionados para determinar por qué las implementaciones centralizadas (establecidas en `025-fix-ui-labels-tooltips`) no se están reflejando.
- **FR-02**: Se debe identificar si el problema radica en el uso de componentes `rx` heredados directos, o si hay sobrescrituras de estilos CSS.

### 3.2 Refactorización de Componentes de Formulario
- **FR-03**: Todos los inputs de texto y selectores en los módulos afectados deben ser refactorizados para utilizar `neuro_floating_input` y `neuro_floating_select` (o las directrices estándar actuales).
- **FR-04**: Las etiquetas flotantes deben comportarse reactivamente, moviéndose hacia el borde superior cuando el campo tiene foco o contenido.
- **FR-04b (Edge Case)**: En caso de encontrar componentes complejos (ej. date pickers) que no soporten las Floating Labels nativamente, se aplicará un estilo de fallback estático (placeholder o etiqueta fija) para no bloquear la migración y mantener la funcionalidad sin incurrir en reescrituras profundas.

### 3.3 Refactorización de Botones y Tooltips
- **FR-05**: Todos los botones de acción (especialmente iconos sin texto evidente) en los módulos deben utilizar `neuro_icon_action_button` o `neuro_button` y proveer la propiedad `tooltip_content`. Los textos de los tooltips serán generados de manera inferida y contextual (ej. "Guardar cambios", "Eliminar contrato") según el ícono y la función del botón, para garantizar consistencia sin requerir diccionarios previos.
- **FR-06**: El tooltip generado no debe quedar oculto bajo modales o tablas (garantizando el uso del `Z_TOOLTIP=1100`).

## Clarifications

### Session 2026-07-05
- Q: Estrategia de Contenido para Tooltips → A: Generación inferida (Contextual) - La IA asignará textos descriptivos estándar basados en el icono y la función.
- Q: Manejo de Inputs Complejos → A: Fallback estático (Placeholder) - Los componentes complejos usarán un estilo estandarizado sin animación flotante.

## 4. Non-Functional Requirements

### 4.1 UI/UX
- Debe cumplirse rigurosamente el **Claude/Anthropic Design System** especificado en la constitución del proyecto (colores, sombras, transiciones).

### 4.2 Maintainability
- Los módulos deben adherirse estrictamente al patrón "Clean Architecture Élite" y depender de los componentes centralizados en `src/presentacion_reflex/components/`, previniendo futura fragmentación visual.

## 5. Success Criteria

- **SC-01**: Al 100% de los formularios de los 14 módulos reportados se les implementan etiquetas flotantes reactivas.
- **SC-02**: Al 100% de los botones de acción principal y secundaria de los módulos se les implementan tooltips descriptivos.
- **SC-03**: La compilación de Reflex (`reflex export --frontend-only --no-zip`) no presenta errores tras las refactorizaciones masivas.

## 6. Assumptions & Dependencies

- **Assumptions**: 
  - La infraestructura de UI global (tokens en `styles.py`, `floating_label.py`) está funcional y correcta. El fallo actual es puramente un problema de adopción (componentes antiguos sin migrar).
- **Dependencies**: 
  - Depende de la correcta definición previa del sistema de diseño en `src/presentacion_reflex/components/neuro_elements.py`.
