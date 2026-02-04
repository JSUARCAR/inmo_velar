
import sys
import os

# Adjust path to include src
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_liquidacion_sqlite import RepositorioLiquidacionSQLite

def debug_liquidation(id_liq):
    db = DatabaseManager()
    repo = RepositorioLiquidacionSQLite(db)
    
    data = repo.obtener_datos_para_pdf(id_liq)
    
    print(f"--- Debugging Liquidation {id_liq} ---")
    if not data:
        print("No data found.")
        return

    print(f"Seguro PCT: {data.get('seguro_pct')}")
    print(f"Comision PCT Contrato: {data.get('comision_pct_contrato')}")
    print(f"Comision PCT (Liquidacion): {data.get('comision_pct')}")
    print(f"Valor Admin: {data.get('valor_administracion')}")
    print(f"ID Contrato M: {data.get('id_contrato')}")
    
    # Let's also check if there is an active lease contract linked
    conn = db.obtener_conexion()
    cursor = db.get_dict_cursor(conn)
    cursor.execute(f"SELECT ID_CONTRATO_M FROM LIQUIDACIONES WHERE ID_LIQUIDACION = {id_liq}")
    row = cursor.fetchone()
    if row:
        id_contrato_m = row['ID_CONTRATO_M']
        print(f"Linked Mandate ID: {id_contrato_m}")
        # Get property from mandate
        cursor.execute(f"SELECT ID_PROPIEDAD FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = {id_contrato_m}")
        prop_row = cursor.fetchone()
        if prop_row:
            id_prop = prop_row['ID_PROPIEDAD']
            print(f"Property ID: {id_prop}")
            
            # Check Property Table directly
            cursor.execute(f"SELECT VALOR_ADMINISTRACION, DIRECCION_PROPIEDAD FROM PROPIEDADES WHERE ID_PROPIEDAD = {id_prop}")
            p_data = cursor.fetchone()
            print(f"DIRECT DB CHECK - Propiedad: {p_data['DIRECCION_PROPIEDAD']}, Valor Admin: {p_data['VALOR_ADMINISTRACION']}")
            
            # Check Lease Contract
            cursor.execute(f"SELECT * FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_PROPIEDAD = {id_prop}")
            leases = cursor.fetchall()
            print(f"Lease Contracts found: {len(leases)}")
            for l in leases:
                print(f"  Lease ID: {l['ID_CONTRATO_A']}, Status: {l['ESTADO_CONTRATO_A']}")
                
                # Check Tenant
                id_arr = l['ID_ARRENDATARIO']
                cursor.execute(f"SELECT * FROM ARRENDATARIOS WHERE ID_ARRENDATARIO = {id_arr}")
                arr = cursor.fetchone()
                if arr:
                    print(f"  Tenant ID: {id_arr}, ID_SEGURO: {arr.get('ID_SEGURO')}")
                    if arr.get('ID_SEGURO'):
                        cursor.execute(f"SELECT * FROM SEGUROS WHERE ID_SEGURO = {arr['ID_SEGURO']}")
                        seg = cursor.fetchone()
                        print(f"    Insurance from Tenant: {seg['NOMBRE_SEGURO']} ({seg['PORCENTAJE_SEGURO']}%)")

                # Check Policies for this lease
                cursor.execute(f"SELECT * FROM POLIZAS WHERE ID_CONTRATO = {l['ID_CONTRATO_A']}")
                polizas = cursor.fetchall()
                print(f"  Policies found: {len(polizas)}")
                for p in polizas:
                    print(f"    Policy ID: {p['ID_POLIZA']}, Status: {p['ESTADO']}, ID_SEGURO: {p['ID_SEGURO']}")
    
    print(f"FINAL CHECK: Valor Admin = {data.get('valor_administracion')}")

if __name__ == "__main__":
    debug_liquidation(15)
