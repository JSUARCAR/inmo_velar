# Análisis de Ingeniería Inversa: Módulo de Reportes (Liquidaciones)

Este documento contiene el análisis técnico y la estrategia de inyección requerida para integrar tres nuevas columnas ("Dirección del predio", "Nombre del propietario", "Nombre del asesor") inmediatamente después de `ID_CONTRATO_M` en el reporte de Liquidaciones, sin alterar la arquitectura base.

---

## 1. Identificación del Componente Central (Arquitectura UI y Estado)

El módulo de reportes está gestionado centralmente en la capa de presentación de Reflex por el estado:
**Archivo Objetivo:** `src/presentacion_reflex/state/reportes_state.py`

### Mecanismo de Renderizado Actual
En este archivo, la lógica de extracción de datos recae sobre la función asíncrona `_fetch_data`. Para la gran mayoría de los submódulos, incluyendo `"liquidaciones"`, el sistema emplea un mapeo estático (`table_map`) que asocia el ID del reporte con el nombre de la tabla en la base de datos (aprox. línea 450).

```python
        table_map = {
            # ... otros módulos
            "liquidaciones": "liquidaciones",
            # ...
        }
```

Al hacer "match", el sistema ejecuta una instrucción de consulta genérica (`SELECT * FROM {table_name}`). Las cabeceras del datatable UI (`preview_headers`) y el listado de datos (`preview_data`) se obtienen de forma dinámica basándose estrictamente en el orden de las claves del diccionario retornado por `cursor.fetchall()`.

---

## 2. Ingeniería Inversa del Modelo de Datos Relacional (PostgreSQL)

Para poder extraer las 3 columnas solicitadas y posicionarlas tras el `ID_CONTRATO_M`, es necesario trazar la ruta de relaciones foráneas desde la tabla `LIQUIDACIONES` hacia las tablas maestras (`PROPIEDADES`, `PROPIETARIOS`, `ASESORES` y `PERSONAS`):

- **Origen:** **`LIQUIDACIONES` (`l`)**
  Es la tabla pivot. Contiene el campo fundamental `ID_CONTRATO_M`.
- **Eje de Relación:** **`CONTRATOS_MANDATOS` (`cm`)**
  Relación principal: `l.ID_CONTRATO_M = cm.ID_CONTRATO_M`. Contiene las llaves foráneas necesarias: `ID_PROPIEDAD`, `ID_PROPIETARIO` e `ID_ASESOR`.
- **Columna 1 (Dirección):** **`PROPIEDADES` (`p`)**
  Relación: `cm.ID_PROPIEDAD = p.ID_PROPIEDAD`. De aquí extraemos `DIRECCION_PROPIEDAD`.
- **Columna 2 (Propietario):** **`PROPIETARIOS` (`prop`)** -> **`PERSONAS` (`per_prop`)**
  Relación 1: `cm.ID_PROPIETARIO = prop.ID_PROPIETARIO`. 
  Relación 2: `prop.ID_PERSONA = per_prop.ID_PERSONA`. De aquí obtenemos `NOMBRE_COMPLETO`.
- **Columna 3 (Asesor):** **`ASESORES` (`a`)** -> **`PERSONAS` (`per_ase`)**
  Relación 1: `cm.ID_ASESOR = a.ID_ASESOR`.
  Relación 2: `a.ID_PERSONA = per_ase.ID_PERSONA`. De aquí obtenemos `NOMBRE_COMPLETO`.

---

## 3. Plan de Integración Técnica de Élite (Ajuste No Invasivo)

Para cumplir con el requerimiento de negocio de ubicar las columnas *exactamente después* de `ID_CONTRATO_M`, se debe realizar una "intercepción" en la función `_fetch_data` para el identificador `"liquidaciones"`, justo antes de que sea procesado por la lógica genérica del `table_map`.

Al ejecutar un bloque SQL con un orden específico de declaración en el `SELECT`, el framework dinámico del cliente Reflex heredará ese mismo orden automáticamente, inyectando las columnas en la posición exacta.

### Consulta SQL a Inyectar:
```sql
SELECT 
    l.ID_LIQUIDACION,
    l.ID_CONTRATO_M,
    p.DIRECCION_PROPIEDAD AS "Direccion_Predio",
    per_prop.NOMBRE_COMPLETO AS "Nombre_Propietario",
    per_ase.NOMBRE_COMPLETO AS "Nombre_Asesor",
    l.PERIODO,
    l.FECHA_GENERACION,
    l.CANON_BRUTO,
    l.OTROS_INGRESOS,
    l.TOTAL_INGRESOS,
    l.COMISION_PORCENTAJE,
    l.COMISION_MONTO,
    l.IVA_COMISION,
    l.IMPUESTO_4X1000,
    l.GASTOS_ADMINISTRACION,
    l.GASTOS_SERVICIOS,
    l.GASTOS_REPARACIONES,
    l.OTROS_EGRESOS,
    l.TOTAL_EGRESOS,
    l.NETO_A_PAGAR,
    l.ESTADO_LIQUIDACION,
    l.FECHA_PAGO,
    l.METODO_PAGO,
    l.REFERENCIA_PAGO,
    l.OBSERVACIONES,
    l.MOTIVO_CANCELACION,
    l.APROBADA_POR,
    l.APROBADA_EN,
    l.PAGADA_POR,
    l.PAGADA_EN,
    l.CREATED_AT,
    l.CREATED_BY,
    l.UPDATED_AT,
    l.UPDATED_BY
FROM liquidaciones l
LEFT JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
LEFT JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
LEFT JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
LEFT JOIN PERSONAS per_prop ON prop.ID_PERSONA = per_prop.ID_PERSONA
LEFT JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
LEFT JOIN PERSONAS per_ase ON a.ID_PERSONA = per_ase.ID_PERSONA
```

### Pasos Prácticos de Implementación Futura:
1. En el archivo `src/presentacion_reflex/state/reportes_state.py`, localizar la definición del diccionario `table_map` dentro del método `_fetch_data`.
2. Remover `"liquidaciones": "liquidaciones"` de las claves de dicho diccionario para evitar la auto-generación cruda.
3. Agregar un flujo condicional `elif report_id == "liquidaciones":` superior, ejecutar en este bloque la query SQL estructurada y retornar los resultados paginados (`paginated`).
4. Al devolver el diccionario resultante de `psycopg2` o `sqlite3` (`cursor.fetchall()`), las cabeceras UI y la exportación a CSV asimilarán los campos inyectados en la posición predefinida tras el `ID_CONTRATO_M`.