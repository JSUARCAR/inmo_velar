"""
Verification script for PDF Liquidaciones implementation
Tests that the new PDF methods can be called and return data
"""

import sys
sys.path.insert(0, 'src')

from aplicacion.servicios.servicio_financiero import ServicioFinanciero
from infraestructura.persistencia.database import db_manager

print("="*80)
print("Testing PDF Liquidaciones Implementation")
print("="*80)

# Test 1: Create service
print("\n1. Creating ServicioFinanciero...")
try:
    servicio = ServicioFinanciero(db_manager)
    print("   ✅ Service created successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Check method exists
print("\n2. Checking if obtener_datos_liquidacion_para_pdf exists...")
if hasattr(servicio, 'obtener_datos_liquidacion_para_pdf'):
    print("   ✅ Method exists")
else:
    print("   ❌ Method not found")
    sys.exit(1)

# Test 3: Try to fetch data for liquidacion ID 1
print("\n3. Fetching data for liquidacion_id=1...")
try:
    datos = servicio.obtener_datos_liquidacion_para_pdf(1)
    
    if datos:
        print(f"   ✅ Data retrieved successfully")
        print(f"   - Propietario: {datos.get('propietario')}")
        print(f"   - Propiedad: {datos.get('propiedad')}")
        print(f"   - Período: {datos.get('periodo')}")
        print(f"   - Canon: ${datos.get('canon'):,}")
        print(f"   - Neto: ${datos.get('neto_pagar'):,}")
        print(f"   - Keys available: {len(datos.keys())} keys")
    else:
        print("   ℹ️  No data found for liquidacion_id=1 (might not exist in DB)")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("Verification Complete")
print("="*80)
