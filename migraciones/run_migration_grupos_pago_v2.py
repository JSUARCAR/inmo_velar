import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos

def migrar_grupos_pago():
    print("Iniciando migración de Grupos de Pago a V2...")
    db = db_manager
    conn = db.obtener_conexion()
    cursor = db.get_dict_cursor(conn)
    
    try:
        # 1. Alterar la tabla para guardar backup e indicar versión (Si no existen)
        print("Verificando schema...")
        cursor.execute("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='contratos_mandatos' AND column_name='fecha_pago_legacy') THEN
                    ALTER TABLE CONTRATOS_MANDATOS ADD COLUMN FECHA_PAGO_LEGACY VARCHAR(50);
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='contratos_mandatos' AND column_name='version_regla_pago') THEN
                    ALTER TABLE CONTRATOS_MANDATOS ADD COLUMN VERSION_REGLA_PAGO INT DEFAULT 1;
                END IF;
            END $$;
        """)
        conn.commit()
        
        # 2. Respaldar datos actuales (si no se ha respaldado antes)
        print("Respaldando fechas legacy...")
        cursor.execute("""
            UPDATE CONTRATOS_MANDATOS
            SET FECHA_PAGO_LEGACY = FECHA_PAGO
            WHERE FECHA_PAGO_LEGACY IS NULL
        """)
        conn.commit()
        
        # 3. Obtener contratos
        print("Obteniendo contratos a migrar...")
        cursor.execute("""
            SELECT ID_CONTRATO_M, FECHA_INICIO_CONTRATO_M
            FROM CONTRATOS_MANDATOS
        """)
        contratos = cursor.fetchall()
        
        print(f"Migrando {len(contratos)} contratos de mandato...")
        migrados = 0
        
        for contrato in contratos:
            id_contrato = contrato['ID_CONTRATO_M']
            fecha_inicio = contrato['FECHA_INICIO_CONTRATO_M']
            
            nuevo_grupo, nuevo_dia_pago = CalculadoraContratos.calcular_ciclo_pago_mandato(fecha_inicio)
            
            # Actualizar DB
            placeholder = db.get_placeholder()
            query_update = f"""
                UPDATE CONTRATOS_MANDATOS
                SET GRUPO_OPERATIVO = {placeholder},
                    FECHA_PAGO = {placeholder},
                    VERSION_REGLA_PAGO = 2
                WHERE ID_CONTRATO_M = {placeholder}
            """
            cursor.execute(query_update, (nuevo_grupo, str(nuevo_dia_pago), id_contrato))
            migrados += 1
            
        conn.commit()
        print(f"Migración completada. {migrados} contratos actualizados a Versión 2.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error durante la migración: {e}")
        print("Se ha realizado un ROLLBACK automático.")
        
if __name__ == "__main__":
    migrar_grupos_pago()