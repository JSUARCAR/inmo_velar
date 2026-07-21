# Data Model: Columnas Condicionales en Tabla de Contratos

**Date**: 2026-07-21

## Entidades Relevantes

### ContratoMandato (CONTRATOS_MANDATOS)

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| id_contrato_m | int | NO | PK |
| consignatario | str | SÍ | Nombre del consignatario |
| documento_consignatario | str | SÍ | Documento del consignatario |
| banco_propietario | str | SÍ | Banco para depósito |
| numero_cuenta_propietario | str | SÍ | Número de cuenta |
| tipo_cuenta | str | SÍ | Tipo de cuenta (Ahorro/Corriente) |

**Nota**: Estos campos ya existen en la tabla. No se requiere migración.

### ContratoArrendamiento (CONTRATOS_ARRENDAMIENTOS)

| Campo | Tipo | Nullable | FK | Descripción |
|-------|------|----------|-----|-------------|
| id_contrato_a | int | NO | - | PK |
| id_codeudor | int | SÍ | CODEUDORES | FK al codeudor |

### Codeudor (CODEUDORES)

| Campo | Tipo | Nullable | FK | Descripción |
|-------|------|----------|-----|-------------|
| id_codeudor | int | NO | - | PK |
| id_persona | int | NO | PERSONA | FK a datos personales |

### Persona (PERSONA)

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| id_persona | int | NO | PK |
| nombre | str | NO | Nombre completo |
| telefono | str | SÍ | Teléfono de contacto |

## Relaciones

```
CONTRATOS_MANDATOS (campos directos: consignatario, banco, cuenta)
         │
         │ 1:1 (misma fila)
         ▼
    [Datos de información adicional para Mandato]

CONTRATOS_ARRENDAMIENTOS
         │
         │ FK: id_codeudor (nullable)
         ▼
      CODEUDORES
         │
         │ FK: id_persona
         ▼
       PERSONA → nombre, telefono
```

## DTO Actualizado

### ContratoDict (para UI)

```python
from pydantic import BaseModel
from typing import Optional

class ContratoDict(BaseModel):
    """DTO para representar un contrato en la tabla unificada."""
    
    # Campos existentes (sin cambios)
    id_contrato: int
    tipo_contrato: str              # "Mandato" | "Arrendamiento"
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
    
    # NUEVO: Campo para información adicional condicional
    informacion_adicional: Optional[str] = None
    # Formato Mandato: "Consignatario | Banco | Cuenta"
    # Formato Arrendamiento: "Nombre Codeudor | Teléfono"
    # Sin datos: None o "No registrado"
```

## Reglas de Negocio

### Formato de Visualización

| Tipo Contrato | Campos | Formato Ejemplo |
|---------------|--------|-----------------|
| Mandato | consignatario, banco_propietario, numero_cuenta_propietario | `"Juan Pérez | Bancolombia | 1234567890"` |
| Arrendamiento | codeudor_nombre, codeudor_telefono | `"María García | 3101234567"` |
| Sin datos | - | `"No registrado"` |

### Lógica de Construcción

```python
def construir_informacion_adicional(contrato: dict) -> str | None:
    """Construye el campo informacion_adicional según tipo de contrato."""
    
    if contrato["tipo_contrato"] == "Mandato":
        consignatario = contrato.get("consignatario")
        banco = contrato.get("banco_propietario")
        cuenta = contrato.get("numero_cuenta_propietario")
        
        if consignatario or banco or cuenta:
            parts = [
                consignatario or "—",
                banco or "—",
                cuenta or "—"
            ]
            return " | ".join(parts)
        return "No registrado"
    
    elif contrato["tipo_contrato"] == "Arrendamiento":
        codeudor_nombre = contrato.get("codeudor_nombre")
        codeudor_telefono = contrato.get("codeudor_telefono")
        
        if codeudor_nombre:
            parts = [
                codeudor_nombre,
                codeudor_telefono or "—"
            ]
            return " | ".join(parts)
        return "No registrado"
    
    return None
```

## Migraciones

**No se requieren migraciones de BD.** Todos los campos necesarios ya existen:
- Mandato: campos directos en `CONTRATOS_MANDATOS`
- Arrendamiento: FK `id_codeudor` ya existe, solo se necesita el JOIN
