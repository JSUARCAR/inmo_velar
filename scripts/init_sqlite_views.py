import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()
db_path = os.getenv("DATABASE_URL", "")
if db_path.startswith("postgresql"):
    print("El entorno actual está configurado para PostgreSQL. No se requiere inicializar vistas de SQLite.")
    exit(0)

# Obtener path de SQLite
from src.infraestructura.configuracion.settings import obtener_configuracion
config = obtener_configuracion()
db_file = Path(config.database_path)

if not db_file.exists():
    print(f"La base de datos SQLite no existe en {db_file}")
    exit(1)

def create_sqlite_views():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("Iniciando creación de vistas para Dashboard en SQLite...")
    
    try:
        cursor.execute("BEGIN TRANSACTION")

        # ==========================================
        # VISTAS DASHBOARD
        # ==========================================
        print("Restaurando VW_ALERTA_VENCIMIENTO_CONTRATOS...")
        cursor.execute("DROP VIEW IF EXISTS VW_ALERTA_VENCIMIENTO_CONTRATOS;")
        cursor.execute("""
            CREATE VIEW VW_ALERTA_VENCIMIENTO_CONTRATOS AS
            SELECT 
                'ARRENDAMIENTO' AS TIPO_CONTRATO,
                ca.ID_CONTRATO_A AS ID_CONTRATO,
                ca.ID_PROPIEDAD,
                p.DIRECCION_PROPIEDAD AS DIRECCION,
                per.NOMBRE_COMPLETO AS INQUILINO_PROPIETARIO,
                ca.FECHA_FIN_CONTRATO_A AS FECHA_FIN,
                CAST(julianday(ca.FECHA_FIN_CONTRATO_A) - julianday('now') AS INTEGER) AS DIAS_RESTANTES
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN ARRENDATARIOS a ON ca.ID_ARRENDATARIO = a.ID_ARRENDATARIO
            JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
            WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
            
            UNION ALL
            
            SELECT 
                'MANDATO' AS TIPO_CONTRATO,
                cm.ID_CONTRATO_M AS ID_CONTRATO,
                cm.ID_PROPIEDAD,
                p.DIRECCION_PROPIEDAD AS DIRECCION,
                per.NOMBRE_COMPLETO AS INQUILINO_PROPIETARIO,
                cm.FECHA_FIN_CONTRATO_M AS FECHA_FIN,
                CAST(julianday(cm.FECHA_FIN_CONTRATO_M) - julianday('now') AS INTEGER) AS DIAS_RESTANTES
            FROM CONTRATOS_MANDATOS cm
            JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN PROPIETARIOS pr ON cm.ID_PROPIETARIO = pr.ID_PROPIETARIO
            JOIN PERSONAS per ON pr.ID_PERSONA = per.ID_PERSONA
            WHERE cm.ESTADO_CONTRATO_M = 'ACTIVO';
        """)

        print("Restaurando VW_ALERTA_MORA_DIARIA...")
        cursor.execute("DROP VIEW IF EXISTS VW_ALERTA_MORA_DIARIA;")
        cursor.execute("""
            CREATE VIEW VW_ALERTA_MORA_DIARIA AS
            SELECT 
                ca.ID_CONTRATO_A,
                per.NOMBRE_COMPLETO AS ARRENDATARIO,
                p.DIRECCION_PROPIEDAD AS PROPIEDAD,
                ca.CANON_ARRENDAMIENTO AS VALOR_RECAUDO,
                CAST(
                    julianday('now') - 
                    julianday(
                        strftime('%Y-%m', 'now') || '-' || 
                        substr('00' || ca.DIA_PAGO, -2, 2)
                    ) AS INTEGER
                ) AS DIAS_RETRASO
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN ARRENDATARIOS a ON ca.ID_ARRENDATARIO = a.ID_ARRENDATARIO
            JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
            WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
            AND CAST(strftime('%d', 'now') AS INTEGER) > ca.DIA_PAGO
            AND NOT EXISTS (
                SELECT 1 
                FROM RECAUDOS r 
                WHERE r.ID_CONTRATO_A = ca.ID_CONTRATO_A 
                AND strftime('%m', r.FECHA_PAGO) = strftime('%m', 'now')
                AND strftime('%Y', r.FECHA_PAGO) = strftime('%Y', 'now')
                AND r.ESTADO_RECAUDO = 'Aplicado'
            );
        """)

        conn.commit()
        print("Vistas creadas exitosamente.")

    except Exception as e:
        conn.rollback()
        print(f"Error durante la creación de vistas: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_sqlite_views()
