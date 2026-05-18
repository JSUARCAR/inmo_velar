# ADR-001: Migración de Comisión de Asesor a ContratoMandato

## Contexto
El porcentaje de comisión para liquidación de asesores se obtenía del rol Asesor (perfil global), pero la regla de negocio requiere que provenga del Contrato de Mandato (negociación individual con cada propietario).

## Decisión
Migrar la fuente de verdad de la comisión de `ASESORES.COMISION_PORCENTAJE_ARRIENDO` a `CONTRATOS_MANDATOS.COMISION_PORCENTAJE_CONTRATO_M`.

Se implementó un desglose individual por contrato en la tabla `LIQUIDACIONES_CONTRATOS`, almacenando tanto el porcentaje como el monto calculado en el momento de la liquidación.

Se añadió el metadato `MODO_COMISION` en `LIQUIDACIONES_ASESORES` para diferenciar liquidaciones generadas bajo la regla antigua ('ASESOR') de las nuevas ('CONTRATO_MANDATO').

## Consecuencias
- **Positivas:** 
    - Alineación 100% con la regla de negocio real.
    - Trazabilidad total de cómo se calculó cada peso de la comisión.
    - Posibilidad de tener diferentes porcentajes de comisión para un mismo asesor en un mismo periodo.
- **Negativas:** 
    - Ligero incremento en la complejidad del JOIN en el repositorio.
- **Neutrales:** 
    - Liquidaciones históricas preservadas sin cambios (retrocompatibilidad asegurada).

## Alternativas Descartadas
- **Promedio ponderado simple:** Se descartó porque se pierde la trazabilidad de qué contrato aportó cuánto.
- **Liquidaciones separadas por contrato:** Se descartó porque complicaría la gestión de pagos y bonificaciones globales del asesor.

## Estado
Aceptado
