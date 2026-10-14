# Contrato: Servicio de generación por propietario

**Método**: `ServicioFinanciero.generar_liquidacion_propietario(id_propietario: int, periodo: str, datos_adicionales_por_contrato: Optional[Dict], usuario_sistema: str) -> ResultadoGeneracionPropietario`

## Entrada

| Campo | Tipo | Regla |
|-------|------|-------|
| `id_propietario` | int > 0 | Debe existir con mandatos activos; sin mandatos ⇒ `{0,0,0}` |
| `periodo` | str `YYYY-MM` | Exacto, sin trim implícito (CHK008 pendiente) |
| `datos_adicionales_por_contrato` | dict \| None | Clave por `ID_CONTRATO_M`; `None` = defaults |
| `usuario_sistema` | str | Auditoría `CREATED_BY` |

## Salida

`ResultadoGeneracionPropietario(generadas, omitidas, errores, no_elegibles, detalles_no_elegibles)` — nunca lanza por contratos individuales (cada fallo se cuenta); solo falla si la consulta de contratos falla.

## Invariantes

- Compatible con claves dict en MAYÚSCULAS (PG) y minúsculas (SQLite/tests).
- Idempotente: re-ejecución ⇒ `omitidas` (UNIQUE), sin duplicados.
- Sin arriendo ⇒ `no_elegibles += 1` con detalle `"{direccion}: sin contrato de arrendamiento activo en esta propiedad"`.

## Alcance de lectura y semántica de filtro (Nota LIKE vs =)

La recuperación por período la rige FR-005 y queda documentada de la siguiente manera:
- **Vista Individual**: Utiliza coincidencia de patrón `LIKE '%{periodo}%'` en SQL (`repositorio_liquidacion_postgres.py:listar_paginado`).
- **Vista Agrupada por Propietario**: Utiliza coincidencia exacta `= %s` en SQL (`repositorio_liquidacion_postgres.py:listar_agrupadas_por_propietario_paginado`).
- **Preservación intencional**: Conforme a la clarificación Q3 y FR-005, ambas semánticas se preservan intactas sin cambios para garantizar retrocompatibilidad y refactorización incremental.
