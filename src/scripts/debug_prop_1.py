import os
import sys

# Add src to path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager


def debug_prop_1():
    print("--- Debugging Property 1 ---")
    query_prop = "SELECT * FROM PROPIEDADES WHERE ID_PROPIEDAD = 1"

    query_mandatos = "SELECT * FROM CONTRATOS_MANDATOS WHERE ID_PROPIEDAD = 1"

    query_arriendos = "SELECT * FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_PROPIEDAD = 1"

    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)

        print("\n[PROPIEDAD]:")
        cursor.execute(query_prop)
        props = cursor.fetchall()
        for p in props:
            # Handle potential dict wrapper
            p_dict = dict(p) if hasattr(p, "keys") else p
            print(p_dict)

        print("\n[MANDATOS]:")
        cursor.execute(query_mandatos)
        mandatos = cursor.fetchall()
        for m in mandatos:
            m_dict = dict(m) if hasattr(m, "keys") else m
            print(
                f"ID: {m_dict.get('ID_CONTRATO_M', m_dict.get('id_contrato_m'))} - Estado: {m_dict.get('ESTADO_CONTRATO_M', m_dict.get('estado_contrato_m'))}"
            )

        print("\n[ARRENDAMIENTOS]:")
        cursor.execute(query_arriendos)
        arriendos = cursor.fetchall()
        for a in arriendos:
            a_dict = dict(a) if hasattr(a, "keys") else a
            print(
                f"ID: {a_dict.get('ID_CONTRATO_A', a_dict.get('id_contrato_a'))} - Estado: {a_dict.get('ESTADO_CONTRATO_A', a_dict.get('estado_contrato_a'))}"
            )


if __name__ == "__main__":
    debug_prop_1()
