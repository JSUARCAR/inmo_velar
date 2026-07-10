# Data Model: Dashboard Documentation

**Feature**: 039-dashboard-documentation  
**Date**: 2026-07-08  
**Status**: Complete

## Documentation Entities

### 1. Documentation Module

**Purpose**: Representa un módulo del sistema documentado

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identificador único del módulo (ej: "dashboard") |
| name | string | Nombre del módulo (ej: "Dashboard") |
| description | string | Descripción corta del módulo |
| version | string | Versión del módulo documentado |
| last_updated | date | Fecha de última actualización |

**Relationships**: 
- Contains → Sections (1:N)
- Contains → Screenshots (1:N)

### 2. Documentation Section

**Purpose**: Representa una sección del manual

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identificador único de la sección |
| title | string | Título de la sección |
| level | number | Nivel de encabezado (1-6) |
| content | markdown | Contenido de la sección |
| order | number | Orden de aparición |

**Relationships**:
- BelongsTo → Module (N:1)
- Contains → Subsections (1:N)

### 3. Screenshot

**Purpose**: Representa una captura de pantalla del sistema

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identificador único (ej: "01-dashboard-general") |
| filename | string | Nombre del archivo (ej: "01-dashboard-general.png") |
| path | string | Ruta relativa al archivo |
| alt_text | string | Texto alternativo para accesibilidad |
| caption | string | Descripción de la imagen |
| section_ref | string | Referencia a la sección asociada |

**Relationships**:
- BelongsTo → Module (N:1)
- ReferencedBy → Section (N:N)

### 4. Glossary Term

**Purpose**: Representa un término del glosario

| Field | Type | Description |
|-------|------|-------------|
| term | string | Término en español |
| definition | string | Definición del término |
| synonyms | list | Sinónimos o términos alternativos |

**Relationships**:
- ReferencedIn → Section (N:N)

### 5. FAQ Item

**Purpose**: Representa una pregunta frecuente

| Field | Type | Description |
|-------|------|-------------|
| question | string | Pregunta del usuario |
| answer | string | Respuesta detallada |
| category | string | Categoría (ej: "acceso", "filtros", "errores") |
| order | number | Orden de aparición |

**Relationships**:
- BelongsTo → Module (N:1)

### 6. Troubleshooting Entry

**Purpose**: Representa un caso de solución de problemas

| Field | Type | Description |
|-------|------|-------------|
| symptom | string | Síntoma observado |
| cause | string | Causa probable |
| solution | string | Solución paso a paso |
| priority | string | Prioridad (alta, media, baja) |

**Relationships**:
- BelongsTo → Module (N:1)

## Entity Relationships Diagram

```
┌─────────────────┐
│ Documentation   │
│ Module          │
└────────┬────────┘
         │
         ├──────────────────┬──────────────────┬──────────────────┐
         │                  │                  │                  │
         ▼                  ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Section         │  │ Screenshot      │  │ FAQ Item        │  │ Troubleshooting │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│ Subsection      │  │ Glossary Term   │
└─────────────────┘  └─────────────────┘
```

## Validation Rules

### Documentation Module
- `id` must be unique and lowercase
- `name` must be in Spanish
- `version` must follow semantic versioning

### Screenshot
- `filename` must match pattern `{number}-{name}.png`
- `alt_text` must be in Spanish
- `path` must be valid relative path

### Glossary Term
- `term` must be unique
- `definition` must be at least 10 characters

## State Transitions

### Documentation Lifecycle
```
Draft → Review → Approved → Published → Updated
```

### Screenshot Lifecycle
```
Captured → Anonymized (if needed) → Referenced → Updated
```

## Data Volume Assumptions

- **Module**: 1 per documentation task
- **Sections**: 15-20 per module
- **Screenshots**: 10-15 per module
- **Glossary Terms**: 10-20 per module
- **FAQ Items**: 5-10 per module
- **Troubleshooting**: 5-10 per module