import sys
import os
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def debug_contract_1():
    print("--- Debugging Lease Contract ID 1 ---")
    
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        
        # 1. Get Contract Data
        print("\n[CONTRATO ARRENDAMIENTO ID=1]")
        cursor.execute("SELECT * FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = 1")
        contrato = cursor.fetchone()
        
        if not contrato:
            print("❌ CONTRATO NO ENCONTRADO")
            return

        c_dict = dict(contrato) if hasattr(contrato, 'keys') else contrato
        print(c_dict)
        
        id_arr = c_dict.get('ID_ARRENDATARIO') or c_dict.get('id_arrendatario')
        id_prop = c_dict.get('ID_PROPIEDAD') or c_dict.get('id_propiedad')
        
        print(f"\nLink to Arrendatario ID: {id_arr}")
        print(f"Link to Propiedad ID: {id_prop}")
        
        # 2. Check Arrendatario
        if id_arr:
            print(f"\n[ARRENDATARIO ID={id_arr}]")
            cursor.execute(f"SELECT * FROM ARRENDATARIOS WHERE ID_ARRENDATARIO = {id_arr}")
            arrendatario = cursor.fetchone()
            if arrendatario:
                a_dict = dict(arrendatario) if hasattr(arrendatario, 'keys') else arrendatario
                print(a_dict)
                id_persona = a_dict.get('ID_PERSONA') or a_dict.get('id_persona')
                
                # 3. Check Persona
                if id_persona:
                    print(f"\n[PERSONA ID={id_persona}]")
                    cursor.execute(f"SELECT * FROM PERSONAS WHERE ID_PERSONA = {id_persona}")
                    persona = cursor.fetchone()
                    if persona:
                         p_dict = dict(persona) if hasattr(persona, 'keys') else persona
                         print(p_dict)
                    else:
                        print("❌ PERSONA NO ENCONTRADA")
            else:
                print("❌ ARRENDATARIO NO ENCONTRADO")
        else:
             print("❌ ID_ARRENDATARIO es NULL/Vacío")

        # 4. Check Propiedad
        if id_prop:
             print(f"\n[PROPIEDAD ID={id_prop}]")
             cursor.execute(f"SELECT * FROM PROPIEDADES WHERE ID_PROPIEDAD = {id_prop}")
             prop = cursor.fetchone()
             if prop:
                 pr_dict = dict(prop) if hasattr(prop, 'keys') else prop
                 print(pr_dict)
             else:
                 print("❌ PROPIEDAD NO ENCONTRADA")

if __name__ == "__main__":
    debug_contract_1()
