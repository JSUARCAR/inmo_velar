# 🔌 Guía de Integración con Base de Datos Real

## 📋 Resumen

El sistema PDF Élite actualmente usa `MockPDFRepository` con datos de prueba. Esta guía te muestra cómo conectar a tu base de datos PostgreSQL real.

---

## 🎯 Paso 1: Entender la Arquitectura Actual

### Flujo de Datos
```
UI (Reflex) 
  → PDFState (event handlers)
    → MockPDFRepository (DATOS MOCK)
      → ServicioPDFFacade
        → Templates Elite
          → PDF Generado
```

### Archivos Clave
- **`pdf_state.py`** - Event handlers de Reflex
- **`mock_data_repository.py`** - Datos de prueba (REEMPLAZAR)
- **`servicio_pdf_facade.py`** - Lógica de negocio PDF

---

## 🔧 Paso 2: Conectar a PostgreSQL

Ya tienes `database.py` configurado. Solo necesitas crear el repository real.

### Crear `pdf_data_repository.py`

```python
# src/infraestructura/servicios/pdf_elite/utils/pdf_data_repository.py

from typing import Dict, Any, List, Optional
from src.infraestructura.persistencia.database import db_manager


class PDFDataRepository:
    """Repository real con queries a PostgreSQL"""
    
    @classmethod
    def get_contrato_data(cls, contrato_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene datos completos de un contrato desde PostgreSQL"""
        
        with db_manager.transaccion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            
            # Query principal del contrato
            cursor.execute("""
                SELECT 
                    c.id,
                    c.fecha_inicio,
                    c.duracion_meses,
                    c.canon,
                    c.deposito,
                    c.administracion,
                    c.dia_pago,
                    c.estado,
                    c.arrendador_id,
                    c.arrendatario_id,
                    c.inmueble_id
                FROM CONTRATOS c
                WHERE c.id = %s
            """, (contrato_id,))
            
            contrato = cursor.fetchone()
            if not contrato:
                return None
            
            # Obtener arrendador
            cursor.execute("""
                SELECT nombre, tipo_documento, documento, telefono, email, direccion
                FROM PERSONAS
                WHERE id = %s
            """, (contrato['ARRENDADOR_ID'],))
            arrendador = cursor.fetchone()
            
            # Obtener arrendatario
            cursor.execute("""
                SELECT nombre, tipo_documento, documento, telefono, email, direccion
                FROM PERSONAS
                WHERE id = %s
            """, (contrato['ARRENDATARIO_ID'],))
            arrendatario = cursor.fetchone()
            
            # Obtener inmueble
            cursor.execute("""
                SELECT direccion, tipo, area, habitaciones, banos, estrato
                FROM INMUEBLES
                WHERE id = %s
            """, (contrato['INMUEBLE_ID'],))
            inmueble = cursor.fetchone()
            
            # Construir diccionario resultado
            return {
                'contrato_id': contrato['ID'],
                'fecha': contrato['FECHA_INICIO'].strftime('%Y-%m-%d'),
                'estado': contrato['ESTADO'],
                'arrendador': {
                    'nombre': arrendador['NOMBRE'],
                    'documento': f"{arrendador['TIPO_DOCUMENTO']} {arrendador['DOCUMENTO']}",
                    'telefono': arrendador['TELEFONO'],
                    'email': arrendador['EMAIL'],
                    'direccion': arrendador['DIRECCION']
                },
                'arrendatario': {
                    'nombre': arrendatario['NOMBRE'],
                    'documento': f"{arrendatario['TIPO_DOCUMENTO']} {arrendatario['DOCUMENTO']}",
                    'telefono': arrendatario['TELEFONO'],
                    'email': arrendatario['EMAIL'],
                    'direccion': arrendatario['DIRECCION']
                },
                'inmueble': {
                    'direccion': inmueble['DIRECCION'],
                    'tipo': inmueble['TIPO'],
                    'area': str(inmueble['AREA']),
                    'habitaciones': str(inmueble['HABITACIONES']),
                    'banos': str(inmueble['BANOS']),
                    'estrato': str(inmueble['ESTRATO'])
                },
                'condiciones': {
                    'canon': contrato['CANON'],
                    'duracion_meses': contrato['DURACION_MESES'],
                    'dia_pago': contrato['DIA_PAGO'],
                    'deposito': contrato['DEPOSITO'],
                    'administracion': contrato['ADMINISTRACION']
                }
            }
    
    @classmethod
    def get_estado_cuenta_data(
        cls,
        propietario_id: int,
        periodo: str
    ) -> Optional[Dict[str, Any]]:
        """Obtiene datos para estado de cuenta"""
        
        with db_manager.transaccion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            
            # Obtener propietario
            cursor.execute("""
                SELECT nombre, tipo_documento, documento, telefono, email
                FROM PERSONAS
                WHERE id = %s
            """, (propietario_id,))
            propietario = cursor.fetchone()
            
            if not propietario:
                return None
            
            # Obtener inmuebles del propietario con contratos activos
            cursor.execute("""
                SELECT 
                    i.direccion,
                    i.tipo,
                    c.canon,
                    p.nombre as arrendatario
                FROM INMUEBLES i
                LEFT JOIN CONTRATOS c ON c.inmueble_id = i.id AND c.estado = 'ACTIVO'
                LEFT JOIN PERSONAS p ON p.id = c.arrendatario_id
                WHERE i.propietario_id = %s
                LIMIT 1
            """, (propietario_id,))
            inmueble = cursor.fetchone()
            
            # Obtener movimientos del período
            # NOTA: Ajusta según tu estructura de tablas
            cursor.execute("""
                SELECT 
                    fecha,
                    concepto,
                    CASE WHEN tipo = 'INGRESO' THEN valor ELSE 0 END as ingreso,
                    CASE WHEN tipo = 'EGRESO' THEN valor ELSE 0 END as egreso
                FROM MOVIMIENTOS
                WHERE propietario_id = %s
                  AND TO_CHAR(fecha, 'YYYY-MM') = %s
                ORDER BY fecha
            """, (propietario_id, periodo))
            movimientos = cursor.fetchall()
            
            # Calcular resumen
            total_ingresos = sum(m['INGRESO'] for m in movimientos)
            total_egresos = sum(m['EGRESO'] for m in movimientos)
            
            return {
                'estado_id': propietario_id * 100,
                'periodo': periodo,
                'propietario': {
                    'nombre': propietario['NOMBRE'],
                    'documento': f"{propietario['TIPO_DOCUMENTO']} {propietario['DOCUMENTO']}",
                    'telefono': propietario['TELEFONO'],
                    'email': propietario['EMAIL']
                },
                'inmueble': {
                    'direccion': inmueble['DIRECCION'],
                    'tipo': inmueble['TIPO'],
                    'canon': inmueble['CANON'] if inmueble['CANON'] else 0,
                    'arrendatario': inmueble['ARRENDATARIO'] if inmueble['ARRENDATARIO'] else 'Sin arrendar'
                },
                'movimientos': [
                    {
                        'fecha': m['FECHA'].strftime('%Y-%m-%d'),
                        'concepto': m['CONCEPTO'],
                        'ingreso': m['INGRESO'],
                        'egreso': m['EGRESO']
                    }
                    for m in movimientos
                ],
                'resumen': {
                    'total_ingresos': total_ingresos,
                    'total_egresos': total_egresos,
                    'honorarios': int(total_ingresos * 0.10),
                    'otros_descuentos': total_egresos - int(total_ingresos * 0.10),
                    'valor_neto': total_ingresos - total_egresos,
                    'cuenta_bancaria': 'Bancolombia ****1234',
                    'fecha_pago': f"{periodo}-15"
                }
            }
```

---

## 🔄 Paso 3: Reemplazar Mock por Real

### Modificar `pdf_state.py`

Busca estas líneas:
```python
from src.infraestructura.servicios.pdf_elite.utils.mock_data_repository import MockPDFRepository
datos = MockPDFRepository.get_contrato_data(contrato_id)
```

Reemplázalas por:
```python
from src.infraestructura.servicios.pdf_elite.utils.pdf_data_repository import PDFDataRepository
datos = PDFDataRepository.get_contrato_data(contrato_id)
```

**O mejor aún**, usa variable de entorno:

```python
# Al inicio de pdf_state.py
import os

# Elegir repository según configuración
if os.getenv('USE_MOCK_PDF_DATA', 'true').lower() == 'true':
    from src.infraestructura.servicios.pdf_elite.utils.mock_data_repository import MockPDFRepository as PDFRepository
else:
    from src.infraestructura.servicios.pdf_elite.utils.pdf_data_repository import PDFDataRepository as PDFRepository

# Luego usa:
datos = PDFRepository.get_contrato_data(contrato_id)
```

Agrega a `.env`:
```bash
# true = usa datos mock, false = usa PostgreSQL real
USE_MOCK_PDF_DATA=false
```

---

## ✅ Paso 4: Probar la Integración

### Script de Prueba
```python
# tests/test_pdf_db_integration.py

def test_contrato_desde_db():
    from src.infraestructura.servicios.pdf_elite.utils.pdf_data_repository import PDFDataRepository
    
    # Usar ID real de tu DB
    datos contrato = PDFDataRepository.get_contrato_data(1)
    
    assert datos is not None
    assert 'contrato_id' in datos
    assert 'arrendador' in datos
    print("✅ Conexión a DB exitosa!")
```

---

## 📊 Mapeo de Tablas

Ajusta los nombres según tu schema real:

| Mock | Tu DB Real | Notas |
|------|------------|-------|
| `CONTRATOS` | ¿Tu nombre? | Tabla de contratos |
| `PERSONAS` | ¿Tu nombre? | Arrendadores/arrendatarios |
| `INMUEBLES` | ¿PROPIEDADES? | Propiedades/inmuebles |
| `MOVIMIENTOS` | ¿RECAUDOS/DESCUENTOS? | Movimientos financieros |

---

## 🐛 Troubleshooting

### Error: "No module named 'pdf_data_repository'"
→ Asegúrate de crear el archivo en la ruta correcta

### Error: Columnas no encontradas
→ Revisa nombres de columnas en tus tablas (mayúsculas/minúsculas)

### Error: Conexión rechazada
→ Verifica credenciales en `.env` (DB_HOST, DB_USER, DB_PASSWORD)

---

## 🚀 Producción

1. **Crear `pdf_data_repository.py`** con queries reales
2. **Modificar `.env`**: `USE_MOCK_PDF_DATA=false`
3. **Probar** con IDs reales
4. **Desplegar**

---

**¿Necesitas ayuda?** Revisa `mock_data_repository.py` como referencia de la estructura de datos que los templates esperan.
