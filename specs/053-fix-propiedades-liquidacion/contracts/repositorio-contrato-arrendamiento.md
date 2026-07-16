# Contract: RepositorioContratoArrendamiento

**Date**: 2026-07-13

## Method: obtener_activos_por_asesor(id_asesor: int) → list[dict]

### Input
- `id_asesor`: ID del asesor inmobiliario

### Output
Lista de diccionarios con la siguiente estructura:
```python
{
    "id_contrato_a": int,          # ID del contrato de arrendamiento
    "id_propiedad": int,           # ID de la propiedad
    "canon_arrendamiento": int,    # Canon mensual
    "estado_contrato_a": str,      # Estado del contrato (debe ser "ACTIVO")
    "id_arrendatario": int | None, # ID del arrendatario
    "comision_porcentaje_contrato_m": int,  # % comisión (escala 0-10000)
    "id_contrato_m": int,          # ID del contrato mandato
    "direccion_propiedad": str,    # Dirección de la propiedad
    "id_seguro": int | None,       # ID del seguro
    "nombre_seguro": str | None,   # Nombre del seguro
    "porcentaje_seguro": int | None  # % seguro (escala 0-10000)
}
```

### Behavior
- Retorna SOLO propiedades que tengan:
  1. Un CONTRATO_ARRENDAMIENTO con `ESTADO_CONTRATO_A = 'ACTIVO'`
  2. Un CONTRATO_MANDATO con `ESTADO_CONTRATO_M = 'ACTIVO'` e `ID_ASESOR = id_asesor`
- No produce duplicados (DISTINCT ON o equivalent)
- Propiedades sin mandato activo NO se incluyen
- Propiedades con mandato activo pero de otro asesor NO se incluyen

### Validation Scenarios
1. Asesor con 46 propiedades activas → retorna 46 registros
2. Asesor con 1 propiedad activa → retorna 1 registro
3. Asesor con propiedades activas e inactivas → retorna solo activas
4. Propiedad con múltiples mandatos históricos → retorna solo el activo
5. Propiedad sin mandato → no se incluye en resultados
