"""
Test de Funcionalidades Críticas con PostgreSQL
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from infraestructura.persistencia.database import db_manager, get_placeholder, is_postgresql
from aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion

def test_login():
    print("Testing Login...")
    servicio_auth = ServicioAutenticacion(db_manager)
    usuario = servicio_auth.autenticar('ADMIN', 'admin')
    if usuario:
        print("[OK] Login successful")
        return True
    else:
        print("[FAIL] Login failed")
        return False

def test_propiedades():
    print("Testing Propiedades List...")
    conn = db_manager.obtener_conexion()
    cursor = db_manager.get_dict_cursor(conn) # Usar dict cursor!
    placeholder = db_manager.get_placeholder()
    
    try:
        cursor.execute(f"SELECT COUNT(*) as count FROM PROPIEDADES")
        # Si es dict cursor, devuelve dict, si no, row/tuple. 
        # Pero mi test script debe ser robusto.
        row = cursor.fetchone()
        if hasattr(row, 'get'):
            count = row.get('count') or row.get('COUNT')
        else:
            count = row[0]
            
        print(f"[OK] Propiedades: {count}")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

if __name__ == '__main__':
    test_login()
    test_propiedades()
