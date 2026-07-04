# Quickstart Validation Guide

**Feature**: playwright-validation
**Date**: 2026-07-03

Esta guía detalla cómo ejecutar localmente las pruebas automatizadas de Playwright apuntando al entorno de producción para validar la funcionalidad.

## Prerequisites

1. Python 3.11+ instalado.
2. Navegadores de Playwright descargados (`playwright install chromium`).
3. Librerías instaladas: `pytest-playwright`.
4. Variables de entorno listas con las credenciales.

## Setup

Abre tu terminal en la raíz del proyecto y asegura que tu entorno virtual esté activo:

```bash
# Instalar dependencias si faltan
pip install pytest-playwright
playwright install chromium
```

Configura las variables de entorno temporalmente para la sesión (Windows PowerShell):
```powershell
$env:PLAYWRIGHT_TEST_USER="jsuarcar"
$env:PLAYWRIGHT_TEST_PASSWORD="velarjoan2026"
```

## Ejecutar Casos de Prueba

**1. Ejecución Completa con Modo Debug Visual (UI)**
Si deseas ver cómo se abren las pestañas y los clics:
```bash
pytest tests/e2e/ --headed --slowmo 500
```
*(Espera que todos los tests pasen y veas las interacciones de los modales).*

**2. Ejecución Completa Silenciosa con Captura de Trazas (Para Triage)**
Si deseas recolectar evidencia de red y consola en caso de fallo:
```bash
pytest tests/e2e/ --tracing on-first-retry -v
```

## Validación por Escenarios Específicos

**Validar únicamente el Plan de Pago en Incidentes:**
```bash
pytest tests/e2e/test_incidentes.py::test_visualizacion_plan_pago --headed
```

**Validar la Selección de Incidentes:**
```bash
pytest tests/e2e/test_liquidaciones.py::test_modal_seleccion_incidentes --headed
```

**Validar la Eliminación de Liquidación (Prueba Destructiva en Sandbox):**
```bash
pytest tests/e2e/test_liquidaciones.py::test_eliminar_liquidacion_sandbox --headed
```

## Análisis de Resultados

Si algún test falla, Playwright generará el reporte en un directorio como `test-results/`.
Para visualizar la traza que incluye logs de red y snapshots del DOM:

```bash
playwright show-trace test-results/path-al-archivo-trace.zip
```
