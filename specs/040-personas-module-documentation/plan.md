# Implementation Plan: Manual de Usuario - Módulo Personas

**Branch**: `040-personas-module-documentation` | **Date**: 2026-07-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/040-personas-module-documentation/spec.md`

## Summary

Crear un manual de usuario empresarial completo para el módulo Personas de Inmobiliaria Velar, incluyendo documentación funcional detallada y 8-10 capturas de pantalla. El manual seguirá estándares MkDocs con Material for MkDocs, escrito 100% en español, con versionado por fecha y mantenimiento a cargo de los desarrolladores del módulo.

## Technical Context

**Language/Version**: Markdown (MkDocs-compatible)

**Primary Dependencies**: MkDocs, Material for MkDocs

**Storage**: Archivos en `docs/manual-usuario/modulos/personas.md`

**Testing**: Verificación manual de renderizado en MkDocs

**Target Platform**: Web (sitio estático MkDocs)

**Project Type**: Documentation

**Performance Goals**: N/A (documentación)

**Constraints**: 
- 100% español (consistente con constitución del proyecto)
- Seguir buenas prácticas de MkDocs y Material for MkDocs
- Solo funcionalidades UI visibles
- 8-10 capturas de pantalla moderadas

**Scale/Scope**: 1 módulo documentado (Personas), ~16 secciones, 12-15KB contenido

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| 100% Español | ✅ PASS | Todo el contenido en español |
| Clean Architecture | N/A | Documentación, no código |
| Documentation Maintenance | ✅ PASS | Responsable: desarrolladores del módulo |
| Zero Leaks | ✅ PASS | No se exponen credenciales en documentación |

## Project Structure

### Documentation (this feature)

```text
specs/040-personas-module-documentation/
├── plan.md              # Este archivo
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A para documentación)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
docs/
├── manual-usuario/
│   ├── modulos/
│   │   └── personas.md          # Archivo principal a actualizar
│   ├── inicio.md
│   ├── instalacion.md
│   └── preguntas-frecuentes.md
├── assets/
│   └── screenshots/
│       └── Personas/            # Directorio para capturas de pantalla
│           ├── README.md        # Instrucciones de captura
│           └── *.png            # Capturas (8-10 archivos)
├── manual-tecnico/
└── decisions/
```

**Structure Decision**: Documentación MkDocs existente. Se actualizará `personas.md` y se crearán capturas en `docs/assets/screenshots/Personas/`.

## Complexity Tracking

No aplica - tarea de documentación sin violaciones de constitución.

## Implementation Approach

### Fase 0: Investigación (research.md)

1. Analizar estructura existente de `personas.md` (171 líneas actuales)
2. Identificar funcionalidades UI del módulo desde código fuente
3. Definir estructura del manual (16 secciones)
4. Establecer estándares de escritura para manual de usuario

### Fase 1: Diseño y Contratos

1. **data-model.md**: Entidades documentadas (Persona, Rol, KPI, Auditoría)
2. **contracts/**: N/A - documentación no tiene interfaces externas
3. **quickstart.md**: Guía de validación del manual renderizado

### Fase 2: Tareas (tasks.md)

Generado por `/speckit.tasks` después de completar Phase 0 y 1.

## Deliverables

| Artefacto | Descripción | Estado |
|-----------|-------------|--------|
| `personas.md` | Manual completo actualizado | Pendiente |
| Capturas de pantalla | 8-10 imágenes PNG | Pendiente |
| `README.md` | Instrucciones de captura | Creado |
