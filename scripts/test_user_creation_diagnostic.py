"""
Script de prueba completa del módulo de usuarios con limpieza previa.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.aplicacion.servicios.servicio_usuarios import ServicioUsuarios
from src.infraestructura.persistencia.database import db_manager

def limpiar_usuario_prueba():
    """Elimina el usuario de prueba si existe."""
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        cursor.execute("DELETE from USUARIOS WHERE NOMBRE_USUARIO = %s", ("test_diagnostic",))
        cursor.execute("DELETE FROM USUARIOS WHERE NOMBRE_USUARIO = %s", ("usuario_prueba",))
        conn.commit()
        print("✓ Usuarios de prueba eliminados")
    except Exception as e:
        print(f"  (Usuarios de prueba no existían: {e})")

def test_crear_usuario():
    """Prueba la creación de un nuevo usuario."""
    try:
        print("\n" + "=" * 60)
        print("PRUEBA: Creación de Usuario")
        print("=" * 60)
        
        servicio = ServicioUsuarios(db_manager)
        
        # Intentar crear un usuario de prueba
        print("\n1. Intentando crear usuario 'test_diagnostic'...")
        
        usuario = servicio.crear_usuario(
            nombre_usuario="test_diagnostic",
            contrasena="test123456",
            rol="Asesor",
            creador="admin"
        )
        
        print(f"✓ Usuario creado exitosamente!")
        print(f"  ID: {usuario.id_usuario}")
        print(f"  Nombre: {usuario.nombre_usuario}")
        print(f"  Rol: {usuario.rol}")
        print(f"  Estado: {'Activo' if usuario.es_activo() else 'Inactivo'}")
        
        # Verificar que el usuario se puede consultar
        print("\n2. Verificando que el usuario existe en la BD...")
        usuario_consultado = servicio.obtener_usuario(usuario.id_usuario)
        
        if usuario_consultado:
            print("✓ Usuario encontrado en la base de datos")
        else:
            print("✗ ERROR: Usuario NO encontrado en la base de datos")
            return False
        
        # Prueba 3: Cambiar estado
        print("\n3. Probando cambio de estado...")
        servicio.cambiar_estado(usuario.id_usuario, False, "admin")
        usuario_inactivo = servicio.obtener_usuario(usuario.id_usuario)
        if not usuario_inactivo.es_activo():
            print("✓ Usuario desactivado correctamente")
        else:
            print("✗ ERROR: No se pudo desactivar el usuario")
            return False
        
        # Prueba 4: Reactivar
        servicio.cambiar_estado(usuario.id_usuario, True, "admin")
        usuario_activo = servicio.obtener_usuario(usuario.id_usuario)
        if usuario_activo.es_activo():
            print("✓ Usuario reactivado correctamente")
        else:
            print("✗ ERROR: No se pudo reactivar el usuario")
            return False
        
        # Prueba 5: Actualizar datos
        print("\n4. Probando actualización de datos...")
        servicio.actualizar_usuario(
            usuario.id_usuario,
            {"rol": "Operativo"},
            "admin"
        )
        usuario_actualizado = servicio.obtener_usuario(usuario.id_usuario)
        if usuario_actualizado.rol == "Operativo":
            print("✓ Rol actualizado correctamente")
        else:
            print("✗ ERROR: No se pudo actualizar el rol")
            return False
            
        print("\n" + "=" * 60)
        print("RESULTADO: ✅ TODAS LAS PRUEBAS EXITOSAS")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR DETECTADO:")
        print(f"  Tipo: {type(e).__name__}")
        print(f"  Mensaje: {str(e)}")
        
        # Información adicional de debug
        import traceback
        print("\nStack trace completo:")
        traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("RESULTADO: ❌ PRUEBA FALLIDA")
        print("=" * 60)
        
        return False

if __name__ == "__main__":
    print("Iniciando pruebas del módulo de usuarios...\n")
    limpiar_usuario_prueba()
    success = test_crear_usuario()
    sys.exit(0 if success else 1)
