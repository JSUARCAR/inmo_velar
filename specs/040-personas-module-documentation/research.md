# Research: Manual de Usuario - Módulo Personas

**Date**: 2026-07-08

## Summary

Investigación completada para la creación del manual de usuario del módulo Personas. Se analizó el código fuente, la estructura UI existente y las mejores prácticas de documentación MkDocs.

## Research Findings

### 1. Estructura UI del Módulo Personas

**Decision**: Documentar 16 secciones principales

**Rationale**: Análisis del código reveló las siguientes funcionalidades:
- Header con KPIs (5 roles: Propietario, Arrendatario, Asesor, Codeudor, Proveedor)
- Barra de filtros avanzados (rol, fechas, búsqueda, toggles)
- Dos modos de vista (tabla y cards)
- Wizard de 3 pasos para creación
- Modal de detalles con auditoría
- Paginación
- Exportación CSV

**Alternatives Considered**:
- Documentación minimalista (8 secciones) → Rechazada: insuficiente para manual empresarial
- Documentación exhaustiva (20+ secciones) → Rechazada: excesiva para alcance definido

### 2. Estándares de Escritura

**Decision**: Adoptar estilo de manual de usuario empresarial

**Rationale**: Basado en buenas prácticas MkDocs y Material for MkDocs:
- Títulos claros y descriptivos
- Tablas para información estructurada
- Notas, advertencias y tips con syntax de MkDocs
- Diagramas Mermaid para flujos
- Secciones colapsables para FAQ
- Imágenes con descripción alternativa

**Alternatives Considered**:
- Estilo técnico/desarrollador → Rechazado: público objetivo es usuario final
- Estilo académico → Rechazado: demasiado formal para software empresarial

### 3. Estrategia de Capturas de Pantalla

**Decision**: 8-10 capturas moderadas

**Rationale**: Balance entre claridad visual y mantenibilidad:
- Vista general del módulo
- KPIs de roles
- Filtros avanzados
- Vista de tabla
- Vista de cards
- Wizard de creación (paso 2: roles)
- Modal de detalles
- Paginación

**Alternatives Considered**:
- Mínimo (4-5) → Rechazado: insuficiente para comprensión visual
- Completo (12+) → Rechazado: excesivo para mantenimiento

### 4. Formato de Archivo

**Decision**: Markdown con frontmatter MkDocs

**Rationale**: Compatibilidad directa con MkDocs:
- Extensión `.md`
- Frontmatter para metadatos
- Syntax compatible con Material for MkDocs
- Soporte para admoniciones (note, warning, tip, important)

**Alternatives Considered**:
- RST (reStructuredText) → Rechazado: MkDocs usa Markdown
- HTML → Rechazado: menos mantenible

### 5. Localización

**Decision**: Solo español

**Rationale**: 
- Constitución del proyecto: "100% ESPAÑOL"
- Público objetivo: usuarios hispanohablantes
- Consistencia con resto de documentación

**Alternatives Considered**:
- Bilingüe → Rechazado: incrementa esfuerzo sin necesidad actual
- Español con glosario inglés → Rechazado: innecesario para alcance

## Conclusions

Todas las áreas de investigación resueltas. No quedan NEEDS CLARIFICATION.

**Artifacts Generated**:
- research.md (este archivo)
- plan.md (plan de implementación)

**Ready for Phase 1**: Sí - proceder con data-model.md y quickstart.md
