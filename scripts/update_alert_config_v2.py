import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion

def update_config():
    print("=== Actualizando Configuración (Retry) ===")
    
    try:
        # Check current
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # Try UPDATE first
            cursor.execute("UPDATE CONFIGURACION SET VALOR = '90' WHERE CLAVE = 'DIAS_ALERTA_MANDATO'")
            if cursor.rowcount == 0:
                print("[INFO] No existe, insertando...")
                cursor.execute("INSERT INTO CONFIGURACION (CLAVE, VALOR, DESCRIPCION) VALUES ('DIAS_ALERTA_MANDATO', '90', 'Días de antelación para alertas de contratos de mandato')")
            else:
                print("[INFO] Actualizado existente.")
                
            conn.commit()
            
        print("[OK] Configuración actualizada.")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_config()
