from dotenv import load_dotenv
load_dotenv()
from src.infraestructura.persistencia.database import db_manager

def migrar():
    print("Iniciando migración para corregir typo ALERTA_VENCIMINETO_CONTRATO_M en base de datos...")
    
    sql_query = "ALTER TABLE CONTRATOS_MANDATOS RENAME COLUMN ALERTA_VENCIMINETO_CONTRATO_M TO ALERTA_VENCIMIENTO_CONTRATO_M;"
    
    try:
        db_manager.execute_write(sql_query)
        print("Migración ejecutada con éxito.")
    except Exception as e:
        print(f"La migración falló o la columna ya fue migrada. Detalles: {e}")

if __name__ == "__main__":
    migrar()
