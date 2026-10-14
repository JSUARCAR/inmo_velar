# Data Model: Liquidación Propietarios Octubre 2026

**Feature**: [spec.md](spec.md) | Fuente: `repositorio_liquidacion_postgres.py`, `liquidacion.py`, `resultado_generacion.py`

Sin cambios de esquema: el fix no agrega tablas ni columnas. Entidades y reglas tocadas:

## Liquidación (`LIQUIDACIONES`)

- Clave: `ID_LIQUIDACION` (autoincremental / `RETURNING` en PG).
- Identidad de negocio: `UNIQUE(ID_CONTRATO_M, PERIODO)` — base de la idempotencia (duplicado → omitida, nunca error).
- `PERIODO TEXT NOT NULL`, formato `YYYY-MM` exacto; estado inicial `En Proceso`.
- `ESTADO_LIQUIDACION ∈ {En Proceso, Aprobada, Pagada, Cancelada}`; transiciones: En Proceso→Aprobada→Pagada; Aprobada→En Proceso (reversar); cualquiera no-Pagada→Cancelada.
- Soft-delete: `eliminada` (todas las consultas filtran `eliminada = FALSE`).
- Relaciones: `ID_CONTRATO_M → CONTRATOS_MANDATOS`; cuotas en `CUOTA_INCIDENTE.ID_LIQUIDACION` (desasociar con NULL antes de borrado físico TEST).

## Elegibilidad (derivada, no persistida)

- Contrato genera ⟺ `CONTRATOS_MANDATOS.ESTADO_CONTRATO_M = ACTIVO` **y** existe `CONTRATOS_ARRENDAMIENTOS` ACTIVO en la misma `ID_PROPIEDAD`.
- Sin arriendo ⇒ `no_elegible` con motivo, sin persistir, sin bloquear al resto.

## ResultadoGeneracionPropietario

- Agregado `{generadas, omitidas, errores, no_elegibles, detalles_no_elegibles}` por propietario; la masiva los suma para el toast.
- `ValueError("Ya existe una liquidación para el período {periodo}")` ⇒ omitida; `LiquidacionNoElegibleError` ⇒ no_elegible; resto ⇒ error.

## Estado Frontend (`LiquidacionesState`)

- `filter_periodo` (`""`/`"Todos"` = sin filtro), `vista_agrupada`, `current_page`, `page_size = 25`.
- Invariante post-masiva (nuevo): `filter_periodo == periodo_generado`, `current_page == 1`, tabla recargada en ambas vistas.

## Volúmenes de referencia

- 79 mandatos activos, 64 arriendos activos, 64 contratos elegibles, 50 propietarios, 60 liqs en `2026-09`, 0 en `2026-10` (pre-fix).
