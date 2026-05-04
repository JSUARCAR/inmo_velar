
from src.infraestructura.persistencia.database import db_manager
import os

os.environ['PYTHONPATH'] = '.'

def check_counts():
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) AS total FROM CONTRATOS_MANDATOS")
    row_m = cursor.fetchone()
    print(f"Mandatos (Dict): {row_m}")
    
    cursor.execute("SELECT COUNT(*) AS total FROM CONTRATOS_ARRENDAMIENTOS")
    row_a = cursor.fetchone()
    print(f"Arrendamientos (Dict): {row_a}")

if __name__ == '__main__':
    check_counts()
