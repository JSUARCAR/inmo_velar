# Diagnostic Report: Playwright Validation

**Feature**: playwright-validation
**Date**: 2026-07-03
**Target Environment**: `https://extraordinary-joy-production-2fd2.up.railway.app/`

## Executive Summary

Se ha implementado con éxito el arnés E2E en Playwright para validar los módulos de Incidentes y Liquidaciones, encapsulando las credenciales y aislando el entorno de pruebas. Sin embargo, durante la ejecución automatizada contra el entorno de producción, los tests fallaron en la fase de Setup (Login) impidiendo la validación funcional profunda de los flujos de negocio.

## Hallazgos (Findings)

### Finding 1: Fallo de Localización en el Formulario de Login (Bloqueante)

**Descripción**: El motor de automatización Playwright es incapaz de localizar el campo de contraseña mediante heurísticas de `placeholder` (buscando "Contraseña" o "Password").
**Causa Raíz Identificada**: 
Existen dos posibilidades según la arquitectura actual (Reflex):
1. **Divergencia del DOM**: Reflex podría no estar renderizando el atributo HTML `placeholder` en el input subyacente de Radix UI, o podría estar utilizando un label visual flotante que no se traduce en el atributo estándar.
2. **Latencia / Renderizado Diferido**: La aplicación puede estar tardando más de 30 segundos (Timeout por defecto) en compilar/servir el bundle inicial de React/Reflex en Railway, provocando que el DOM esté vacío al momento de la aserción.

**Impacto Funcional**: Impide el inicio de sesión automatizado y, por consiguiente, anula la posibilidad de validar E2E los módulos internos.
**Evidencia (Log de consola)**:
```text
playwright._impl._errors.TimeoutError: Locator.fill: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_placeholder(re.compile(r"Contrase.a|Password", re.IGNORECASE))
```

### Propuesta de Corrección Técnica

Alineado con los principios de Clean Code y robustez de UI:

1. **TestIDs Estrictos (Frontend)**: Se debe inyectar el atributo `id` o `data-testid` (ej: `id="password_input"`) en los componentes de login de Reflex. Evitar depender de textos visuales (placeholders/labels) para la automatización crítica de infraestructura.
2. **Healthcheck Pre-Login**: Implementar en `utils.py` una espera de un elemento persistente (ej: el logo de "Inmobiliaria Velar" en la página pública) antes de intentar llenar el formulario, asegurando que el framework React haya hidratado el DOM.

## Siguientes Pasos

1. Revisar el código del componente de Login en la rama principal y añadir `data-testid` explícitos.
2. Una vez aplicados, re-ejecutar `pytest tests/e2e/ --tracing on-first-retry` para capturar la traza y verificar los flujos de "Seleccionar Incidente", "Plan de Pago" y "Eliminación" en la propiedad Sandbox.
