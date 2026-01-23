"""
Script de verificación para el módulo de Configuración.
Verifica que todos los campos se guarden y actualicen correctamente.
"""

import sys
import os
from pathlib import Path

# Add project root to path
current_dir = Path(os.getcwd())
sys.path.append(str(current_dir))

from src.infraestructura.persistencia.database import db_manager
from src.dominio.entidades.configuracion_empresa import ConfiguracionEmpresa
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion

def test_configuracion_roundtrip():
    """Prueba completa de guardado y carga de configuración."""
    
    print("=== TEST: Configuración - Guardado y Carga ===\n")
    
    servicio = ServicioConfiguracion(db_manager)
    
    # 1. Crear datos de prueba
    print("1. Creando configuración de prueba...")
    test_config = ConfiguracionEmpresa(
        nombre_empresa="Test Company S.A.S.",
        nit="900.123.456-7",
        email="test@company.com",
        telefono="+57 300 999 8888",
        direccion="Calle Test 123",
        ubicacion="Bogotá D.C.",
        website="https://www.testcompany.com"
    )
    
    # Agregar redes sociales
    redes = {
        "facebook": "@testcompany",
        "instagram": "@testcompany",
        "tiktok": "@testcompany"
    }
    test_config.set_redes_sociales_from_dict(redes)
    
    print("   ✓ Configuración de prueba creada")
    print(f"   - Nombre: {test_config.nombre_empresa}")
    print(f"   - NIT: {test_config.nit}")
    print(f"   - Email: {test_config.email}")
    print(f"   - Redes: {test_config.redes_sociales_dict}")
    
    # 2. Guardar en BD
    print("\n2. Guardando en base de datos...")
    try:
        servicio.guardar_configuracion_empresa(test_config, "TEST_SCRIPT")
        print("   ✓ Datos guardados exitosamente")
    except Exception as e:
        print(f"   ✗ ERROR al guardar: {e}")
        return False
    
    # 3. Recuperar de BD
    print("\n3. Recuperando desde base de datos...")
    try:
        loaded_config = servicio.obtener_configuracion_empresa()
        print("   ✓ Datos cargados exitosamente")
    except Exception as e:
        print(f"   ✗ ERROR al cargar: {e}")
        return False
    
    # 4. Verificar campos
    print("\n4. Verificando campos...")
    fields_to_check = [
        ("nombre_empresa", test_config.nombre_empresa, loaded_config.nombre_empresa),
        ("nit", test_config.nit, loaded_config.nit),
        ("email", test_config.email, loaded_config.email),
        ("telefono", test_config.telefono, loaded_config.telefono),
        ("direccion", test_config.direccion, loaded_config.direccion),
        ("ubicacion", test_config.ubicacion, loaded_config.ubicacion),
        ("website", test_config.website, loaded_config.website),
    ]
    
    all_ok = True
    for field_name, expected, actual in fields_to_check:
        if expected == actual:
            print(f"   ✓ {field_name}: OK")
        else:
            print(f"   ✗ {field_name}: FALLO (esperado: {expected}, actual: {actual})")
            all_ok = False
    
    # Verificar redes sociales
    loaded_redes = loaded_config.redes_sociales_dict
    for red, username in redes.items():
        if loaded_redes.get(red) == username:
            print(f"   ✓ {red}: OK ({username})")
        else:
            print(f"   ✗ {red}: FALLO (esperado: {username}, actual: {loaded_redes.get(red)})")
            all_ok = False
    
    # 5. Resultado final
    print("\n" + "="*50)
    if all_ok:
        print("✅ TODOS LOS TESTS PASARON")
        print("La configuración se guarda y carga correctamente.")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("Revisa los errores anteriores.")
    print("="*50)
    
    return all_ok

if __name__ == "__main__":
    success = test_configuracion_roundtrip()
    sys.exit(0 if success else 1)
