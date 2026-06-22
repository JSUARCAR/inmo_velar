# ADR 0010: Estandarización del Cálculo de Diferencia de Días en PostgreSQL

## Estado
Aceptado

## Fecha
2026-06-22

## Contexto
El módulo Dashboard utilizaba `EXTRACT(DAY FROM AGE(fecha1, fecha2))` para calcular
los días restantes hasta el vencimiento de contratos. La función `AGE()` de PostgreSQL
retorna un intervalo estructurado (ej: "7 months 1 day"). Al aplicar `EXTRACT(DAY ...)`,
se extraía únicamente la porción de días del intervalo (1), ignorando los meses (7),
lo que provocaba que contratos a 215 días de su vencimiento aparecieran como "1 día
restante" en la tabla de Vencimientos Próximos (90 Días).

## Decisión
- **Días absolutos entre dos fechas:** Usar resta directa con casteo:
  `(fecha_fin::DATE - CURRENT_DATE)::INTEGER`
- **Años completos transcurridos:** `EXTRACT(YEAR FROM AGE(...))` es válido
  exclusivamente para obtener períodos completados (ej: años de contrato para IPC).
- **Prohibido:** `EXTRACT(DAY FROM AGE(...))` para obtener diferencia total en días.

## Alternativas Descartadas
- `DATE_PART('epoch', AGE(...)) / 86400`: Funciona pero es menos legible y propenso
  a errores de redondeo por fracciones de segundo.

## Consecuencias
- Mayor precisión matemática y alineamiento con la lógica de SQLite (`julianday`).
- Eliminación de falsos positivos en filtros de rangos de días.
- Requiere auditoría de cualquier uso futuro de `AGE()` en consultas de días.
