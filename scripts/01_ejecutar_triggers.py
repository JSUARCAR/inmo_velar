"""
Script 1: Ejecutar Triggers de Auditoria
Crea todos los triggers de auditoria en la base de datos.
"""

import sys
from pathlib import Path

# Agregar el directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.triggers_auditoria import ejecutar_todos_los_triggers


def main():
    """Ejecuta los triggers de auditoria."""
    print("=" * 60)
    print("SCRIPT 1: INSTALACION DE TRIGGERS DE AUDITORIA")
    print("=" * 60)
    print()
    
    try:
        # Inicializar base de datos
        db_manager = DatabaseManager()
        print("[OK] Conexion a base de datos establecida")
        print("Archivo:", db_manager.database_path)
        print()
        
        # Verificar si existe tabla AUDITORIA_CAMBIOS
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='AUDITORIA_CAMBIOS'
            """)
            
            if not cursor.fetchone():
                print("[!] Tabla AUDITORIA_CAMBIOS no existe")
                print("Creando tabla...")
                
                cursor.execute("""
                    CREATE TABLE AUDITORIA_CAMBIOS (
                        ID_AUDITORIA INTEGER PRIMARY KEY AUTOINCREMENT,
                        TABLA_AFECTADA TEXT NOT NULL,
                        OPERACION TEXT NOT NULL,
                        ID_REGISTRO TEXT NOT NULL,
                        FECHA_HORA TEXT NOT NULL,
                        ID_USUARIO TEXT,
                        IP_ORIGEN TEXT,
                        DATOS_ANTERIORES TEXT,
                        DATOS_NUEVOS TEXT
                    )
                """)
                conn.commit()
                print("[OK] Tabla AUDITORIA_CAMBIOS creada exitosamente")
            else:
                print("[OK] Tabla AUDITORIA_CAMBIOS ya existe")
        
        print()
        print("Ejecutando triggers de auditoria...")
        
        # Ejecutar triggers
        ejecutar_todos_los_triggers(db_manager)
        
        print()
        print("=" * 60)
        print("[OK] INSTALACION COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print("[ERROR] ERROR EN LA INSTALACION")
        print("=" * 60)
        print("Error:", str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
