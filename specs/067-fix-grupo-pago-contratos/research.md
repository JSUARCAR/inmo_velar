# Phase 0: Research & Technical Decisions

## 1. Patrón de Acceso a Datos (db_manager vs ORM/Repository)
*   **Decision**: Utilizar `db_manager` con ejecución directa de SQL parametrizado (`%s`) para el script de migración masiva.
*   **Rationale**:
    1.  Los scripts en el directorio `scripts/` (ej. `recalcular_contratos_elite.py`) de la arquitectura actual usan el enfoque directo de `db_manager` para realizar `SELECT` y `UPDATE` masivos.
    2.  Esto evita dependencias pesadas de la capa de aplicación dentro del script de migración CLI, reduciendo el riesgo de efectos secundarios (como envíos de notificaciones accidentales o side-effects del repositorio).
    3.  Permite un manejo transaccional explícito `with db_manager.transaccion() as conexion:`, que cumple con la regla de Atomicidad.
*   **Alternatives considered**: Instanciar e inyectar `RepositorioContratoMandatoPostgres`. Descartado porque la actualización masiva (`executemany`) a través de `db_manager` es más eficiente para migraciones de grado industrial y ya es el estándar usado en los otros scripts del proyecto (`migrar_ciclo_operativo_v3.py`, etc.).

## 2. Lógica de Recalibración
*   **Decision**: Reutilizar `CalculadoraContratos.calcular_ciclo_pago_mandato` importándola desde el script.
*   **Rationale**: Garantiza "Single Source of Truth". Si la regla vuelve a cambiar, la calculadora será actualizada y el script seguirá siendo válido (o podrá re-ejecutarse). No duplicar la lógica de rangos en el script.
*   **Alternatives considered**: Hardcodear las reglas V2 (28-7, etc) dentro del script SQL. Descartado porque SQL no debe contener lógica de negocio (anti-patrón).

## 3. Alcance Filtrado (Activos y Mandatos)
*   **Decision**: El query SQL base filtrará explícitamente `ESTADO_CONTRATO_M = 'Activo'` y se ejecutará exclusivamente sobre la tabla `CONTRATOS_MANDATOS`.
*   **Rationale**: Cumple exactamente con las aclaraciones (Clarifications) realizadas en la fase de especificación para evitar daños colaterales en históricos y arrendamientos.
