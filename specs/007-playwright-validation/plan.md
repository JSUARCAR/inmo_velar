# Implementation Plan: playwright-validation

**Branch**: `007-playwright-validation` | **Date**: 2026-07-03 | **Spec**: [spec.md](file:///C:/Users/PC/OneDrive/Desktop/inmobiliaria%20velar/PYTHON-REFLEX/specs/007-playwright-validation/spec.md)

**Input**: Feature specification from `/specs/007-playwright-validation/spec.md`

## Summary

Implementación de scripts de automatización E2E utilizando Playwright en Python para validar en el entorno de producción (`https://extraordinary-joy-production-2fd2.up.railway.app/`) los flujos de "Plan de Pago en Incidentes", "Selección de Incidentes en Liquidaciones", y "Eliminar Liquidación" en un entorno seguro (Sandbox).

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `playwright`, `pytest-playwright`

**Storage**: N/A (Pruebas E2E sobre el entorno de producción)

**Testing**: `pytest` como runner, Playwright para assertions y navegación UI.

**Target Platform**: Web Browsers (Chromium preferido para pruebas E2E)

**Project Type**: Suite de pruebas End-to-End (E2E) integradas al repositorio actual.

**Performance Goals**: Tiempos de ejecución estables con esperas explícitas (waits) para evitar flakiness (tests inestables).

**Constraints**: Protección estricta de credenciales (Zero Leak Protocol), uso del entorno sandbox "Calle Falsa 123 - Test Renov" para evitar corrupción de datos reales.

**Scale/Scope**: 3 escenarios de prueba críticos, generación de trazas (traces), videos/screenshots ante fallos, y reporte de diagnóstico.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **10. VERIFICACIÓN EN NAVEGADOR Y UI (RUNTIME)**: Esta iniciativa implementa directamente el mandato de no confiar solo en el análisis estático, sino en el Runtime Verification usando un navegador real (Playwright).
- **4. HIGIENE Y SEGURIDAD (PROTOCOLO ZERO LEAK)**: Cero filtraciones de credenciales. Las credenciales de prueba deben pasarse mediante variables de entorno seguras (`.env`) o inyectarse sin dejar rastro en logs.
- **13. DEPURACIÓN SISTEMÁTICA**: El objetivo de estos tests es generar evidencia ("Evidencia como Dato") para triage sistemático en caso de hallar bugs.
- **Veredicto**: PASSED. El plan cumple al 100% con los principios de validación y control de calidad establecidos.

## Project Structure

### Documentation (this feature)

```text
specs/007-playwright-validation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Phase 1 output (Test contracts)
```

### Source Code (repository root)

```text
tests/
└── e2e/
    ├── conftest.py             # Configuración de pytest, fixtures de auth y trazas.
    ├── utils.py                # Helpers para login y navegación.
    ├── test_incidentes.py      # Casos de prueba para validación de Plan de Pago.
    └── test_liquidaciones.py   # Casos de prueba para Selección de incidentes y Eliminación.
```

**Structure Decision**: Se consolida la automatización dentro del directorio `tests/e2e/` (creándolo si no existe) para mantenerlo aislado de las pruebas unitarias y de integración.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

(Sin violaciones detectadas. La complejidad es mínima, puramente limitada a escribir tests y recolectar logs).
