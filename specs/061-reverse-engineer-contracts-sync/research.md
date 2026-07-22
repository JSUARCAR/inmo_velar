# Research: Ingeniería Inversa - Sincronización Contratos, Liquidaciones y Recaudos

**Date**: 2026-07-22
**Feature**: 061-reverse-engineer-contracts-sync

## Summary

Investigación completada para validar la sincronización entre módulos de Contratos, Liquidaciones de Propietarios y Recaudos. No se identificaron unknowns en el Technical Context.

## Decisions

### D1: Framework de Testing
**Decision**: pytest con pytest-cov
**Rationale**: Es el framework estándar del proyecto (requerido en requirements.txt). Soporta fixtures, parametrización y cobertura de código.
**Alternatives**: unittest (descartado por ser más verboso), nose2 (no está en dependencias)

### D2: Estrategia de Validación
**Decision**: Script repeatable que genera informe de texto estructurado
**Rationale**: Permite ejecución periódica post-cambio de código y diagnóstico rápido de inconsistencias.
**Alternatives**: Tests unitarios solamente (no capturan flujos end-to-end), auditoría manual (no es repeatable)

### D3: Fuente de Datos para Validación
**Decision**: Datos de prueba controlados en entorno de staging
**Rationale**: Permite controlar escenarios exactos y reproducir resultados. Datos de producción son impredecibles.
**Alternatives**: Datos de producción (riesgo de falsos positivos/negativos)

### D4: Definición de "Retroactivo"
**Decision**: Cualquier modificación de un registro después de su creación inicial
**Rationale**: Definición más restrictiva y segura para protección de datos financieros históricos.
**Alternatives**: Solo modificaciones que alteren valores financieros (menos seguro), solo registros en estado "Pagado" (incompleto)

### D5: Ubicación del Script de Auditoría
**Decision**: `tests/verification/audit_sincronizacion.py`
**Rationale**: Separado de tests unitarios/integración porque es una herramienta de auditoría, no un test automatizado.
**Alternatives**: `scripts/` (mezcla con scripts de producción), `tests/` (confunde con tests)

## Integration Patterns Identified

### P1: Cascada de Renovación
**Flow**: ContratoArrendamiento.renovar() → ContratoMandato.canon_mandato → Propiedad.canon_arrendamiento_estimado
**Key Files**:
- `src/aplicacion/servicios/servicio_contrato_arrendamiento.py:394` (_ejecutar_renovacion_arrendamiento)
- `src/aplicacion/servicios/servicio_contrato_mandato.py` (renovar_mandato)
- `src/dominio/entidades/renovacion_contrato.py` (canon_anterior, canon_nuevo)

### P2: Generación de Liquidaciones
**Flow**: servicio_financiero.generar_liquidacion_mensual() → usa contrato.canon_mandato
**Key Files**:
- `src/aplicacion/servicios/servicio_financiero.py` (generar_liquidacion_mensual)
- `src/infraestructura/repositorios/repositorio_liquidacion_postgres.py`

### P3: Generación de Recaudos
**Flow**: servicio_recaudo.generar_recaudos_mes_actual() → usa CONTRATOS_ARRENDAMIENTOS.CANON_ARRENDAMIENTO
**Key Files**:
- `src/aplicacion/servicios/servicio_recaudo.py` (generar_recaudos_mes_actual)
- `src/infraestructura/repositorios/repositorio_recaudo.py`

## Validation Scripts Analysis

### Existing Scripts
1. `scripts/recalcular_contratos_elite.py`: Solo recalcula duración/pago/grupo en contratos activos. NO toca liquidaciones/recaudos.
2. `scripts/recalculate_totals.py`: Solo recalcula LIQUIDACIONES_ASESORES (liquidaciones de asesores), NO liquidaciones de propietarios.

### Gap Identified
No existe script que valide la sincronización entre contratos → liquidaciones → recaudos después de una renovación.

## Recommendations

1. **Crear script de auditoría** que valide:
   - Cascada de renovación (canon → mandato → propiedad)
   - Preservación de registros históricos
   - Generación con canon actualizado
   - Consistencia entre módulos
   - Ausencia de actualizaciones retroactivas
   - Respeto de fecha de vigencia

2. **Crear tests de integración** que prueben:
   - Flujo completo de renovación → generación de liquidación → generación de recaudo
   - Aislamiento de datos históricos

3. **Integrar en CI/CD** para ejecución post-cada cambio de código
