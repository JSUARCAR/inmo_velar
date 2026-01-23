
import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_seguros import ServicioSeguros

def run_verification():
    print("=== Iniciando Verificación Módulo Seguros ===")
    
    db_manager = DatabaseManager()
    servicio = ServicioSeguros(db_manager)
    
    # 1. Verificar Alias en Dropdown
    print("\n[TEST 1] Verificando alias 'DIRECCION' en listar_contratos_candidatos...")
    try:
        contratos = servicio.listar_contratos_candidatos()
        if not contratos:
            print("WARNING: No hay contratos candidatos para verificar (Base de datos vacía o sin contratos activos?)")
        else:
            first = contratos[0]
            if 'DIRECCION' in first:
                print(f"SUCCESS: Clave 'DIRECCION' encontrada en el resultado: {first['DIRECCION']}")
            else:
                print(f"FAIL: Clave 'DIRECCION' NO encontrada. Claves presentes: {list(first.keys())}")
    except Exception as e:
        print(f"FAIL: Exception al listar contratos: {e}")

    # 2. Verificar Renombramiento de activar_seguro
    print("\n[TEST 2] Verificando método activar_seguro...")
    if hasattr(servicio, 'activar_seguro'):
        print("SUCCESS: Método 'activar_seguro' existe en ServicioSeguros.")
    else:
        print("FAIL: Método 'activar_seguro' NO encontrado en ServicioSeguros.")
        return

    # 3. Prueba Funcional Activar/Desactivar
    print("\n[TEST 3] Prueba funcional (Create -> Desactivar -> Activar)...")
    try:
        # Create dummy seguro
        nombre_test = "Seguro Test Verification"
        # Cleanup first if exists using raw sql to avoid service constraints if any
        with db_manager.obtener_conexion() as conn:
            conn.execute("DELETE FROM SEGUROS WHERE NOMBRE_SEGURO = ?", (nombre_test,))
        
        nuevo_seguro = servicio.crear_seguro({
            "nombre_seguro": nombre_test,
            "porcentaje_seguro": 10,
            "fecha_inicio_seguro": "2024-01-01"
        }, "test_script")
        print(f"Seguro creado: ID {nuevo_seguro.id_seguro} - Estado: {nuevo_seguro.estado_seguro}")
        
        # Desactivar
        servicio.desactivar_seguro(nuevo_seguro.id_seguro, "Test desactivar", "test_script")
        s_des = servicio.obtener_seguro(nuevo_seguro.id_seguro)
        print(f"Seguro desactivado - Estado: {s_des.estado_seguro} (Esperado: 0 o False)")
        
        # Activar (The fix!)
        servicio.activar_seguro(nuevo_seguro.id_seguro, "test_script")
        s_act = servicio.obtener_seguro(nuevo_seguro.id_seguro)
        print(f"Seguro reactivado - Estado: {s_act.estado_seguro} (Esperado: 1 o True)")
        
        if s_act.esta_activo():
            print("SUCCESS: El seguro fue reactivado correctamente usando 'activar_seguro'.")
        else:
            print("FAIL: El seguro no aparece como activo.")
            
        # Cleanup
        with db_manager.obtener_conexion() as conn:
            conn.execute("DELETE FROM SEGUROS WHERE ID_SEGURO = ?", (nuevo_seguro.id_seguro,))
            
    except Exception as e:
        print(f"FAIL: Excepción durante flujos de prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_verification()
