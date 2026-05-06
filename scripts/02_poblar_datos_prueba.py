"""
Script 2: Poblar Datos de Prueba (CORREGIDO)
Crea datos iniciales para validacion del sistema.
"""

import sys
from pathlib import Path
from datetime import datetime
import hashlib

# Agregar el directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infraestructura.persistencia.database import DatabaseManager
from src.dominio.entidades.persona import Persona
from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite


def crear_usuario_admin(db_manager):
    """Crea el usuario administrador directamente en BD."""
    print("Creando usuario ADMIN...")
    
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("SELECT COUNT(*) FROM USUARIOS WHERE NOMBRE_USUARIO = 'admin'")
            if cursor.fetchone()[0] > 0:
                print("  [i] Usuario admin ya existe, omitiendo...")
                return
            
            # Hashear contraseña "admin123"
            contraseña_hash = hashlib.sha256("admin123".encode('utf-8')).hexdigest()
            
            cursor.execute("""
                INSERT INTO USUARIOS (NOMBRE_USUARIO, CONTRASENA_HASH, ROL, ESTADO_USUARIO, FECHA_CREACION, CREATED_BY)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("admin", contraseña_hash, "Administrador", 1, datetime.now().isoformat(), "SYSTEM"))
            
            conn.commit()
            print("  [OK] Usuario admin creado (usuario: admin, password: admin123)")
            
    except Exception as e:
        print("  [ERROR]", str(e))


def crear_municipios_prueba(db_manager):
    """Crea municipios de prueba."""
    print("Creando municipios de prueba...")
    
    municipios_data = [
        ("BOGOTA D.C.", "BOGOTA D.C."),
        ("MEDELLIN", "ANTIOQUIA"),
        ("CALI", "VALLE DEL CAUCA"),
        ("BARRANQUILLA", "ATLANTICO"),
    ]
    
    for nombre, depto in municipios_data:
        try:
            with db_manager.obtener_conexion() as conn:
                cursor = conn.cursor()
                
                # Verificar si ya existe
                cursor.execute("SELECT COUNT(*) FROM MUNICIPIOS WHERE NOMBRE_MUNICIPIO = ?", (nombre,))
                if cursor.fetchone()[0] > 0:
                    print("  [i]", nombre, "ya existe, omitiendo...")
                    continue
                
                cursor.execute("""
                    INSERT INTO MUNICIPIOS (NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO, CREATED_AT, CREATED_BY)
                    VALUES (?, ?, 1, ?, 'SYSTEM')
                """, (nombre, depto, datetime.now().isoformat()))
                conn.commit()
                print("  [OK]", nombre, "creado")
                
        except Exception as e:
            print("  [ERROR] creando", nombre, ":", str(e))


def crear_ipc_prueba(db_manager):
    """Crea registros IPC de prueba."""
    print("Creando registros IPC...")
    
    ipc_data = [
        (2023, 13),  # 13% anual
        (2024, 9),   # 9% anual
    ]
    
    for anio, valor in ipc_data:
        try:
            with db_manager.obtener_conexion() as conn:
                cursor = conn.cursor()
                
                # Verificar si ya existe
                cursor.execute("SELECT COUNT(*) FROM IPC WHERE ANIO = ?", (anio,))
                if cursor.fetchone()[0] > 0:
                    print("  [i] IPC", anio, "ya existe, omitiendo...")
                    continue
                
                cursor.execute("""
                    INSERT INTO IPC (ANIO, VALOR_IPC, FECHA_PUBLICACION, ESTADO_REGISTRO, CREATED_AT, CREATED_BY)
                    VALUES (?, ?, ?, 1, ?, 'SYSTEM')
                """, (anio, valor, datetime.now().isoformat(), datetime.now().isoformat()))
                conn.commit()
                print("  [OK] IPC", anio, ":", valor, "% creado")
                
        except Exception as e:
            print("  [ERROR] creando IPC", anio, ":", str(e))


def crear_personas_prueba(db_manager):
    """Crea personas de prueba."""
    print("Creando personas de prueba...")
    
    repo_persona = RepositorioPersonaSQLite(db_manager)
    
    personas_data = [
        ("CC", "1234567890", "JUAN PEREZ GOMEZ", "3001234567", "juan.perez@email.com"),
        ("CC", "9876543210", "MARIA GARCIA LOPEZ", "3009876543", "maria.garcia@email.com"),
        ("NIT", "900123456", "INMOBILIARIA XYZ S.A.S.", "6012345678", "contacto@inmoxyz.com"),
    ]
    
    for tipo_doc, num_doc, nombre, tel, email in personas_data:
        try:
            # Verificar si ya existe
            persona_existente = repo_persona.obtener_por_documento(num_doc)
            if persona_existente:
                print("  [i]", nombre, "ya existe, omitiendo...")
                continue
            
            persona = Persona(
                tipo_documento=tipo_doc,
                numero_documento=num_doc,
                nombre_completo=nombre,
                telefono_principal=tel,
                correo_electronico=email
            )
            persona_creada = repo_persona.crear(persona, "admin")
            print("  [OK]", nombre, "creado (ID:", persona_creada.id_persona, ")")
            
        except Exception as e:
            print("  [ERROR] creando", nombre, ":", str(e))


def main():
    """Ejecuta el poblado de datos de prueba."""
    print("=" * 60)
    print("SCRIPT 2: POBLADO DE DATOS DE PRUEBA")
    print("=" * 60)
    print()
    
    try:
        db_manager = DatabaseManager()
        print("[OK] Conexion a base de datos establecida")
        print()
        
        crear_usuario_admin(db_manager)
        print()
        
        crear_municipios_prueba(db_manager)
        print()
        
        crear_ipc_prueba(db_manager)
        print()
        
        crear_personas_prueba(db_manager)
        print()
        
        print("=" * 60)
        print("[OK] POBLADO DE DATOS COMPLETADO")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print("[ERROR] ERROR EN EL POBLADO DE DATOS")
        print("=" * 60)
        print("Error:", str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
