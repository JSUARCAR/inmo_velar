
import sqlite3
import os

# Configuración
DB_PATH = 'DB_Inmo_Velar.db'

def crear_tabla_documentos():
    """Crea la tabla DOCUMENTOS si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print(f"Conectado a la base de datos: {DB_PATH}")
        
        # 1. Crear tabla DOCUMENTOS
        sql_create_table = """
        CREATE TABLE IF NOT EXISTS DOCUMENTOS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ENTIDAD_TIPO TEXT NOT NULL,
            ENTIDAD_ID TEXT NOT NULL,
            NOMBRE_ARCHIVO TEXT NOT NULL,
            EXTENSION TEXT,
            MIME_TYPE TEXT,
            DESCRIPCION TEXT,
            CONTENIDO BLOB,
            VERSION INTEGER DEFAULT 1,
            ES_VIGENTE BOOLEAN DEFAULT 1,
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CREATED_BY TEXT
        );
        """
        cursor.execute(sql_create_table)
        print("Tabla DOCUMENTOS creada o verificada.")
        
        # 2. Crear índices para búsqueda rápida
        sql_index_entidad = """
        CREATE INDEX IF NOT EXISTS idx_documentos_entidad ON DOCUMENTOS (ENTIDAD_TIPO, ENTIDAD_ID);
        """
        cursor.execute(sql_index_entidad)
        print("Índice idx_documentos_entidad creado.")
        
        # 3. Crear índice para vigencia
        sql_index_vigente = """
        CREATE INDEX IF NOT EXISTS idx_documentos_vigente ON DOCUMENTOS (ES_VIGENTE);
        """
        cursor.execute(sql_index_vigente)
        print("Índice idx_documentos_vigente creado.")
        
        conn.commit()
        print("Migración completada exitosamente.")
        
    except sqlite3.Error as e:
        print(f"Error durante la migración: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encuentra la base de datos en {DB_PATH}")
    else:
        crear_tabla_documentos()
