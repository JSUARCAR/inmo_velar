# Floating Labels en Filtros Avanzados

## Overview

Reemplazar los placeholders tradicionales por etiquetas visibles (labels) permanentes en todos los campos de la sección de Filtros Avanzados del sistema. El nombre del campo debe permanecer visible incluso después de que el usuario ingrese un valor, mejorando la claridad, usabilidad y accesibilidad de la interfaz.

## User Scenarios & Testing

### Primary User Flow

1. El usuario navega a una sección del sistema que contiene filtros avanzados (Dashboard, Reportes, Listados)
2. Observa cada campo de filtro con su etiqueta visible permanentemente mostrada
3. Al hacer clic en un campo para ingreser datos, la etiqueta se desplaza suavemente hacia arriba (patrón Floating Label)
4. El nombre del campo permanece visible en todo momento, incluso con datos ingresados
5. El usuario puede identificar claramente qué contiene cada campo sin depender de la memoria

### Acceptance Scenarios

- **Given** el usuario visualiza un campo de filtro, **When** el campo está vacío, **Then** la etiqueta se muestra en su posición normal
- **Given** el usuario ingresa un valor en el campo, **When** el campo contiene datos, **Then** la etiqueta se desplaza hacia arriba y permanece visible
- **Given** el usuario hace clic en un campo, **When** recibe foco, **Then** la etiqueta se anima suavemente hacia arriba
- **Given** el usuario elimina el contenido del campo, **When** el campo queda vacío, **Then** la etiqueta regresa a su posición original

### Edge Cases

- Campos con valores preseleccionados (ej: "Todos los asesores") deben mostrar la etiqueta en posición superior desde el inicio
- Campos de tipo select/dropdown deben aplicar el mismo patrón de etiqueta flotante
- En dispositivos móviles, las etiquetas deben ser legibles y no interferir con el teclado virtual
- Estados de error deben mantener la etiqueta visible, cambiando su color a `var(--red-9)` para indicar validación fallida

## Requirements

### Functional Requirements

- **FR-01**: Cada campo de filtro debe tener una etiqueta visible que identifique su contenido
- **FR-02**: La etiqueta debe desplazarse hacia arriba cuando el campo recibe foco o contiene datos
- **FR-03**: La etiqueta nunca debe desaparecer ni ser reemplazada únicamente por un placeholder
- **FR-04**: El patrón Floating Label debe ser consistente en todos los campos de formulario del sistema
- **FR-05**: Las transiciones de la etiqueta deben ser suaves, durar entre 150-300ms y usar curva `cubic-bezier(0.4, 0, 0.2, 1)`
- **FR-06**: Los campos con valores preseleccionados deben mostrar la etiqueta en posición superior
- **FR-07**: El componente debe ser accesible mediante navegación por teclado
- **FR-08**: Los lectores de pantalla deben anunciar correctamente el nombre del campo
- **FR-09**: En estado de error, la etiqueta debe cambiar su color a `var(--red-9)` manteniendo la legibilidad

### Design Requirements

- **DR-01**: La etiqueta debe usar el mismo sistema de diseño neumórfico existente
- **DR-02**: El tamaño de fuente de la etiqueta debe ser consistente con el sistema tipográfico actual
- **DR-03**: Los colores deben respetar la paleta de colores definida en el proyecto
- **DR-04**: El espacio entre la etiqueta y el campo debe ser consistente en todos los formularios

## Success Criteria

### Quantitative Metrics

- Tiempo de identificación de campo: El usuario debe poder identificar un campo en menos de 1 segundo
- Tasa de errores de ingreso: Reducción del 30% en errores de datos ingresados en campos incorrectos
- Tiempo de completado de formulario: Reducción del 20% en tiempo para completar filtros

### Qualitative Measures

- Los usuarios reportan mayor claridad en la identificación de campos
- La interfaz se percibe más profesional y consistente
- Mejora en la accesibilidad para usuarios con discapacidades visuales

## Key Entities

- **Campo de Filtro**: Elemento de formulario que permite al usuario filtrar datos
- **Etiqueta Flotante (Floating Label)**: Texto descriptivo que se desplaza al recibir foco
- **Estado del Campo**: Representa si el campo está vacío, con foco, o con datos

## Clarifications

### Session 2026-07-05

- Q: ¿Qué curva de easing debe usar la transición de la etiqueta flotante? → A: `cubic-bezier(0.4, 0, 0.2, 1)` (estándar Material Design, convención del proyecto)
- Q: ¿Cómo debe comportarse visualmente la etiqueta en estado de error? → A: Cambiar color de etiqueta a `var(--red-9)` (rojo semántico del sistema)

## Assumptions

- El sistema actual utiliza placeholders que desaparecen al ingresar datos
- Los componentes de formulario existentes siguen el diseño neumórfico del proyecto
- La implementación debe ser compatible con la versión actual de Reflex
- No se requiere soporte para navegadores muy antiguos (IE11)

## Scope

### In Scope

- Campos de formulario en la sección de Filtros Avanzados
- Campos de formulario en Dashboard principal
- Campos de formulario en módulos de Reportes
- Componente reutilizable para todos los formularios del sistema

### Out of Scope

- Modificación de la lógica de filtrado existente
- Cambios en la estructura de datos subyacente
- Modificación de estilos globales del sistema (solo componentes de formulario)
