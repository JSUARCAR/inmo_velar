# Contrato: Evento de generación masiva (UI)

**Evento**: `LiquidacionesState.generar_liquidacion_masiva(form_data: Dict)` — `@rx.event(background=True)`

## Entrada (`form_data`)

| Campo | Tipo | Regla |
|-------|------|-------|
| `periodo` | str `YYYY-MM` | Requerido; vacío ⇒ `ValueError("Debe seleccionar un período")` |

## Comportamiento garantizado

1. Itera todos los `ID_PROPIETARIO` con mandato ACTIVO + arriendo ACTIVO.
2. Al éxito: `show_bulk_create_modal = False`, `form_data = {}`, **`filter_periodo = periodo`**, **`current_page = 1`**, y **siempre** `yield load_liquidaciones()` (ambas vistas).
3. Toast resumen: `"{g} generadas / {o} ya existían / {n} no elegibles / {e} con error"` (+ hasta 3 motivos); `info` si `g==0, e==0, o>0`; `success` si `e==0`; `warning` si `e>0`; `error` si falló el lote.
4. Sin propietarios elegibles ⇒ `ValueError` + toast error, sin loading infinito.
5. Concurrencia: ejecuciones simultáneas permitidas; la restricción UNIQUE serializa de facto y la segunda cuenta duplicados como omitidas. Una carrera exacta sobre el mismo contrato+período cuenta como error transitorio reintentable.

## Concurrencia e Idempotencia (Análisis C1)

- **Ejecuciones concurrentes**: Si dos administradores disparan la generación masiva para el mismo período simultáneamente, la restricción `UNIQUE(ID_CONTRATO_M, PERIODO)` garantiza la idempotencia a nivel de base de datos sin necesidad de bloqueos globales.
- **Comportamiento ante duplicados**: La segunda ejecución detecta las liquidaciones existentes y las contabiliza como `omitidas`, reportando un toast informativo y evitando duplicados o estados corruptos.
- **Caso cero-elegibles**: Si ningún mandato cumple los criterios de elegibilidad para el período, el flujo aborta limpiamente arrojando `ValueError`, notificando vía toast y desactivando `is_loading` sin dejar la UI bloqueada.

## Permisos

Botón visible solo con `check_action("Liquidaciones", "CREAR")`.
