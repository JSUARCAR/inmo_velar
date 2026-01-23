import sys
import os

# Agregar directorio raíz al path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion

def crear_usuario_admin():
    try:
        # DB Manager se autoconecta bajo demanda
        servicio = ServicioAutenticacion(db_manager)
        
        # Verificar si existe
        usuario = servicio.repo_usuario.obtener_por_nombre("admin")
        
        if usuario:
            print("✅ Usuario 'admin' ya existe.")
            # Resetear contraseña a 'admin123' para pruebas
            
            # Nota: Necesitamos hacerlo manualmente porque cambiar_contraseña requiere contraseña actual correcta
            import hashlib
            nuevo_hash = hashlib.sha256("admin123".encode('utf-8')).hexdigest()
            usuario.contrasena_hash = nuevo_hash
            
            # Usar repo directamente para actualizar
            servicio.repo_usuario.actualizar(usuario, "system_init")
            print("🔄 Contraseña reseteada a: admin123")
        else:
            print("⚠️ Usuario 'admin' no existe. Creando...")
            servicio.crear_usuario("admin", "admin123", "ADMIN", "system_init")
            print("✅ Usuario 'admin' creado exitosamente.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.cerrar_todas_conexiones()

if __name__ == "__main__":
    crear_usuario_admin()
