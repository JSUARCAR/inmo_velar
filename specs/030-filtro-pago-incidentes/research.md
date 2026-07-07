# Research: Filtro de Pago en Incidentes

## Origen Dinámico de los Estados de Pago
**Problema**: El ComboBox debe poblarse con los estados de pago reales deducidos de las liquidaciones asociadas a los incidentes, en lugar de utilizar estados predefinidos o estáticos.
- **Decision**: Se implementará un método en `repositorio_incidentes.py` (`obtener_estados_pago_disponibles()`) que ejecute una consulta `SELECT DISTINCT` sobre el estado de pago calculado de las liquidaciones asociadas a los incidentes activos. 
- **Rationale**: Garantiza que los filtros mostrados en la UI siempre reflejen datos reales y existentes en la base de datos (PostgreSQL), evitando mostrar opciones "vacías" o huérfanas. Cumple con la especificación `FR-002`.
- **Alternatives considered**: Extraer todos los incidentes a la capa de Aplicación y deducir los estados en memoria con Python (rechazado por violar los objetivos de rendimiento y las políticas de la constitución de aprovechar PostgreSQL nativo).

## Filtrado de Incidentes por Estado de Pago
**Problema**: ¿Cómo aplicar el filtro de estado de pago en la consulta principal de incidentes?
- **Decision**: Se modificará el método `obtener_incidentes` (o su equivalente) en `repositorio_incidentes.py` para aceptar un parámetro `estado_pago`. La cláusula `WHERE` incorporará una subconsulta o un `JOIN` hacia la tabla `liquidaciones` para verificar el estado consolidado de los pagos asociados a cada incidente (utilizando `%s` para la interpolación segura).
- **Rationale**: Realizar el filtrado directamente en PostgreSQL (Infraestructura) es obligatorio según el mandato de "Filtrado Nativamente en BD", garantizando tiempos de respuesta < 1s (Cumple `SC-001` y `FR-003`).
- **Alternatives considered**: Filtrar los resultados en el State Management de Reflex en el Frontend. Totalmente inaceptable bajo estándares élite ya que no escala con bases de datos grandes.
