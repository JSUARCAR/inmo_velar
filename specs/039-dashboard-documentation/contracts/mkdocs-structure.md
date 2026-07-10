# MkDocs Structure Contract

**Feature**: 039-dashboard-documentation  
**Date**: 2026-07-08  
**Status**: Complete

## Overview

Define la estructura y formato del archivo de documentación `dashboard.md` para garantizar compatibilidad con MkDocs y Material for MkDocs theme.

## File Structure Contract

### Required Sections

| Section | Level | Required | Description |
|---------|-------|----------|-------------|
| # Dashboard | H1 | Yes | Título principal del módulo |
| ## 1. Introducción | H2 | Yes | Introducción al módulo |
| ### Objetivo | H3 | Yes | Propósito del módulo |
| ### Alcance | H3 | Yes | Alcance funcional |
| ### Beneficios | H3 | Yes | Beneficios para el usuario |
| ### Casos de uso | H3 | Yes | Casos de uso principales |
| ## 2. Conceptos Básicos | H2 | Yes | Definiciones y glosario inicial |
| ## 3. Acceso | H2 | Yes | Instrucciones de acceso |
| ## 4. Interfaz de Usuario | H2 | Yes | Descripción de la interfaz |
| ## 5. Funcionalidades | H2 | Yes | Funcionalidades detalladas |
| ## 6. Flujo Operativo | H2 | Yes | Flujos de trabajo |
| ## 7. Reglas de Negocio | H2 | Yes | Reglas del sistema |
| ## 8. Validaciones | H2 | Yes | Reglas de validación |
| ## 9. Casos Prácticos | H2 | Yes | Ejemplos prácticos |
| ## 10. Buenas Prácticas | H2 | Yes | Recomendaciones de uso |
| ## 11. Preguntas Frecuentes | H2 | Yes | FAQ |
| ## 12. Solución de Problemas | H2 | Yes | Troubleshooting |
| ## 13. Glosario | H2 | Yes | Glosario de términos |
| ## 14. Referencias | H2 | Yes | Referencias adicionales |
| ## 15. Registro de Cambios | H2 | Yes | Changelog |

### Content Format Rules

#### Headings
- H1: Only one per file (module title)
- H2: Main sections (numbered 1-15)
- H3: Subsections within main sections
- H4-H6: Use sparingly for deep nesting

#### Admonitions (Material for MkDocs)

```markdown
> [!NOTE] Title
> Content for note

> [!IMPORTANT] Title
> Important information

> [!TIP] Title
> Helpful tip

> [!WARNING] Title
> Warning information

> [!CAUTION] Title
> Caution information
```

#### Tables

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
```

#### Images

```markdown
![Alt text in Spanish](../../assets/screenshots/Dashboard/filename.png)
*Caption in Spanish*
```

#### Code Blocks

````markdown
```
plain code block
```

```python
# language-specific
```
````

#### Lists

- Unordered list items
- Use `-` for consistency
- Nest with 2 spaces

1. Ordered list items
2. Use numbers

#### Links

```markdown
[Link text](relative-path.md)
[External link](https://example.com)
```

## Validation Checklist

### File Validation
- [ ] File exists at `docs/manual-usuario/modulos/dashboard.md`
- [ ] File is valid Markdown
- [ ] File uses UTF-8 encoding
- [ ] File has consistent line endings (LF)

### Content Validation
- [ ] All 15 required sections present
- [ ] Headings follow hierarchy (no skipped levels)
- [ ] Tables have proper header separator
- [ ] Images have alt text in Spanish
- [ ] Admonitions use correct syntax
- [ ] No broken relative links

### MkDocs Compatibility
- [ ] File builds with `mkdocs build --strict`
- [ ] No warnings in build output
- [ ] All images are accessible
- [ ] All links are valid

## Screenshot References

### Required Screenshots

| ID | Filename | Section | Alt Text |
|----|----------|---------|----------|
| 1 | 01-dashboard-general.png | 4. Interfaz de Usuario | "Vista general del Dashboard" |
| 2 | 02-filtros.png | 5.2 Usar Filtros | "Barra de filtros del Dashboard" |
| 3 | 03-kpi-estrategicos.png | 5.1 Visualizar Indicadores | "Tarjetas KPI estratégicos" |
| 4 | 04-pulso-operativo.png | 5.4 Interpretar Pulso Operativo | "Pulso Operativo del Dashboard" |
| 5 | 05-evolucion-recaudo.png | 5.5.1 Evolución del Recaudo | "Gráfico de Evolución del Recaudo" |
| 6 | 06-vencimientos-chart.png | 5.5.2 Vencimientos | "Gráfico de Vencimientos por Período" |
| 7 | 07-propiedades-tipo.png | 5.5.3 Propiedades por Tipo | "Gráfico de Propiedades por Tipo" |
| 8 | 08-incidentes.png | 5.5.4 Incidentes | "Gráfico de Incidentes por Estado" |
| 9 | 09-top-asesores.png | 5.5.5 Top Asesores | "Gráfico de Top Asesores" |
| 10 | 10-tunel-vencimientos.png | 5.5.6 Túnel de Vencimientos | "Gráfico de Túnel de Vencimientos" |
| 11 | 11-tabla-vencimientos.png | 5.6 Revisar Tabla | "Tabla de Vencimientos Consolidados" |
| 12 | 12-estado-carga.png | 7. Reglas de Negocio | "Estado de carga del Dashboard" |

### Image Path Pattern

```
../../assets/screenshots/Dashboard/{filename}
```

Relative from: `docs/manual-usuario/modulos/`

## Style Guide

### Terminology
- Use "Dashboard" (capitalized) when referring to the module
- Use "panel de control" (lowercase) when describing generically
- Use "KPI" (uppercase) for Key Performance Indicator
- Use "Asesor" (capitalized) for advisor role

### Formatting
- Bold for UI element names: **Botón "Actualizar"**
- Code for technical terms: `dashboard:read`
- Italics for emphasis (sparingly)
- No ALL CAPS except acronyms

### Numbers
- Use commas for thousands: 1.000
- Use periods for decimals: 99,5%
- Currency: $ followed by amount: $1.234.567

### Dates
- Format: DD/MM/YYYY
- Example: 08/07/2026