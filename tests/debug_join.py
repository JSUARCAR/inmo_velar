
import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import DatabaseManager

def test_join_query():
    print("=== Testing JOIN Query for Dropdown ===")
    db = DatabaseManager()
    
    with db.obtener_conexion() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT 
                ca.ID_CONTRATO_A, 
                p.DIRECCION_PROPIEDAD as DIRECCION,
                per.NOMBRE_COMPLETO as INQUILINO,
                ca.ESTADO_CONTRATO_A
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            WHERE ca.ESTADO_CONTRATO_A = 'Activo'
        """
        print(f"Executing query: {query}")
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"Rows found: {len(rows)}")
        for row in rows:
            print(dict(row))
            
        if len(rows) == 0:
            print("\n--- Diagnostic: Why 0 rows? ---")
            # Check if property and tenant exist
            cursor.execute("SELECT * FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo'")
            actives = cursor.fetchall()
            for a in actives:
                a_dict = dict(a)
                print(f"Active Contract: {a_dict}")
                
                # Check Property
                cursor.execute("SELECT * FROM PROPIEDADES WHERE ID_PROPIEDAD = ?", (a_dict['ID_PROPIEDAD'],))
                prop = cursor.fetchone()
                print(f"  Property {a_dict['ID_PROPIEDAD']}: {'Found' if prop else 'MISSING'}")
                
                # Check Tenant
                cursor.execute("SELECT * FROM PERSONAS WHERE ID_PERSONA = ?", (a_dict['ID_ARRENDATARIO'],))
                tenant = cursor.fetchone()
                print(f"  Tenant {a_dict['ID_ARRENDATARIO']}: {'Found' if tenant else 'MISSING'}")

if __name__ == "__main__":
    test_join_query()
