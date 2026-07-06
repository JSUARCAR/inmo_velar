# Data Model: campos-extra-contratos

## Hallazgo Clave: Tabla Única

> **IMPORTANTE**: El sistema usa una SOLA tabla `contratos` para ambos tipos (mandato y arrendamiento), diferenciados por el campo `tipo_contrato`. No existen tablas separadas `contratos_mandato` / `contratos_arrendamiento`.

## Entidades Afectadas

### 1. Contrato (tabla `contratos`)
- **Campos Agregados**:
  - `enlace_video` (VARCHAR(512), Opcional): URL del video de recibo del inmueble. Aplica a ambos tipos de contrato.
  - `responsable_deposito_id` (INTEGER, Opcional, Foreign Key → `asesores(id)`): Referencia al asesor responsable del depósito. Solo aplica cuando `tipo_contrato = 'mandato'`.
- **Validaciones DTO**:
  - `enlace_video`: URL bien formada (http/https), opcional, max 512 caracteres.
  - `responsable_deposito_id`: ID numérico válido referenciando un asesor existente, opcional (puede ser None).

### 2. Asesor (tabla `asesores`)
- **Modelo Existente**: No se modifica.
- **Servicio Existente**: `obtener_asesores_activos()` ya disponible en `asesor_service.py` y `repositorio_asesor.py`.

## Cambios Estructurales en Base de Datos (SQL DDL)

```sql
-- Agregar columnas a la tabla única 'contratos'
ALTER TABLE contratos ADD COLUMN enlace_video VARCHAR(512);
ALTER TABLE contratos ADD COLUMN responsable_deposito_id INTEGER REFERENCES asesores(id);
```

## Archivos Afectados

| Capa | Archivo | Cambio |
|------|---------|--------|
| Dominio | `src/dominio/contrato.py` | Agregar atributos `enlace_video`, `responsable_deposito_id` |
| Aplicación | `src/aplicacion/contrato_service.py` | Pasar nuevos campos en crear/actualizar |
| Infraestructura | `src/infraestructura/repositorio_contrato.py` | Actualizar INSERT/UPDATE/SELECT SQL |
| Presentación | `src/presentacion_reflex/contratos.py` | Agregar campos al State, modales y funciones guardar/editar |
