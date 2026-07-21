import sys
import os

# Añadir el path raíz para importar configuración
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.infraestructura.persistencia.database import db_manager

def validar_mandatos(db):
    print("=== Validación Mandatos ===")
    conn = db.obtener_conexion()
    cursor = db.get_dict_cursor(conn)
    query = """
    SELECT ID_CONTRATO_M, CONSIGNATARIO, BANCO_PROPIETARIO, NUMERO_CUENTA_PROPIETARIO 
    FROM CONTRATOS_MANDATOS 
    WHERE CONSIGNATARIO IS NULL OR BANCO_PROPIETARIO IS NULL OR NUMERO_CUENTA_PROPIETARIO IS NULL
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"Mandatos con información de consignatario incompleta: {len(rows)}")
    for r in rows:
        print(f" - Contrato ID {r.get('id_contrato_m') or r.get('ID_CONTRATO_M')}: Consignatario={r.get('consignatario') or r.get('CONSIGNATARIO')}, Banco={r.get('banco_propietario') or r.get('BANCO_PROPIETARIO')}, Cuenta={r.get('numero_cuenta_propietario') or r.get('NUMERO_CUENTA_PROPIETARIO')}")
    print()

def validar_arrendamientos(db):
    print("=== Validación Arrendamientos ===")
    conn = db.obtener_conexion()
    cursor = db.get_dict_cursor(conn)
    query = """
    SELECT ca.ID_CONTRATO_A, ca.ID_CODEUDOR, c.ID_PERSONA, p.NOMBRE_COMPLETO
    FROM CONTRATOS_ARRENDAMIENTOS ca
    LEFT JOIN CODEUDORES c ON ca.ID_CODEUDOR = c.ID_CODEUDOR
    LEFT JOIN PERSONAS p ON c.ID_PERSONA = p.ID_PERSONA
    WHERE ca.ID_CODEUDOR IS NOT NULL AND p.NOMBRE_COMPLETO IS NULL
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"Arrendamientos con codeudor huérfano (sin persona): {len(rows)}")
    for r in rows:
        print(f" - Contrato ID {r.get('id_contrato_a') or r.get('ID_CONTRATO_A')}: Codeudor={r.get('id_codeudor') or r.get('ID_CODEUDOR')}")
    print()

if __name__ == "__main__":
    try:
        validar_mandatos(db_manager)
        validar_arrendamientos(db_manager)
    except Exception as e:
        print(f"Error: {e}")
