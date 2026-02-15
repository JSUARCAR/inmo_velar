"""
Test Script: Verify fecha_pago is now saved correctly
"""
import sys
import os
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite
from src.aplicacion.servicios.servicio_contrato_mandato import ServicioContratoMandato
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
from src.infraestructura.persistencia.repositorio_renovacion_sqlite import RepositorioRenovacionSQLite

print("=" * 80)
print("🧪 Testing fecha_pago Save Functionality")
print("=" * 80)

# Initialize services
repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
repo_propiedad = RepositorioPropiedadSQLite(db_manager)
repo_renovacion = RepositorioRenovacionSQLite(db_manager)

servicio = ServicioContratoMandato(repo_mandato, repo_propiedad, repo_renovacion)

# Test 1: Find an existing mandate contract to update
print("\n📋 Test 1: Finding existing mandate contract...")
contratos = repo_mandato.listar_todos()
if not contratos:
    print("❌ No existing contracts found. Cannot test update.")
    sys.exit(0)

test_contract = contratos[0]
print(f"✅ Found contract ID: {test_contract.id_contrato_m}")
print(f"   Current fecha_pago: {test_contract.fecha_pago}")

# Test 2: Update with a new fecha_pago value
print("\n📝 Test 2: Updating fecha_pago to '15'...")
datos_actualizacion = {
    "id_propiedad": test_contract.id_propiedad,
    "id_propietario": test_contract.id_propietario,
    "id_asesor": test_contract.id_asesor,
    "fecha_inicio": test_contract.fecha_inicio_contrato_m,
    "fecha_fin": test_contract.fecha_fin_contrato_m,
    "duracion_meses": test_contract.duracion_contrato_m,
    "canon": test_contract.canon_mandato,
    "comision_porcentaje": test_contract.comision_porcentaje_contrato_m,
    "fecha_pago": "15"  # NEW VALUE
}

try:
    servicio.actualizar_mandato(test_contract.id_contrato_m, datos_actualizacion, "test_user")
    print("✅ Update executed successfully")
except Exception as e:
    print(f"❌ Update failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verify the value was saved
print("\n🔍 Test 3: Verifying fecha_pago was saved...")
updated_contract = repo_mandato.obtener_por_id(test_contract.id_contrato_m)
if updated_contract.fecha_pago == "15":
    print(f"✅ SUCCESS! fecha_pago correctly saved: {updated_contract.fecha_pago}")
else:
    print(f"❌ FAILED! Expected '15', but found: {updated_contract.fecha_pago}")
    sys.exit(1)

# Test 4: Restore original value
print("\n🔄 Test 4: Restoring original fecha_pago value...")
datos_restauracion = datos_actualizacion.copy()
datos_restauracion["fecha_pago"] = test_contract.fecha_pago
servicio.actualizar_mandato(test_contract.id_contrato_m, datos_restauracion, "test_user")
restored = repo_mandato.obtener_por_id(test_contract.id_contrato_m)
print(f"✅ Restored to: {restored.fecha_pago}")

print("\n" + "=" * 80)
print("🎉 ALL TESTS PASSED - fecha_pago is now saving correctly!")
print("=" * 80)
