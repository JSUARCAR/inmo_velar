"""
PHASE 1: ROOT CAUSE INVESTIGATION - DIAGNOSIS
=============================================

## Problem Statement
User reports that when editing a mandate contract and entering a value in "Fecha de Pago", 
the value is NOT being saved to the PostgreSQL database on Railway.

## Data Flow Analysis
Following the data from UI → State → Service → Repository → Database:

### ✅ Layer 1: UI Component  
File: `contrato_mandato_form.py`
- Has input field for "Fecha de Pago" (type="date")
- Field name: "fecha_pago"

### ✅ Layer 2: State Management
File: `contratos_state.py` (line 885)
```python
datos_procesados = {
    ...
    "fecha_pago": form_data.get("fecha_pago"),
    ...
}
```
- Value IS extracted from form_data
- Value IS passed to servicio.actualizar_mandato()

### ❌ Layer 3: Service (APPLICATION) - **ROOT CAUSE IDENTIFIED**
File: `servicio_contratos.py` - method `actualizar_mandato` (lines 143-180)
```python
def actualizar_mandato(self, id_contrato: int, datos: Dict, usuario_sistema: str) -> None:
    mandato = self.repo_mandato.obtener_por_id(id_contrato)
    
    # Updates these fields:
    mandato.id_propiedad = datos.get("id_propiedad", mandato.id_propiedad)
    mandato.id_propietario = datos.get("id_propietario", mandato.id_propietario)
    mandato.id_asesor = datos.get("id_asesor", mandato.id_asesor)
    mandato.fecha_inicio_contrato_m = datos.get("fecha_inicio", mandato.fecha_inicio_contrato_m)
    mandato.fecha_fin_contrato_m = datos.get("fecha_fin", mandato.fecha_fin_contrato_m)
    mandato.duracion_contrato_m = datos.get("duracion_meses", mandato.duracion_contrato_m)
    mandato.canon_mandato = datos.get("canon", mandato.canon_mandato)
    mandato.comision_porcentaje_contrato_m = datos.get("comision_porcentaje", mandato.comision_porcentaje_contrato_m)
    
    # ❌ MISSING: mandato.fecha_pago = datos.get("fecha_pago", mandato.fecha_pago)
    
    self.repo_mandato.actualizar(mandato, usuario_sistema)
```

**DIAGNOSIS:**
The service layer receives `fecha_pago` in the `datos` dict but NEVER assigns it to `mandato.fecha_pago` 
before calling `repo_mandato.actualizar()`. This means the entity passed to the repository still has 
the OLD value (or None), regardless of what the user entered.

### ✅ Layer 4: Repository
File: `repositorio_contrato_mandato_sqlite.py`
- Repository DOES include `FECHA_PAGO` in UPDATE statement (verified, we just fixed duplicate column issue)
- Repository correctly uses `contrato.fecha_pago` in the VALUES tuple

## Verification Evidence
1. ✅ UI field exists and captures input
2. ✅ State extracts and passes value to service
3. ❌ Service does NOT assign the value to the entity
4. ✅ Repository would save it IF the entity had the correct value

## Root Cause Conclusion
**The bug is in `servicio_contratos.py`, method `actualizar_mandato`, lines 143-180.**

The method is missing this line:
```python
mandato.fecha_pago = datos.get("fecha_pago", mandato.fecha_pago)
```

This is a classic example of:
- ✅ Database schema updated
- ✅ Repository updated
- ✅ UI updated
- ✅ State updated
- ❌ Service layer NOT updated (field assignment missing)

## Next Steps
PHASE 2: Fix Implementation
- Add the missing line to `actualizar_mandato`
- Check `crear_mandato` for the same issue
- Verify fix works locally
- Deploy to Railway
"""
