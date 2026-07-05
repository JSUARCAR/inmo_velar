# Research: fix-filtro-ciclo-ui

## Context
El objetivo principal era resolver dos problemas relacionados con la sección de filtros en el módulo de liquidaciones:
1. Error SQL de base de datos debido a un alias inexistente en la tabla de propiedades (`prop.GRUPO_OPERATIVO`).
2. Superposición de controles en la UI bajo resoluciones estrechas.

## Findings & Decisions

### 1. Resolución de Alias en Base de Datos
- **Unknown/Issue**: La consulta de base de datos arroja "column prop.grupo_operativo does not exist".
- **Decision**: Sustituir la referencia al alias `prop` por `p`, que es el alias canónico para la tabla de propiedades en los JOINs de `repositorio_liquidacion_postgres.py`.
- **Rationale**: El alias `prop` fue utilizado por error. Reemplazarlo garantiza que la consulta se ejecute correctamente.
- **Alternatives considered**: Añadir un nuevo JOIN con alias `prop` (rechazado por causar duplicación y pérdida de rendimiento en la consulta).

### 2. Layout Responsivo de UI
- **Unknown/Issue**: Los componentes `neuro_select_root` y `neuro_button` se agolpan y superponen al cambiar la resolución.
- **Decision**: Ajustar los parámetros de ancho (width) de los contenedores Flex en `liquidaciones.py`. Cada componente de filtro debe tener `width=["100%", "100%", "auto o píxeles fijos"]` para forzar un componente por fila en móvil.
- **Rationale**: En móviles, disponer de un control por fila mejora drásticamente el espacio táctil y previene solapamientos visuales de la interfaz neumórfica.
- **Alternatives considered**: Mantener todos los filtros en una sola fila pero habilitar un overflow scroll horizontal (rechazado por empeorar la experiencia UX táctil y ocultar información crítica).
