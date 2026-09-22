import argparse
import json
import os
import sys

sys.path.insert(0, ".")
from src.infraestructura.persistencia.database import db_manager


def del_in(cur, table, column, values, extra=""):
    if not values:
        print(f"  {table}: 0 (skip)")
        return 0
    ph = ",".join(["%s"] * len(values))
    sql = f"DELETE FROM {table} WHERE {column} IN ({ph}) {extra}"
    cur.execute(sql, tuple(values))
    print(f"  {table}: {cur.rowcount} eliminados")
    return cur.rowcount


def count_in(cur, table, column, values):
    if not values:
        print(f"  {table}: 0 candidatas")
        return 0
    ph = ",".join(["%s"] * len(values))
    sql = f"SELECT COUNT(*) FROM {table} WHERE {column} IN ({ph})"
    cur.execute(sql, tuple(values))
    count = cur.fetchone()["COUNT"]
    print(f"  {table}: {count} candidatas")
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ejecutar", action="store_true", help="borra de verdad")
    ap.add_argument("--dry-run", action="store_true", help="solo cuenta (defecto)")
    ap.add_argument("--bitacora", type=str, default="specs/076-liquidacion-requiere-arrendamiento/bitacora_test.json")
    args = ap.parse_args()
    
    ejecutar = args.ejecutar and not args.dry_run

    if not os.path.exists(args.bitacora):
        print(f"Bitacora no encontrada: {args.bitacora}")
        return

    with open(args.bitacora, "r", encoding="utf-8") as f:
        bitacora = json.load(f)

    personas = bitacora.get("personas", [])
    propiedades = bitacora.get("propiedades", [])
    contratos_a = bitacora.get("contratos_arrendamientos", [])
    contratos_m = bitacora.get("contratos_mandatos", [])
    recaudos = bitacora.get("recaudos", [])
    liquidaciones = bitacora.get("liquidaciones", [])
    propietarios = bitacora.get("propietarios", [])
    arrendatarios = bitacora.get("arrendatarios", [])

    if not ejecutar:
        print("MODO DRY-RUN (no se borra nada). Usa --ejecutar para borrar.")
        conn = db_manager.obtener_conexion()
        cur = conn.cursor()
        try:
            count_in(cur, "recaudo_conceptos", "id_recaudo", recaudos)
            count_in(cur, "recaudos", "id_recaudo", recaudos)
            
            # huérfanos incidentes
            if propiedades:
                ph_inc = ",".join(["%s"] * len(propiedades))
                cur.execute(f"SELECT id_incidente FROM incidentes WHERE id_propiedad IN ({ph_inc})", tuple(propiedades))
                inc_ids = [r["ID_INCIDENTE"] for r in cur.fetchall()]
                if inc_ids:
                    count_in(cur, "incidente_liquidacion", "id_incidente", inc_ids)
                    count_in(cur, "plan_pago_incidente", "id_incidente", inc_ids)
                    count_in(cur, "historial_incidentes", "id_incidente", inc_ids)
                    count_in(cur, "incidentes", "id_incidente", inc_ids)
            
            count_in(cur, "liquidaciones", "id_liquidacion", liquidaciones)
            count_in(cur, "contratos_arrendamientos", "id_contrato_a", contratos_a)
            count_in(cur, "contratos_mandatos", "id_contrato_m", contratos_m)
            count_in(cur, "propiedades", "id_propiedad", propiedades)
            count_in(cur, "propietarios", "id_persona", propietarios)
            count_in(cur, "arrendatarios", "id_persona", arrendatarios)
            count_in(cur, "personas", "id_persona", personas)
        finally:
            conn.close()
        return

    try:
        with db_manager.transaccion() as conn:
            cur = conn.cursor()
            
            del_in(cur, "recaudo_conceptos", "id_recaudo", recaudos)
            del_in(cur, "recaudos", "id_recaudo", recaudos)

            if propiedades:
                ph_inc = ",".join(["%s"] * len(propiedades))
                cur.execute(f"SELECT id_incidente FROM incidentes WHERE id_propiedad IN ({ph_inc})", tuple(propiedades))
                inc_ids = [r["ID_INCIDENTE"] for r in cur.fetchall()]
                if inc_ids:
                    ph_i = ",".join(["%s"] * len(inc_ids))
                    cur.execute(f"SELECT id_plan_pago FROM plan_pago_incidente WHERE id_incidente IN ({ph_i})", tuple(inc_ids))
                    plan_ids = [r["ID_PLAN_PAGO"] for r in cur.fetchall()]
                    if plan_ids:
                        del_in(cur, "cuota_incidente", "id_plan_pago", plan_ids)
                    
                    del_in(cur, "incidente_liquidacion", "id_incidente", inc_ids)
                    del_in(cur, "plan_pago_incidente", "id_incidente", inc_ids)
                    del_in(cur, "historial_incidentes", "id_incidente", inc_ids)
                    del_in(cur, "incidentes", "id_incidente", inc_ids)

            del_in(cur, "liquidaciones", "id_liquidacion", liquidaciones)
            del_in(cur, "contratos_arrendamientos", "id_contrato_a", contratos_a)
            del_in(cur, "contratos_mandatos", "id_contrato_m", contratos_m)
            del_in(cur, "propiedades", "id_propiedad", propiedades)
            del_in(cur, "propietarios", "id_persona", propietarios)
            del_in(cur, "arrendatarios", "id_persona", arrendatarios)
            del_in(cur, "personas", "id_persona", personas)
            
            print("COMMIT OK (transaccion completa).")
            
    except Exception as e:
        print(f"ROLLBACK (error detectado): {e}")
        sys.exit(1)

    print("Post-verificacion en curso...")
    try:
        conn = db_manager.obtener_conexion()
        cur = conn.cursor()
        errores = 0
        def check_0(table, col, ids):
            nonlocal errores
            if ids:
                ph = ",".join(["%s"] * len(ids))
                cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IN ({ph})", tuple(ids))
                c = cur.fetchone()["COUNT"]
                if c > 0:
                    print(f"Error: quedaron {c} registros en {table}")
                    errores += 1
        
        check_0("recaudos", "id_recaudo", recaudos)
        check_0("liquidaciones", "id_liquidacion", liquidaciones)
        check_0("contratos_arrendamientos", "id_contrato_a", contratos_a)
        check_0("contratos_mandatos", "id_contrato_m", contratos_m)
        check_0("propiedades", "id_propiedad", propiedades)
        check_0("personas", "id_persona", personas)
        
        if errores == 0:
            print("Verificacion OK. Borrando archivo bitacora...")
            os.remove(args.bitacora)
        else:
            print("Verificacion fallida, no se borra la bitacora.")
            sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
