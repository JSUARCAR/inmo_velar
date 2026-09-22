# Data Model: Elegibilidad conjunta Mandato Activo + Arrendamiento Activo

**Date**: 2026-09-22
**Feature**: 076-liquidacion-requiere-arrendamiento

## Sin cambios de esquema

Esta feature **no introduce migraciones de esquema**. La verificación conjunta opera sobre columnas y relaciones ya existentes. A continuación el modelo relevante que **se lee** (y ocasionalmente se inserta) durante la validación.

## Entidades relevantes existentes

### Propiedad (punto de unión)

| Campo | Tipo | Propósito en esta feature |
|-------|------|---------------------------|
| ID_PROPIEDAD | INT (PK) | Identificador único del inmueble; es la clave de unión de mandato y arrendamiento |
| DIRECCION_PROPIEDAD | VARCHAR | Solo referencia visual; NO se usa para coincidencia (Q5) |
| MATRICULA_INMOBILIARIA | VARCHAR | Referencia; ID es la autoridad |
| VALOR_ADMINISTRACION | NUMERIC | Gastos de administración de la liquidación |

### ContratoMandato (`CONTRATOS_MANDATOS`)

| Campo | Tipo | Propósito |
|-------|------|-----------|
| ID_CONTRATO_M | INT (PK) | Identificador del mandato |
| ID_PROPIEDAD | INT (FK → PROPIEDADES) | Propiedad administrada; usado para unir con arrendamiento |
| ID_PROPIETARIO | INT (FK) | Propietario beneficiario de la liquidación |
| ID_ASESOR | INT (FK) | Asesor de gestión |
| CANON_MANDATO | NUMERIC | Canon de la liquidación |
| COMISION_PORCENTAJE_CONTRATO_M | NUMERIC | Porcentaje de comisión (base 10000) |
| IVA_CONTRATO_M | NUMERIC | IVA de referencia |
| ESTADO_CONTRATO_M | VARCHAR/ENUM | DEBE ser `ACTIVO` para la combinación 1 |
| FECHA_INICIO_CONTRATO_M / FECHA_FIN_CONTRATO_M | DATE | Rango temporal para la reconstrucción histórica de la auditoría |

### ContratoArrendamiento (`CONTRATOS_ARRENDAMIENTOS`)

| Campo | Tipo | Propósito |
|-------|------|-----------|
| ID_CONTRATO_A | INT (PK) | Identificador del arrendamiento |
| ID_PROPIEDAD | INT (FK → PROPIEDADES) | DEBE coincidir exactamente con `cm.ID_PROPIEDAD` (Q5) |
| ID_ARRENDATARIO | INT (FK) | Inquilino (afectado por limpieza TEST) |
| CANON_ARRENDAMIENTO | NUMERIC | Canon del arrendamiento |
| ESTADO_CONTRATO_A | VARCHAR/ENUM | DEBE ser `ACTIVO` para la combinación 1 |
| FECHA_INICIO_CONTRATO_A / FECHA_FIN_CONTRATO_A | DATE | Rango temporal para reconstrucción histórica |

### Liquidacion (`LIQUIDACIONES`)

| Campo | Tipo | Propósito |
|-------|------|-----------|
| ID_LIQUIDACION | INT (PK) | Identificador |
| ID_CONTRATO_M | INT (FK → CONTRATOS_MANDATOS) | Vínculo a mandato; único contrato por período |
| PERIODO | VARCHAR(7) | Período `YYYY-MM` |
| FECHA_GENERACION | DATE/ISO | Base temporal de la auditoría histórica (Q2) |
| ESTADO_LIQUIDACION | VARCHAR(20) | `En Proceso/Aprobada/Pagada/Cancelada`; la auditoría es solo lectura |

### Recaudo / Cuota de incidente (afectados por la limpieza TEST)

- `RECAUDOS` y `RECAUDO_CONCEPTOS`: movimientos del arrendamiento asociado a la liquidación.
- `CUOTA_INCIDENTE` → `INCIDENTE_LIQUIDACION` → `INCIDENTES`: relaciones derivadas asociadas a la liquidación/propiedad; sujetas a limpieza si apuntan exclusivamente a entidades de la bitácora (Q3).

## Elegibilidad conjunta (regla de datos)

```
elegible(contrato_m) :=
    contrato_m.estado_contrato_m == 'ACTIVO'
    AND existe ca IN CONTRATOS_ARRENDAMIENTOS
        WHERE ca.id_propiedad == contrato_m.id_propiedad
          AND ca.estado_contrato_a == 'ACTIVO'
```

Equivalente SQL para candidatos:

```sql
SELECT DISTINCT cm.ID_CONTRATO_M
FROM CONTRATOS_MANDATOS cm
WHERE cm.ESTADO_CONTRATO_M = %s
  AND EXISTS (
      SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca
      WHERE ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
        AND ca.ESTADO_CONTRATO_A = %s
  )
```

Los mismos puntos se reutilizan en la UI (formulario y masiva) para excluir candidatos de antemano (FR-005).

## Matriz de estados (referencia de datos)

| # | ESTADO_CONTRATO_M | Arrendamiento ACTIVO (misma ID) | Resultado |
|---|-------------------|----------------------------------|-----------|
| 1 | ACTIVO | Sí | ELEGIBLE → genera liquidación |
| 2 | ACTIVO | No existe | No elegible (motivo: sin arrendamiento activo) |
| 3 | ACTIVO | Inactivo/Finalizado | No elegible (motivo: sin arrendamiento activo) |
| 4 | No activo | ACTIVO | No elegible (motivo: sin mandato activo) |
| 5 | No activo | No/inactivo | No elegible (motivo: sin mandato activo y sin arrendamiento activo) |

Nota: la combinación 4 no será alcanzable por las consultas de candidatos (solo se parten de mandatos ACTIVO), pero se protege en `generar_liquidacion_mensual` por si una llamada directa entrega un mandato no activo.

## Bitácora de creación TEST (dato para la limpieza)

Documento operativo `bitacora_test.json` en `specs/076-liquidacion-requiere-arrendamiento/` (no es dato de la app):

```json
{
  "contratos_mandatos": [101, 102],
  "contratos_arrendamientos": [201],
  "propiedades": [301],
  "propietarios": [401],
  "arrendatarios": [501],
  "personas": [601],
  "liquidaciones": [701],
  "recaudos": [801]
}
```

- La limpieza recorre el orden FK: recaudos → liquidaciones / incidentes derivados → contratos → propiedades → arrendatarios/propietarios → personas.
- Idempotencia: `DELETE ... WHERE id IN (...)` ignora IDs inexistentes; no se borra nada fuera de la bitácora.
- Integridad: transacción única con `ROLLBACK` total ante cualquier error (igual patrón que `limpiar_datos_prueba_pg.py`); condición de `--dry-run` por defecto.

## Integridad de datos

- La restricción existente `UNIQUE(ID_CONTRATO_M, PERIODO)` se mantiene (no duplicados por contrato/período).
- La auditoría NO modifica ni elimina ninguna fila (solo `SELECT`).
- La limpieza solo toca IDs listados en la bitácora; los datos reales quedan intactos y verificables (SC-005).