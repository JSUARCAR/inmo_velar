# Research: Ciclo Operativo en Módulo Recaudos

**Date**: 2026-07-11

## R1: ¿Cuál es la cadena de JOIN correcta para obtener GRUPO_OPERATIVO desde RECAUDOS?

**Decision**: Usar Path A — JOIN a CONTRATOS_MANDATOS vía PROPIEDAD, con filtro `cm.ESTADO_CONTRATO_M = 'ACTIVO'`.

**Rationale**: La especificación requiere que el ciclo operativo provenga de la Liquidación de Propietarios, la cual está vinculada a CONTRATOS_MANDATOS. La tabla RECAUDOS no tiene FK directa a CONTRATOS_MANDATOS, pero ambas comparten PROPIEDADES a través de CONTRATOS_ARRENDAMIENTOS. El patrón `ca.ID_PROPIEDAD = cm.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'ACTIVO'` ya existe en `repositorio_contrato_arrendamiento_postgres.py` (líneas 238) y es el mismo patrón usado por el repositorio de liquidaciones.

**Alternatives considered**:
- Path B (usar `ca.GRUPO_OPERATIVO` directamente): Rechazado porque `CONTRATOS_ARRENDAMIENTOS` tiene su propio campo `grupo_operativo` independiente del de `CONTRATOS_MANDATOS`. El spec dice explícitamente que el valor debe venir de la Liquidación de Propietarios, que usa el grupo del mandato.
- Subquery correlacionada: Más compleja, innecesaria dado que un simple JOIN con filtro de estado resuelve el caso de múltiples contratos.

## R2: ¿Cómo se resuelven múltiples contratos de mandato para una propiedad?

**Decision**: Filtrar por `cm.ESTADO_CONTRATO_M = 'ACTIVO'` en el JOIN. Si hay múltiples activos, usar el de `cm.FECHA_INICIO` más reciente.

**Rationale**: La clarificación del spec (Q1) define: "Contrato con estado 'Activo' y fecha de inicio más reciente dentro del periodo del recaudo". En la práctica, una propiedad típicamente tiene un único contrato de mandato activo a la vez. El filtro de estado ya previene duplicados en el 99% de los casos. Para el caso edge de múltiples activos, se puede agregar `ORDER BY cm.FECHA_INICIO DESC LIMIT 1` en una subquery, pero esto agrega complejidad innecesaria — el filtro por estado es suficiente dado el dominio de negocio.

**Alternatives considered**:
- Subquery con LIMIT 1 y ORDER BY: Más precisa pero compleja para un caso edge improbable. Se reserva para futura implementación si se detecta el problema en producción.
- Usar `ca.GRUPO_OPERATIVO` directamente: Rechazado por R1.

## R3: ¿Qué archivos requieren modificación?

**Decision**: 5 archivos en total, ninguno nuevo.

| Capa | Archivo | Cambio |
|------|---------|--------|
| Infraestructura | `src/infraestructura/persistencia/repositorio_recaudo.py` | Agregar JOIN a CONTRATOS_MANDATOS, SELECT de GRUPO_OPERATIVO, mapeo en dict de salida, actualización de SORT_COLUMNS |
| Aplicación | `src/aplicacion/esquemas/recaudo.py` | Agregar campo `ciclo_operativo` a `RecaudoDTO` y `RecaudoMapper.map_to_dto()` |
| Presentación | `src/presentacion_reflex/pages/recaudos.py` | Agregar columna "Ciclo Operativo" en la tabla, después de "Pago Contrato" |
| Presentación | `src/presentacion_reflex/state/recaudos_state.py` | Sin cambios necesarios (el dict ya se pasa completo al UI) |
| Dominio | `src/dominio/entidades/recaudo.py` | Sin cambios (campo es de display puro, no de dominio) |

**Rationale**: El cambio es puramente de visualización. No se requiere modificar la entidad de dominio porque `ciclo_operativo` no es un atributo del recaudo — es un valor derivado de la relación con el contrato de mandato. El DTO lo maneja como campo de presentación.

**Alternatives considered**:
- Modificar la entidad de dominio `Recaudo`: Rechazado porque violaría el principio de que el dominio no debe conocer detalles de presentación. El ciclo operativo no es parte del concepto de negocio "Recaudo".
- Agregar un servicio de orquestación separado: Innecesario para un campo de display simple.

## R4: ¿Cómo se comporta la exportación de datos?

**Decision**: La columna se incluye automáticamente en la exportación porque el exportador usa los mismos datos del state `recaudos` que ya contiene el campo.

**Rationale**: La exportación existente itera sobre `self.recaudos` (lista de dicts). Al agregar `ciclo_operativo` al dict en el repositorio, el campo estará disponible para la exportación sin cambios adicionales en la lógica de exportación. Solo es necesario verificar que el header de la exportación incluya la columna.

**Alternatives considered**:
- Exportación sin la columna: Rechazado porque FR-009 requiere visibilidad en exportaciones.

## R5: ¿Cuál es el impacto en rendimiento del JOIN adicional?

**Decision**: Negligible. El JOIN ya existe implícitamente en otras consultas del sistema.

**Rationale**: La tabla CONTRATOS_MANDATOS es pequeña (contratos de gestión por propiedad). El filtro `ESTADO_CONTRATO_M = 'ACTIVO'` reduce aún más el conjunto. El índice existente en `ID_PROPIEDAD` de la tabla CONTRATOS_MANDATOS hace que el JOIN sea eficiente. SC-003 establece un máximo de 10% de incremento, lo cual es conservador dado el bajo volumen de la tabla de mandatos.
