# Phase 0: Outline & Research - Mejoras en Tabla de Liquidaciones

## Decisiones Técnicas y de UI

Dado que la especificación y los requerimientos están alineados con la arquitectura ya establecida, no se encontraron áreas marcadas como `NEEDS CLARIFICATION`. Se documentan las decisiones arquitectónicas para la implementación.

### 1. Manejo del Ordenamiento en Reflex
- **Decision**: Mantener el estado del ordenamiento (`sort_column` y `sort_order`) en la clase de estado principal de Liquidaciones (ej. `EstadoLiquidacion` o similar).
- **Rationale**: Reflex exige que la reactividad se maneje a través de `rx.State`. Almacenar qué columna está ordenándose y si es ascendente o descendente (`ASC` o `DESC`) en el estado permite redibujar la tabla con íconos de flechas en el header y disparar el re-fetching o re-ordenamiento.
- **Alternatives considered**: Ordenamiento puramente en cliente vía Javascript. Rechazado debido a que la paginación suele estar acoplada a la DB, por lo que el ordenamiento de toda la colección debe ejecutarse a nivel de base de datos o lógica de backend y no solo en la página actual.

### 2. Implementación de Filtro por Ciclo Operativo
- **Decision**: Añadir una variable reactiva `filtro_ciclo_operativo: str` en el Estado y mapearla a un componente select/dropdown.
- **Rationale**: El filtrado avanzado ya usa este patrón. Al unificar los filtros bajo un método `aplicar_filtros()` que envíe estos valores a la capa de Aplicación/Infraestructura, se asegura el requisito de que "Ciclo Operativo" funcione como un AND lógico con el resto de filtros.

### 3. Ajuste de UI / Componentes
- **Decision**: Refactorizar la disposición de `rx.hstack`, `rx.vstack` y márgenes en el componente de "Filtros Avanzados" usando Flexbox de Reflex (`wrap="wrap"`, `spacing`) y referenciando las variables del `BASE_STYLE` de la aplicación en lugar de valores duros (magic numbers).
- **Rationale**: El *Claude Design System* exige evitar problemas de superposición y usar *depth* apropiado, por lo que un layout flexible soluciona la superposición de botones al redimensionar.

### 4. Actualización de Repositorios
- **Decision**: Modificar las firmas de los métodos de búsqueda en `repositorio_liquidacion.py` (y sus correspondientes interfaces y servicios) para aceptar parámetros opcionales `order_by: str` y `order_desc: bool`.
- **Rationale**: Para lograr un ordenamiento real, debe ejecutarse en el `ORDER BY` de la consulta de PostgreSQL utilizando inyección segura (nunca strings interpolados inseguros para nombre de columnas).
