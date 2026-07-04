# Data Model & State Changes: fix-prod-diag-bugs

## 1. Cambios en Entidades DTO (Pydantic)

Dado que se ha identificado un fallo por valores nulos, revisaremos las entidades asociadas a las Liquidaciones.

**`src/aplicacion/dtos/liquidacion_dto.py`**
- Asegurar uso estricto de `Optional[T]` con `default=None` o `default=""` para campos conflictivos que puedan estar vacíos en producción (ej. `observaciones`, `incidentes_ids`).

## 2. Modificaciones al Estado Reflex (State)

**`src/presentacion_reflex/estados/estado_incidentes.py`**
Nuevas variables de estado para la Paginación:
- `pagina_actual: int = 1`
- `elementos_por_pagina: int = 20`
- `total_paginas: int = 1`
- `total_registros: int = 0`

Métodos de transición:
- `cargar_pagina(self, numero_pagina: int)`
- `pagina_siguiente(self)`
- `pagina_anterior(self)`
- `actualizar_totales(self)`

## 3. Repositorios de PostgreSQL (Infraestructura)

**`src/infraestructura/repositorios/repositorio_incidentes.py`**
Métodos nuevos o modificados:
- Modificar el método de listado para recibir `limit` y `offset`.
  ```python
  def listar_incidentes_paginados(self, limit: int, offset: int) -> list[Incidente]:
      # Implementación con %s para placeholders de PostgreSQL
  ```
- Método auxiliar: `contar_total_incidentes(self) -> int` para calcular la paginación de UI.

## 4. Script de Backfill

**`scripts/diagnostico/backfill_liquidaciones_nulas.py`**
- Tarea manual de 1-ejecución que iterará sobre las liquidaciones de PostgreSQL, buscará campos `observaciones` IS NULL (u otros detectados) y les hará un UPDATE a un string vacío `''` o `[]` (JSON).
