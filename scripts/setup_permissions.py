#!/usr/bin/env python3
"""
Script para registrar permisos de incidentes y liquidaciones
Uso: python scripts/setup_permissions.py
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


def setup_permissions():
    """Registra todos los permisos necesarios de forma idempotente."""
    import psycopg2
    
    db_url = get_database_url()
    logger.info("Conectando a la base de datos para configurar permisos...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        logger.info("Conexión exitosa. Configurando permisos...")
        
        # Lista de permisos a registrar
        permissions = [
            # Permisos de Liquidaciones
            {
                "modulo": "Liquidaciones",
                "ruta": "/liquidaciones",
                "accion": "ELIMINAR",
                "descripcion": "Eliminar liquidaciones",
                "categoria": "Gestión"
            },
            {
                "modulo": "Liquidaciones",
                "ruta": "/liquidaciones",
                "accion": "SELECCIONAR_INCIDENTES",
                "descripcion": "Seleccionar incidentes para asociar a liquidaciones",
                "categoria": "Gestión"
            },
            # Permisos de Incidentes
            {
                "modulo": "Incidentes",
                "ruta": "/incidentes",
                "accion": "DEFINIR_PLAN_PAGO",
                "descripcion": "Definir plan de pago para incidentes aprobados",
                "categoria": "Gestión"
            },
            {
                "modulo": "Incidentes",
                "ruta": "/incidentes",
                "accion": "VER_ESTADO_PAGO",
                "descripcion": "Visualizar estado de pago de incidentes",
                "categoria": "Consulta"
            },
        ]
        
        registered = 0
        existing = 0
        errors = 0
        
        for perm in permissions:
            try:
                # Verificar si ya existe
                cursor.execute("""
                    SELECT COUNT(*) as TOTAL
                    FROM PERMISOS
                    WHERE MODULO = %s AND ACCION = %s
                """, (perm["modulo"], perm["accion"]))
                
                result = cursor.fetchone()
                total = result[0] if result else 0
                
                if total > 0:
                    logger.info(f"  ⚠ {perm['modulo']}:{perm['accion']} ya existe")
                    existing += 1
                    continue
                
                # Insertar permiso
                cursor.execute("""
                    INSERT INTO PERMISOS (MODULO, RUTA, ACCION, DESCRIPCION, CATEGORIA)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    perm["modulo"],
                    perm["ruta"],
                    perm["accion"],
                    perm["descripcion"],
                    perm["categoria"]
                ))
                
                logger.info(f"  ✓ {perm['modulo']}:{perm['accion']} registrado")
                registered += 1
                
            except Exception as e:
                logger.error(f"  ✗ Error con {perm['modulo']}:{perm['accion']}: {e}")
                errors += 1
        
        # Verificar permisos registrados
        logger.info("\n--- Verificación de Permisos ---")
        cursor.execute("""
            SELECT MODULO, ACCION 
            FROM PERMISOS 
            WHERE MODULO IN ('Liquidaciones', 'Incidentes')
            ORDER BY MODULO, ACCION
        """)
        
        permisos_existentes = cursor.fetchall()
        logger.info("Permisos en base de datos:")
        for modulo, accion in permisos_existentes:
            logger.info(f"  - {modulo}:{accion}")
        
        cursor.close()
        conn.close()
        
        logger.info(f"\n--- Resumen ---")
        logger.info(f"Permisos registrados: {registered}")
        logger.info(f"Permisos existentes: {existing}")
        logger.info(f"Errores: {errors}")
        
        return errors == 0
        
    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        return False


if __name__ == "__main__":
    success = setup_permissions()
    sys.exit(0 if success else 1)
