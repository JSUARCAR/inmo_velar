import os
import sys
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not set")
    sys.exit(1)

# Default Permissions Data
MODULES = [
    "Personas",
    "Propiedades",
    "Contratos",
    "Dashboard",
    "Liquidación Asesores",
    "Incidentes",
    "Recibos Públicos",
    "Desocupaciones",
    "Seguros",
    "Recaudos",
    "Reportes",
    "Configuración",
    "Usuarios",
    "Auditoría"
]

ACTIONS = ["VER", "CREAR", "EDITAR", "ELIMINAR"]

DDL_SCRIPT = """
-- Crear tabla PERMISOS
CREATE TABLE IF NOT EXISTS PERMISOS (
    ID_PERMISO SERIAL PRIMARY KEY,
    MODULO VARCHAR(100) NOT NULL,
    RUTA VARCHAR(200) NOT NULL,
    ACCION VARCHAR(20) NOT NULL,
    DESCRIPCION TEXT,
    CATEGORIA VARCHAR(50),
    CREATED_AT TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uk_permisos_modulo_accion UNIQUE(MODULO, ACCION)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_permisos_modulo ON PERMISOS(MODULO);
CREATE INDEX IF NOT EXISTS idx_permisos_ruta ON PERMISOS(RUTA);
CREATE INDEX IF NOT EXISTS idx_permisos_categoria ON PERMISOS(CATEGORIA);

-- Crear tabla ROL_PERMISOS
CREATE TABLE IF NOT EXISTS ROL_PERMISOS (
    ID_ROL_PERMISO SERIAL PRIMARY KEY,
    ROL VARCHAR(50) NOT NULL,
    ID_PERMISO INTEGER NOT NULL,
    ACTIVO BOOLEAN DEFAULT TRUE,
    CREATED_BY VARCHAR(100),
    CREATED_AT TIMESTAMP DEFAULT NOW(),
    UPDATED_BY VARCHAR(100),
    UPDATED_AT TIMESTAMP,
    CONSTRAINT fk_rol_permisos_permiso FOREIGN KEY (ID_PERMISO) 
        REFERENCES PERMISOS(ID_PERMISO) ON DELETE CASCADE,
    CONSTRAINT uk_rol_permisos_rol_permiso UNIQUE(ROL, ID_PERMISO)
);

-- Índices para ROL_PERMISOS
CREATE INDEX IF NOT EXISTS idx_rol_permisos_rol ON ROL_PERMISOS(ROL);
CREATE INDEX IF NOT EXISTS idx_rol_permisos_activo ON ROL_PERMISOS(ROL, ACTIVO);
CREATE INDEX IF NOT EXISTS idx_rol_permisos_permiso ON ROL_PERMISOS(ID_PERMISO);
"""

def seed_permissions():
    print(f"Connecting to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '...'}")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()

        # 1. Create Tables
        print("Creating tables...")
        cursor.execute(DDL_SCRIPT)
        conn.commit()
        print("Tables created successfully.")

        # 2. Insert Permissions
        print("Seeding permissions...")
        inserted_count = 0
        skipped_count = 0
        
        for module in MODULES:
            for action in ACTIONS:
                # Generate route slug (simplified)
                route = f"/{module.lower().replace(' ', '-')}"
                description = f"Permiso para {action} en {module}"
                
                try:
                    cursor.execute("""
                        INSERT INTO PERMISOS (MODULO, RUTA, ACCION, DESCRIPCION, CATEGORIA)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (MODULO, ACCION) DO NOTHING
                        RETURNING ID_PERMISO
                    """, (module, route, action, description, "General"))
                    
                    if cursor.fetchone():
                        inserted_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    print(f"Error inserting {module} - {action}: {e}")
                    conn.rollback()

        conn.commit()
        print(f"Permissions seeded: {inserted_count} inserted, {skipped_count} skipped.")

        # 3. Assign All Permissions to Administrador
        print("Assigning permissions to 'Administrador'...")
        cursor.execute("SELECT ID_PERMISO FROM PERMISOS")
        all_permission_ids = [row[0] for row in cursor.fetchall()]

        admin_assigned = 0
        for perm_id in all_permission_ids:
            try:
                cursor.execute("""
                    INSERT INTO ROL_PERMISOS (ROL, ID_PERMISO, ACTIVO, CREATED_BY)
                    VALUES ('Administrador', %s, TRUE, 'SYSTEM')
                    ON CONFLICT (ROL, ID_PERMISO) DO UPDATE SET ACTIVO = TRUE
                """, (perm_id,))
                admin_assigned += 1
            except Exception as e:
                 print(f"Error assigning {perm_id} to Admin: {e}")
                 conn.rollback()
        
        conn.commit()
        print(f"Assigned {admin_assigned} permissions to Administrador.")

        cursor.close()
        conn.close()
        print("Done.")

    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    seed_permissions()
