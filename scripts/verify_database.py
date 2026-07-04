#!/usr/bin/env python3
"""
Script de Verificación de Estado de Base de Datos
Uso: python scripts/verify_database.py
Requiere: Variable de entorno DATABASE_URL configurada
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def get_database_url():
    """Obtiene DATABASE_URL del entorno o lanza error."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL no está configurada en el entorno")
        sys.exit(1)
    return db_url


def verify_database():
    """Verifica el estado completo de la base de datos."""
    import psycopg2
    
    db_url = get_database_url()
    logger.info("Verificando estado de la base de datos...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        logger.info("Conexión exitosa.\n")
        
        # 1. Verificar tablas críticas
        logger.info("=== 1. Tablas Críticas ===")
        required_tables = [
            'incidentes', 'liquidaciones', 'propiedades', 'personas',
            'plan_pago_incidente', 'cuota_incidente', 'incidente_liquidacion',
            'bloqueos_edicion', 'permisos', 'usuarios'
        ]
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        existing_tables = [r[0] for r in cursor.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                logger.info(f"  ✓ {table}")
            else:
                logger.error(f"  ✗ {table} - MISSING")
        
        # 2. Verificar columnas críticas
        logger.info("\n=== 2. Columnas Críticas ===")
        required_columns = [
            ('incidentes', 'estado_pago'),
            ('liquidaciones', 'valor_incidentes'),
        ]
        
        for table, column in required_columns:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            """, (table, column))
            
            col = cursor.fetchone()
            if col:
                logger.info(f"  ✓ {table}.{column}")
            else:
                logger.error(f"  ✗ {table}.{column} - MISSING")
        
        # 3. Verificar permisos
        logger.info("\n=== 3. Permisos Críticos ===")
        required_permissions = [
            ('Liquidaciones', 'ELIMINAR'),
            ('Liquidaciones', 'SELEC_INCIDENTES'),
            ('Incidentes', 'DEFINIR_PLAN_PAGO'),
            ('Incidentes', 'VER_ESTADO_PAGO'),
        ]
        
        for modulo, accion in required_permissions:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM PERMISOS 
                WHERE MODULO = %s AND ACCION = %s
            """, (modulo, accion))
            
            count = cursor.fetchone()[0]
            if count > 0:
                logger.info(f"  ✓ {modulo}:{accion}")
            else:
                logger.error(f"  ✗ {modulo}:{accion} - MISSING")
        
        # 4. Verificar triggers
        logger.info("\n=== 4. Triggers ===")
        cursor.execute("""
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE trigger_schema = 'public'
            AND trigger_name LIKE '%incidente%'
        """)
        
        triggers = [r[0] for r in cursor.fetchall()]
        if triggers:
            for trigger in triggers:
                logger.info(f"  ✓ {trigger}")
        else:
            logger.warning("  ⚠ No incident-related triggers found")
        
        # 5. Verificar índices
        logger.info("\n=== 5. Índices Críticos ===")
        required_indexes = [
            'idx_incidentes_estado_pago',
            'idx_liquidaciones_valor_incidentes',
            'idx_plan_pago_incidente_id_incidente',
        ]
        
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public'
            AND indexname LIKE 'idx_%'
        """)
        
        existing_indexes = [r[0] for r in cursor.fetchall()]
        
        for index in required_indexes:
            if index in existing_indexes:
                logger.info(f"  ✓ {index}")
            else:
                logger.warning(f"  ⚠ {index} - not found")
        
        # 6. Estadísticas generales
        logger.info("\n=== 6. Estadísticas Generales ===")
        
        cursor.execute("SELECT COUNT(*) FROM incidentes")
        incidentes_count = cursor.fetchone()[0]
        logger.info(f"  Incidentes totales: {incidentes_count}")
        
        cursor.execute("SELECT COUNT(*) FROM liquidaciones")
        liquidaciones_count = cursor.fetchone()[0]
        logger.info(f"  Liquidaciones totales: {liquidaciones_count}")
        
        cursor.execute("SELECT COUNT(*) FROM plan_pago_incidente")
        planes_count = cursor.fetchone()[0]
        logger.info(f"  Planes de pago: {planes_count}")
        
        cursor.execute("SELECT COUNT(*) FROM permisos")
        permisos_count = cursor.fetchone()[0]
        logger.info(f"  Permisos totales: {permisos_count}")
        
        cursor.close()
        conn.close()
        
        logger.info("\n=== Verificación Completada ===")
        return True
        
    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        return False


if __name__ == "__main__":
    success = verify_database()
    sys.exit(0 if success else 1)
