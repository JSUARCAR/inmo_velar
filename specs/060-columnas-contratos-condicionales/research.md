# Research: Columnas Condicionales en Tabla de Contratos

**Date**: 2026-07-21

## Decision Log

### 1. Fuente de Datos para Mandato

**Decision**: Usar campos directos de `CONTRATOS_MANDATOS`

**Rationale**: Los campos `consignatario`, `banco_propietario` y `numero_cuenta_propietario` ya están almacenados directamente en la tabla de mandatos. No se requiere JOIN adicional.

**Alternatives Considered**:
- Crear entidad Consignatario separada: Rechazado por agregar complejidad innecesaria cuando los campos ya existen

**Evidence**:
```
Entidad ContratoMandato:
- consignatario: str
- banco_propietario: str
- numero_cuenta_propietario: str
```

### 2. Fuente de Datos para Arrendamiento

**Decision**: JOIN con tablas CODEUDORES y PERSONA

**Rationale**: El codeudor se almacena como FK `id_codeudor` en `CONTRATOS_ARRENDAMIENTOS`, pero nombre y teléfono están en la tabla PERSONA a través de CODEUDORES.id_persona.

**Alternatives Considered**:
- Almacenar datos directos en Arrendamiento: Rechazado por normalización existente

**Evidence**:
```
CONTRATOS_ARRENDAMIENTOS.id_codeudor → CODEUDORES.id_persona → PERSONA (nombre, telefono)
```

### 3. Patrón de UI para Columna Condicional

**Decision**: Agregar columna calculada en `ContratoDict` con formato concatenado

**Rationale**: El patrón existente usa `ContratoDict` como DTO para la UI. Agregar un campo `informacion_adicional` mantiene consistencia.

**Alternatives Considered**:
- Crear componente separado: Rechazado por simplicidad
- Lógica directa en template: Rechazado por Separation of Concerns

### 4. Query de Repositorio

**Decision**: Modificar query de Arrendamiento para incluir datos de Codeudor

**Rationale**: El repositorio actual no retorna datos de codeudor. Se necesita agregar LEFT JOIN.

**Evidence**:
```sql
-- Query actual (simplificado)
SELECT * FROM CONTRATOS_ARRENDAMIENTOS ca
JOIN PROPIEDADES p ON ca.id_propiedad = p.id_propiedad

-- Query necesario
SELECT ca.*, 
       cd.nombre as codeudor_nombre,
       pe.telefono as codeudor_telefono
FROM CONTRATOS_ARRENDAMIENTOS ca
LEFT JOIN CODEUDORES cd ON ca.id_codeudor = cd.id_codeudor
LEFT JOIN PERSONA pe ON cd.id_persona = pe.id_persona
```

### 5. Formato de Visualización

**Decision**: Formato pipe-separated: `"Campo1 | Campo2 | Campo3"`

**Rationale**: Consistente con la decisión del usuario en `/speckit-clarify`. Legible y estándar en tablas de administración.

**Alternatives Considered**:
- Formato con guiones: Menos legible
- Lista vertical: Ocupa demasiado espacio vertical

## Technical Findings

### Estructura Actual de la Tabla

La tabla renderiza en `render_table_view()` en `pages/contratos.py` con 9 columnas:
1. Propiedad
2. Tipo
3. Estado
4. Cumplimiento
5. Propietario/Arrendatario
6. Valor
7. Fecha Pago
8. Fechas
9. Acciones

### Flujo de Datos Actual

```
PostgreSQL → Repositorio (dicts planos) → Servicio → State (ContratoDict) → UI
```

**Nota**: Los datos NO pasan por entidades de dominio al cargar la lista. Se usan dicts directamente.

### Campos Disponibles en ContratoDict

```python
class ContratoDict(pydantic.BaseModel):
    id_contrato: int
    tipo_contrato: str              # "Mandato" o "Arrendamiento"
    estado_contrato: str
    propiedad_direccion: str
    propiedad_matricula: str
    propiedad_tipo: str
    propietario_nombre: str
    propietario_documento: str
    arrendatario_nombre: str
    arrendatario_documento: str
    habitante_nombre: str
    asesor_nombre: str
    fecha_inicio: str
    fecha_fin: str
    valor_canon: float
    valor_administracion: float
    fecha_pago: str
    grupo_operativo: int
    estado_cumplimiento: str
```

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Query más lento por JOINs | Bajo (pocos registros) | LEFT JOIN optimizado, índices existentes |
| Contratos sin codeudor | Medio | LEFT JOIN + validación NULL en UI |
| Múltiples consignatarios | Bajo | Filtrar por designado principal |

## Open Questions

- ¿Existe un campo `es_principal` o `designado` en la tabla de consignatarios? → Asumir que el consignatario del mandato es el principal por defecto.
