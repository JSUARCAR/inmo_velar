# Task 2 Report: Auditoría de Usos Residuales de AGE() en el Repositorio

## Status: ✅ DONE

## Resumen

Se verificaron los 3 usos de `AGE()` en `repositorio_dashboard.py` dentro del método `obtener_contratos_elegibles_ipc`. Todos extraen `YEAR` (años completos para cálculo IPC), no `DAY`, por lo que son **semánticamente correctos** y no presentan el bug documentado en ADR-0010.

## Cambio Realizado

Se añadió un comentario SQL inline (2 líneas, estilo `--`) dentro del query PostgreSQL, justo antes de los campos que usan `AGE()`:

```sql
-- NOTA: AGE() aquí es correcto: extraemos YEAR (años completos),
-- no DAY (días totales). Ver ADR-0010.
```

## Verificación

| Check | Resultado |
|-------|-----------|
| `ruff check` | ✅ All checks passed! |
| `black --check` | ✅ 1 file would be left unchanged |

## Commit

- `62653ba` — `docs(dashboard): anotar uso correcto de AGE en calculo IPC ref ADR-0010`

## Archivo Modificado

- [repositorio_dashboard.py](file:///C:/Users/PC/OneDrive/Desktop/inmobiliaria%20velar/PYTHON-REFLEX/src/infraestructura/persistencia/repositorio_dashboard.py#L361-L362)
