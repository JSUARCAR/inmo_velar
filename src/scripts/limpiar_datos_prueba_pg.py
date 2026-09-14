"""Limpieza quirurgica de datos TEST en Postgres.

Lee IDs desde TEST a borrar.txt y borra SOLO esos registros en orden FK,
en una sola transaccion (rollback total si algo falla).

Uso:
  python src/scripts/limpiar_datos_prueba_pg.py --dry-run   # solo cuenta (defecto)
  python src/scripts/limpiar_datos_prueba_pg.py --ejecutar  # borra de verdad

Orden:
  1. recaudo_conceptos -> recaudos
  2. renovaciones_contratos / documentos(test)
  3. hijos de incidentes: cuota_incidente -> incidente_liquidacion /
     plan_pago_incidente / historial_incidentes -> incidentes
  4. contratos_arrendamientos
  5. propiedades
  6. roles (arrendatarios + resto por seguridad)
  7. personas
"""
import argparse
import pathlib
import sys

sys.path.insert(0, ".")
from src.infraestructura.persistencia.database import db_manager


def parse_txt(path="TEST a borrar.txt"):
    txt = pathlib.Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
    sec = None
    d = {"personas": [], "propiedades": [], "contratos": [], "recaudos": []}
    for line in txt:
        s = line.strip()
        low = s.lower()
        if "personas" in low:
            sec = "personas"
            continue
        if "propiedades" in low:
            sec = "propiedades"
            continue
        if "contratos" in low:
            sec = "contratos"
            continue
        if "recaudos" in low:
            sec = "recaudos"
            continue
        if s.isdigit() and sec:
            d[sec].append(int(s))
    for k in d:
        d[k] = sorted(set(d[k]))
    return d


def del_in(cur, table, column, values, extra=""):
    if not values:
        print(f"  {table}: sin IDs, skip")
        return 0
    ph = ",".join(["%s"] * len(values))
    sql = f"DELETE FROM {table} WHERE {column} IN ({ph}) {extra}"
    cur.execute(sql, tuple(values))
    print(f"  {table}: {cur.rowcount} filas eliminadas")
    return cur.rowcount


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ejecutar", action="store_true", help="borra de verdad")
    ap.add_argument("--dry-run", action="store_true", help="solo cuenta (defecto)")
    args = ap.parse_args()
    ejecutar = args.ejecutar and not args.dry_run
    if not ejecutar:
        print("MODO DRY-RUN (no se borra nada). Usa --ejecutar para borrar.")

    ids = parse_txt()
    print(
        f"IDs: personas={len(ids['personas'])} propiedades={len(ids['propiedades'])} "
        f"contratos_arr={len(ids['contratos'])} recaudos={len(ids['recaudos'])}"
    )
    if not ejecutar:
        # Conteo de lo que se borraria, incluyendo dependientes (solo SELECT, sin writes)
        conn = db_manager.obtener_conexion()
        cur = conn.cursor()
        try:
            for tbl, col, vals in [
                ("recaudo_conceptos", "id_recaudo", ids["recaudos"]),
                ("renovaciones_contratos", "id_contrato_a", ids["contratos"]),
                ("incidentes", "id_propiedad", ids["propiedades"]),
            ]:
                ph = ",".join(["%s"] * len(vals))
                cur.execute(f"SELECT COUNT(*) FROM {tbl} WHERE {col} IN ({ph})", tuple(vals))
                print(f"  {tbl}: {cur.fetchone()['COUNT']} filas candidatas")
        finally:
            conn.close()
        return

    with db_manager.transaccion() as conn:
        cur = conn.cursor()
        print("Borrando en orden FK...")
        del_in(cur, "recaudo_conceptos", "id_recaudo", ids["recaudos"])
        del_in(cur, "recaudos", "id_recaudo", ids["recaudos"])
        del_in(cur, "renovaciones_contratos", "id_contrato_a", ids["contratos"])
        del_in(cur, "ipc_increment_history", "id_contrato_a", ids["contratos"])
        # Hijos de incidentes test (51,52,53): borrar nietos primero
        # 1. averiguar planes ligados a esos incidentes
        ph_inc = ",".join(["%s"] * len(ids["propiedades"]))
        cur.execute(
            f"SELECT id_incidente FROM incidentes WHERE id_propiedad IN ({ph_inc})",
            tuple(ids["propiedades"]),
        )
        inc_ids = [r["ID_INCIDENTE"] for r in cur.fetchall()]
        print(f"  incidentes test detectados: {inc_ids}")
        if inc_ids:
            ph_i = ",".join(["%s"] * len(inc_ids))
            cur.execute(
                f"SELECT id_plan_pago FROM plan_pago_incidente WHERE id_incidente IN ({ph_i})",
                tuple(inc_ids),
            )
            plan_ids = [r["ID_PLAN_PAGO"] for r in cur.fetchall()]
            if plan_ids:
                ph_p = ",".join(["%s"] * len(plan_ids))
                cur.execute(
                    f"DELETE FROM cuota_incidente WHERE id_plan_pago IN ({ph_p})",
                    tuple(plan_ids),
                )
                print(f"  cuota_incidente: {cur.rowcount} filas eliminadas")
            del_in(cur, "incidente_liquidacion", "id_incidente", inc_ids)
            del_in(cur, "plan_pago_incidente", "id_incidente", inc_ids)
            del_in(cur, "historial_incidentes", "id_incidente", inc_ids)
        del_in(cur, "incidentes", "id_propiedad", ids["propiedades"])
        # 1 documento ligado a propiedad test (entidad_id es texto)
        if ids["propiedades"]:
            vals_txt = [str(x) for x in ids["propiedades"]]
            ph = ",".join(["%s"] * len(vals_txt))
            cur.execute(f"DELETE FROM documentos WHERE entidad_id IN ({ph})", tuple(vals_txt))
            print(f"  documentos: {cur.rowcount} filas eliminadas")
        del_in(cur, "contratos_arrendamientos", "id_contrato_a", ids["contratos"])
        del_in(cur, "propiedades", "id_propiedad", ids["propiedades"])
        for rol in ["arrendatarios", "codeudores", "propietarios", "asesores", "proveedores"]:
            del_in(cur, rol, "id_persona", ids["personas"])
        del_in(cur, "personas", "id_persona", ids["personas"])
        print("COMMIT OK (transaccion completa).")


if __name__ == "__main__":
    main()
