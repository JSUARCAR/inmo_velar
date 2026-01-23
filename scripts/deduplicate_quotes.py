import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infraestructura.persistencia.database import db_manager

def clean_duplicates():
    conn = db_manager.obtener_conexion()
    cursor = db_manager.get_dict_cursor(conn)
    
    # Get duplicates for incident 1
    # We group by provider and incident, counting them
    query = """
    SELECT ID_INCIDENTE, ID_PROVEEDOR, COUNT(*) as count
    FROM COTIZACIONES
    WHERE ID_INCIDENTE = 1
    GROUP BY ID_INCIDENTE, ID_PROVEEDOR
    HAVING COUNT(*) > 1
    """
    cursor.execute(query)
    duplicates = cursor.fetchall()
    
    print(f"Found {len(duplicates)} duplicate sets.")
    
    for dup in duplicates:
        print(f"Processing duplicates for Incidente {dup['ID_INCIDENTE']}, Proveedor {dup['ID_PROVEEDOR']}")
        
        # Get individual quotes ordered by ID (assuming higher ID = newer)
        q_details = "SELECT ID_COTIZACION, CREATED_AT FROM COTIZACIONES WHERE ID_INCIDENTE = %s AND ID_PROVEEDOR = %s ORDER BY ID_COTIZACION DESC"
        cursor.execute(q_details, (dup['ID_INCIDENTE'], dup['ID_PROVEEDOR']))
        quotes = cursor.fetchall()
        
        # Keep the latest (first in desc list), delete others
        to_keep = quotes[0]
        to_delete = quotes[1:]
        
        print(f"Keeping quote ID {to_keep['ID_COTIZACION']} (Created: {to_keep['CREATED_AT']})")
        
        for d in to_delete:
            print(f"Deleting duplicate quote ID {d['ID_COTIZACION']} (Created: {d['CREATED_AT']})")
            del_query = "DELETE FROM COTIZACIONES WHERE ID_COTIZACION = %s"
            cursor.execute(del_query, (d['ID_COTIZACION'],))
            
    conn.commit()
    print("Cleanup complete.")

if __name__ == "__main__":
    clean_duplicates()
