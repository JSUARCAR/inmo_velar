import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def rollback_grupos_pago():
    print("Iniciando ROLLBACK de Grupos de Pago (Restaurando a V1)...")
    db = db_manager
    conn = db.obtener_conexion()
    cursor = db.get_dict_cursor(conn)
    
    try:
        # Verificar si existe la columna
        cursor.execute("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='contratos_mandatos' AND column_name='fecha_pago_legacy'
        """)
        if not cursor.fetchone():
            print("ERROR: No se encontró la columna de respaldo 'fecha_pago_legacy'. No se puede hacer rollback.")
            return

        print("Restaurando datos...")
        cursor.execute("""
            UPDATE CONTRATOS_MANDATOS
            SET FECHA_PAGO = FECHA_PAGO_LEGACY,
                VERSION_REGLA_PAGO = 1
            WHERE FECHA_PAGO_LEGACY IS NOT NULL
        """)
        
        # Opcional: Podríamos re-calcular los grupos operativos V1 para ser puristas,
        # pero la prioridad es la fecha de pago. Para restaurar el grupo operativo V1:
        # 1-10 -> G1, 11-20 -> G2, 21-31 -> G3
        
        cursor.execute("""
            SELECT ID_CONTRATO_M, FECHA_INICIO_CONTRATO_M FROM CONTRATOS_MANDATOS
        """)
        contratos = cursor.fetchall()
        
        for contrato in contratos:
            id_c = contrato['ID_CONTRATO_M']
            dia = int(contrato['FECHA_INICIO_CONTRATO_M'].split('-')[2][:2])
            grupo = 1 if dia <= 10 else (2 if dia <= 20 else 3)
            
            placeholder = db.get_placeholder()
            cursor.execute(f"UPDATE CONTRATOS_MANDATOS SET GRUPO_OPERATIVO = {placeholder} WHERE ID_CONTRATO_M = {placeholder}", (grupo, id_c))
            
        conn.commit()
        print("Rollback completado exitosamente.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error durante el rollback: {e}")

if __name__ == "__main__":
    rollback_grupos_pago()