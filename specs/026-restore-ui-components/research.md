# Research & Technical Decisions

### Tooltip Text Strategy
- **Decision**: Usar textos generados contextual e inferidamente durante la refactorización (ej. "Editar [Módulo]", "Eliminar [Entidad]", "Ver detalles").
- **Rationale**: Agiliza la implementación sin sacrificar UX. Requerir un diccionario rígido habría bloqueado el proceso. La consistencia se garantiza usando un patrón verbo + sujeto.
- **Alternatives considered**: Textos genéricos mínimos ("Guardar") - rechazado por baja accesibilidad. Diccionarios pre-aprobados - rechazado por lentitud operativa.

### Manejo de Inputs Complejos (DatePickers/Autocompletes)
- **Decision**: Uso de placeholder estático tradicional en lugar de `floating-label`.
- **Rationale**: Los DatePickers y Selectores custom de Reflex/Radix interceptan las clases o no exponen la estructura de hermanos `input ~ label` que requiere CSS para el floating label puro. El estilo estático de placeholder mantiene la usabilidad del sistema.
- **Alternatives considered**: Sobrescribir wrappers React - rechazado por alto esfuerzo e interrupción de tareas UI estándar. Ignorar el campo - rechazado por pobre UX.
