import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion

def update_config():
    print("=== Actualizando Configuración ===")
    
    if not db_manager.use_postgresql:
        print("[WARN] No usando PostgreSQL.")

    try:
        config = ServicioConfiguracion(db_manager)
        
        print("\n[INFO] Valor actual DIAS_ALERTA_MANDATO: ", config.obtener_valor_parametro("DIAS_ALERTA_MANDATO"))
        
        # Actualizar a 90 días
        print("[INFO] Actualizando a 90 días...")
        
        # Nota: ServicioConfiguracion suele tener un método guardar_parametro o similar.
        # Si no, usamos SQL directo.
        # Revisando db schema: tabla CONFIGURACION (CLAVE, VALOR, ...)
        
        query = """
        INSERT INTO CONFIGURACION (CLAVE, VALOR, DESCRIPCION) 
        VALUES ('DIAS_ALERTA_MANDATO', '90', 'Días de antelación para alertas de contratos de mandato')
        ON CONFLICT (CLAVE) DO UPDATE SET VALOR = '90';
        """
        
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            
        print("[OK] DIAS_ALERTA_MANDATO actualizado a 90.")
        
        # Verificar nuevo valor
        print("[INFO] Nuevo valor: ", config.obtener_valor_parametro("DIAS_ALERTA_MANDATO"))

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_config()
