# Quickstart: validar el fix de liquidación octubre 2026

Guía de validación end-to-end. Detalles de entidades en [data-model.md](data-model.md) y contratos en [contracts/](contracts/).

## Prerrequisitos

- `DATABASE_URL` de Railway en `.env` (solo lectura salvo pasos TEST).
- Python 3.12 con dependencias instaladas.
- Universo de referencia: 64 contratos elegibles detectados el 2026-10-14; las pruebas usan períodos `2099-*` que luego se borran.

## 1. Regresión unitaria (2 min)

```powershell
python -m pytest tests/aplicacion/test_servicio_financiero_elegibilidad.py tests/dominio/test_liquidacion_asesor.py -q
```

Esperado: 8 passed.

## 2. Estado pre-generación (solo lectura)

Consultar en PG: `COUNT(*) WHERE PERIODO='2026-10' AND eliminada=FALSE` debe ser 0 pre-fix; `2026-09` = 60 como testigo de que las consultas funcionan.

## 3. Prueba TEST aislada (período `2099-12`, luego borrar)

1. Elegir 1 contrato elegible sin liq en `2099-12`.
2. `generar_liquidacion_mensual(...)` ⇒ persiste con `En Proceso`.
3. `listar_liquidaciones_paginado(periodo='2099-12')` ⇒ total 1; `listar_liquidaciones_propietarios_paginado` ⇒ 1 grupo.
4. `generar_liquidacion_propietario` mismo propietario ⇒ `generadas=1, omitidas=0, errores=0`; segunda vez ⇒ `omitidas=1`.
5. Limpieza: `UPDATE CUOTA_INCIDENTE SET ID_LIQUIDACION=NULL`, borrar `INCIDENTE_LIQUIDACION`, `DELETE FROM LIQUIDACIONES WHERE PERIODO LIKE '2099%'`; verificar `COUNT = 0`.

## 4. Validación en UI y Sincronización de Filtro (Análisis C2)

- **Validación automatizada de estado Reflex**:
  Dado que Reflex restringe la instanciación directa de subclases de `rx.State` fuera del runtime web activo, la invariante de sincronización se verifica formalmente validando el AST/código fuente de `LiquidacionesState.generar_liquidacion_masiva.fn`:
  ```bash
  python -c "import inspect; from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState; src = inspect.getsource(LiquidacionesState.generar_liquidacion_masiva.fn); assert 'self.filter_periodo = periodo' in src and 'self.current_page = 1' in src and 'yield LiquidacionesState.load_liquidaciones()' in src; print('AST Sync OK')"
  ```
- **Validación interactiva en navegador**:
  Generar masiva para el período deseado desde la vista agrupada (permiso CREAR): el filtro debe saltar automáticamente al período generado, página 1, tabla recargada y toast con el resumen `{g} generadas / {o} ya existían / {n} no elegibles / {e} con error`. Re-ejecutar debe reportar omitidas, sin duplicar registros.

## 4b. Escenario de excepción y bordes de paginación

- **Cero elegibles**: Masiva en un universo donde ningún mandato califica (o sin contratos activos): debe abortar limpiamente arrojando `ValueError("No se encontraron propietarios con contratos de mandato activos")`, mostrando el toast de error respectivo y deshabilitando el spinner de carga sin entrar en bucle de loading infinito.
- **Bordes de paginación**:
  - `Total = 0`: La tabla muestra vista vacía con indicador de página y controles de navegación deshabilitados.
  - `Total = 25`: Una página completa sin botón "Siguiente" activo.
  - `Última página parcial (ej. 60 total)`: Página 3 con exactamente 10 registros.
  - *Diferimiento explícito*: Cualquier rediseño de componentes visuales de paginación queda diferido, dado que el repositorio (`repositorio_liquidacion_postgres.py`) aplica `LIMIT`/`OFFSET` matemáticamente exactos.

## 5. Criterio de aceptación

SC-001/003/004/005 del [spec.md](spec.md): ≥95% persistidos y visibles sin recarga manual, cero `KeyError`, cero filas `2099-*`, tests en verde.
