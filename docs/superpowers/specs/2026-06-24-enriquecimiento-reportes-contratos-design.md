# Diseño Técnico: Enriquecimiento de Reportes de Contratos

## 1. Contexto y Objetivo
Actualmente, los reportes de "Contratos de Mandato" y "Contratos de Arrendamiento" devuelven identificadores brutos de entidades relacionadas (ID_PROPIEDAD, ID_PROPIETARIO, etc.) mediante una consulta de base genérica. El objetivo de este diseño es enriquecer estos reportes directamente desde la base de datos (PostgreSQL), incluyendo los nombres completos y descripciones, y reemplazando las consultas genéricas por consultas especializadas y optimizadas, sin romper la paginación ni la búsqueda y conservando la integridad de la arquitectura limpia actual.

## 2. Arquitectura de Datos (Nuevas Columnas)

### Reporte de Contratos de Mandato
La respuesta constará de las siguientes columnas ordenadas:
- `ID_CONTRATO_M`: Identificador del contrato.
- `ESTADO_CONTRATO_M`: Estado actual.
- `DIRECCION_PROPIEDAD`: Dirección del inmueble (extraída de la tabla `PROPIEDADES`).
- `NOMBRE_PROPIETARIO`: Nombre del propietario (extraída de `PROPIETARIOS` -> `PERSONAS`).
- `NOMBRE_ASESOR`: Nombre del asesor asignado (extraída de `ASESORES` -> `PERSONAS`).
- `FECHA_INICIO_CONTRATO_M`: Fecha de inicio.
- `FECHA_FIN_CONTRATO_M`: Fecha de fin.
- `DURACION_CONTRATO_M`: Duración del contrato.
- `CANON_MANDATO`: Monto del canon.
- `COMISION_PORCENTAJE_CONTRATO_M`: Porcentaje de comisión.
- Metadatos de Trazabilidad: `ID_PROPIEDAD`, `ID_PROPIETARIO`, `ID_ASESOR`.

### Reporte de Contratos de Arrendamiento
La respuesta constará de las siguientes columnas ordenadas:
- `ID_CONTRATO_A`: Identificador del contrato.
- `ESTADO_CONTRATO_A`: Estado actual.
- `DIRECCION_PROPIEDAD`: Dirección del inmueble (extraída de la tabla `PROPIEDADES`).
- `NOMBRE_ARRENDATARIO`: Nombre del arrendatario principal (extraída de `ARRENDATARIOS` -> `PERSONAS`).
- `NOMBRE_HABITANTE`: Nombre del habitante residente (extraída nativamente de `ARRENDATARIOS`).
- `NOMBRE_CODEUDOR`: Nombre del codeudor o fiador, "N/A" si no existe (extraída de `CODEUDORES` -> `PERSONAS`).
- `FECHA_INICIO_CONTRATO_A`: Fecha de inicio.
- `FECHA_FIN_CONTRATO_A`: Fecha de finalización.
- `DURACION_CONTRATO_A`: Duración en meses.
- `CANON_ARRENDAMIENTO`: Valor del canon.
- `DEPOSITO`: Monto del depósito.
- Metadatos de Trazabilidad: `ID_PROPIEDAD`, `ID_ARRENDATARIO`, `ID_CODEUDOR`.

## 3. Integración en Componentes Backend

### 3.1. Capa de Infraestructura (`repositorio_reportes.py`)
Se crearán dos métodos nuevos:
- `obtener_reporte_contratos_mandato(busqueda, page, limit)`: Implementa `INNER JOIN` con propiedades, propietarios, asesores y personas. 
- `obtener_reporte_contratos_arrendamiento(busqueda, page, limit)`: Implementa `INNER JOIN` con propiedades, arrendatarios, y un `LEFT JOIN` con codeudores. Utiliza `COALESCE` para lidiar con la opcionalidad del codeudor y garantizar consistencia en la respuesta para el front-end y exportación en CSV/Excel.

En ambos, el parámetro `busqueda` inyectará una cláusula `WHERE (...)` que ejecutará consultas con `ILIKE` sobre todos los campos de texto enriquecidos (direcciones, nombres de personas e identificadores).

### 3.2. Capa de Aplicación (`servicio_reportes.py`)
1. **Desacople Genérico:** Retirar `"contratos_mandato"` y `"contratos_arrendamiento"` del diccionario `table_map` del método genérico de reportes.
2. **Orquestación Explícita:** Insertar un nuevo bloque condicional dedicado a evaluar `report_id` para estos contratos específicos y rutar la ejecución hacia las nuevas funciones creadas en el repositorio.

## 4. Estándares y Validaciones
- **Seguridad / Cero Filtraciones**: Se respetarán las sentencias parametrizadas (`%s`) para evitar cualquier ataque de inyección SQL en los campos de búsqueda.
- **Eficiencia**: Las consultas mantienen el uso de window functions `COUNT(*) OVER()` para procesar datos y total de registros en una sola consulta.
- **Agnosticidad UI**: El diseño no requiere intervención en la capa `presentacion_reflex`, al extraer los *headers* de manera dinámica.
