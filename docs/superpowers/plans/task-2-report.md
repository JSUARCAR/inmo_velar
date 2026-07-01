# Task 2 Report

## What was implemented
Added the "Generar Paz y Salvo" button in `_tabla_acciones` within `src/presentacion_reflex/pages/contratos.py`. The button is conditionally rendered only when the contract status is not "ACTIVO" (`c.estado_contrato != "ACTIVO"`). It calls `PDFState.generar_certificado_paz_y_salvo` when clicked.

## What was tested and test results
- `python scripts/check_syntax.py src/presentacion_reflex/pages/contratos.py`: PASS
- `ruff check src/presentacion_reflex/pages/contratos.py src/presentacion_reflex/components/contratos/tarjeta_contrato.py`: PASS (All checks passed!)
- `black src/presentacion_reflex/pages/contratos.py src/presentacion_reflex/components/contratos/tarjeta_contrato.py`: PASS (2 files reformatted)

## Files changed
- `src/presentacion_reflex/pages/contratos.py`
- `src/presentacion_reflex/components/contratos/tarjeta_contrato.py` (Reformatted by black)

## Self-review findings
The integration exactly follows the brief requirements and syntax specifications. The `black` formatter adjusted the indentation appropriately across the components modified in tasks 1 and 2.
