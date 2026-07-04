# Research & Technical Decisions: fix-prod-diag-bugs

## 1. Paginación Server-Side en Reflex (Saturación Websocket)

- **Problema**: `Disconnect websocket on page navigation` ocurre al intentar enviar listas masivas (cientos de registros) desde el backend FastAPI/Reflex al cliente por WebSocket, saturando el límite de carga.
- **Decision**: Implementar Paginación Offset/Limit en la base de datos y un componente simple de control en la UI.
- **Rationale**: Es el enfoque más resiliente para escalabilidad. Mover la carga completa de datos al backend e invocar un bloque pequeño en el evento de carga (por ejemplo 20 ítems).
- **Alternatives considered**: Lazy loading en el frontend o Virtualized Lists. Estas opciones requieren enviar los datos o usar librerías JS envueltas complejas. Limit/offset nativo es más alineado a la Clean Architecture y SQL nativo.

## 2. Manejo de Nulos Históricos y Backfill (Caída del Modal)

- **Problema**: El modal "Editar Liquidación" nunca se abre tras el click. El evento de UI despacha la mutación, pero crashea al hidratar el DTO por la ausencia de datos en campos recién introducidos.
- **Decision**: Escribir un script SQL/Python (script `saneamiento_liquidaciones.py`) que parchee los registros históricos vacíos con valores por defecto y simultáneamente cambiar los esquemas de Pydantic para prever `Optional[T]` o `default=""` de manera defensiva.
- **Rationale**: Protege el tiempo de ejecución (runtime) contra fallos inyectados por datos y reestablece la consistencia del catálogo en DB, matando el bug por ambos frentes.
- **Alternatives considered**: Solo cambiar el frontend. Descartado porque la DB seguiría sucia y afectaría reportes futuros.

## 3. Resolución de Bloqueo de Punteros (Pointer-Events Radix)

- **Problema**: Radix UI inserta capas Dismissable (como Popovers o Dialogs) en un Portal al final del body que interceptan eventos del ratón, y Reflex a veces no limpia la regla CSS `pointer-events: none` del body u otros contenedores al desmontar.
- **Decision**: Aplicar un override explícito en `src/presentacion_reflex/styles.py` (`BASE_STYLE`): `"rx.dialog.content": {"pointer_events": "auto"}` y `"rx.popover.content": {"pointer_events": "auto"}`.
- **Rationale**: Este enfoque sigue exactamente el lineamiento de la regla 16 del `constitution.md`. Centralizar esto previene futuras regresiones.
- **Alternatives considered**: Aplicar un estilo inline a cada botón afectado. Descartado por ser tedioso, repetitivo y no-sostenible.
