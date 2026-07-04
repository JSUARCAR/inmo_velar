# Implementation Plan: playwright-prod-diag

**Branch**: `[008-playwright-prod-diag]` | **Date**: 2026-07-03 | **Spec**: [specs/008-playwright-prod-diag/spec.md](specs/008-playwright-prod-diag/spec.md)

**Input**: Feature specification from `specs/008-playwright-prod-diag/spec.md`

## Summary

Desarrollo de un script de diagnóstico funcional y de red (E2E) utilizando Playwright (Python) en modo visible (headed) para interactuar con el entorno de producción en Railway y descubrir asimetrías con el entorno local relacionadas a flujos del módulo de Incidentes y Liquidaciones.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `playwright`, `pytest-playwright`

**Storage**: Local JSON/TXT logs temporales para reporte de red y consola.

**Testing**: Pytest

**Target Platform**: Navegador Web (Chromium) / Aplicación en Railway

**Project Type**: Script de Diagnóstico / Testing E2E

**Performance Goals**: N/A

**Constraints**: Debe ejecutarse en modo `headed=True`. No debe mutar datos reales salvo en propiedades Sandbox. Las credenciales deben ser pasadas por variables de entorno para cumplir el protocolo Zero Leak.

**Scale/Scope**: 3 escenarios de prueba (Plan de Pago, Seleccionar Incidentes, Eliminar Liquidación).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Zero Leak**: Validado. Las contraseñas proporcionadas en el prompt (`velarjoan2026`) no serán hardcodeadas en el script de prueba. Se requerirá usar `os.environ.get("PLAYWRIGHT_PROD_USER")` para inyectar credenciales.
- **Calidad de Código**: Validado. El script será un caso de prueba independiente alojado en un directorio aislado (ej. `tests/diagnostics/`).
- **Estado final**: PASS. No hay violaciones injustificadas.

## Project Structure

### Documentation (this feature)

```text
specs/008-playwright-prod-diag/
├── plan.md              
├── research.md          
├── data-model.md        
├── quickstart.md        
└── tasks.md             # (To be generated later)
```

### Source Code (repository root)

```text
tests/
└── diagnostics/
    ├── conftest.py             # Fixture para autenticación y captura de red
    └── test_prod_diag.py       # Los 3 escenarios de diagnóstico
```

**Structure Decision**: El código se alojará en un subdirectorio aislado `tests/diagnostics/` para no interferir con las pruebas E2E estándar del pipeline de CI/CD, ya que es una herramienta de ingeniería inversa de uso ad-hoc.
