"""Limpieza quirurgica del ruido TEST (produccion).

Elimina SOLO datos inequivocamente de prueba (IDs verificados + patrones
generados por maquina que ningun dato real usa):
  * Personas Grupo A: 'Test T22/T23 User' (DOC-T22-% / DOC-T23-%), 'Juan Test
    Renov' (TEST-DOC), 'Prop Test', 'Asesor Test'
  * Propiedades con matricula TEST-T22-% / TEST-T23-% (+ legadas TEST-*)
  * Sus contratos, recaudos, renovaciones, IPC-history y auditoria asociados
  * Idempotency keys cuyo PARAMETROS.id_contrato es un contrato test
    (match exacto por JSON, sin falsos positivos)
  * Filas IPC de prueba (anios 2096/2097, created_by test_*)
  * Municipios test (99995, 99996, 99997, 99999, 999998) y usuarios test
    (usuario_prueba, test_diagnostic) con sus sesiones

NO toca personas 219-228 (cedulas reales, fuera de alcance por decision
del usuario) ni ningun otro dato real.

Uso:
  python src/scripts/limpiar_ruido_test_grupo_a.py --dry-run   # solo informa (defecto)
  python src/scripts/limpiar_ruido_test_grupo_a.py --ejecutar  # borra en una transaccion
"""
import argparse
import sys

sys.path.insert(0, ".")
from src.infraestructura.persistencia.database import db_manager

# IDs legados ya verificados contra la BD (primera limpieza).
PERSONAS_LEGACY = [672, 673, 674, 675, 696, 703, 704, 705, 706, 999998, 999999]
PROPIEDADES_LEGACY = [100401, 100402, 100403, 100404, 100418, 100423, 100424, 100425,
                      100426, 999998]
MUNICIPIOS_TEST = [99995, 99996, 99997, 99999, 999998]
USUARIOS_TEST = [10, 20]  # usuario_prueba, test_diagnostic
# (anio, created_by) de IPC creados por los tests T22/T23.
IPC_TEST = [(2096, "test_t23"), (2097, "test_t22"), (2097, "test_t22b")]


def contador(cur, table, column, values, extra=""):
    if not values:
        return 0
    ph = ",".join(["%s"] * len(values))
    cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IN ({ph}) {extra}", tuple(values))
    row = cur.fetchone()
    if isinstance(row, dict):
        return row.get("count", row.get("COUNT", 0))
    return row[0]


def borrar(cur, table, column, values, extra=""):
    if not values:
        return 0
    ph = ",".join(["%s"] * len(values))
    cur.execute(f"DELETE FROM {table} WHERE {column} IN ({ph}) {extra}", tuple(values))
    print(f"  {table}: {cur.rowcount} filas eliminadas")
    return cur.rowcount


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ejecutar", action="store_true", help="borra de verdad")
    ap.add_argument("--dry-run", action="store_true", help="solo informa (defecto)")
    args = ap.parse_args()
    ejecutar = args.ejecutar and not args.dry_run
    if not ejecutar:
        print("MODO DRY-RUN (no se borra nada). Usa --ejecutar para borrar.")

    conn = db_manager.obtener_conexion()
    cur = conn.cursor()
    try:
        # Deteccion por patron (familias T22/T23 regeneradas en cada corrida)
        # + IDs legados. Patrones generados por maquina: sin colision real.
        cur.execute(
            "SELECT id_persona FROM personas WHERE id_persona = ANY(%s) "
            "OR numero_documento LIKE 'DOC-T22-%%' OR numero_documento LIKE 'DOC-T23-%%'",
            (PERSONAS_LEGACY,),
        )
        personas = [r["ID_PERSONA"] for r in cur.fetchall()]

        cur.execute(
            "SELECT id_propiedad FROM propiedades WHERE id_propiedad = ANY(%s) "
            "OR matricula_inmobiliaria LIKE 'TEST-T22-%%' "
            "OR matricula_inmobiliaria LIKE 'TEST-T23-%%'",
            (PROPIEDADES_LEGACY,),
        )
        propiedades = [r["ID_PROPIEDAD"] for r in cur.fetchall()]
        print(f"Personas test detectadas: {personas}")
        print(f"Propiedades test detectadas: {propiedades}")

        cur.execute(
            "SELECT id_contrato_a FROM contratos_arrendamientos WHERE id_propiedad = ANY(%s)",
            (propiedades,),
        )
        contratos = [r["ID_CONTRATO_A"] for r in cur.fetchall()]
        print(f"Contratos test detectados: {contratos}")

        cur.execute("SELECT id_recaudo FROM recaudos WHERE id_contrato_a = ANY(%s)", (contratos,))
        recaudos = [r["ID_RECAUDO"] for r in cur.fetchall()]
        cur.execute("SELECT id_recaudo_concepto FROM recaudo_conceptos WHERE id_recaudo = ANY(%s)", (recaudos,))
        conceptos = [r["ID_RECAUDO_CONCEPTO"] for r in cur.fetchall()]

        # Idempotency keys ligadas EXACTAMENTE a contratos test (JSON, sin LIKE).
        cur.execute(
            "SELECT id_key, key FROM idempotency_keys WHERE parametros->>'id_contrato' = ANY(%s)",
            ([str(c) for c in contratos],),
        )
        rows_idem = cur.fetchall()
        idem_keys = [r["ID_KEY"] for r in rows_idem]
        idem_strs = [r["KEY"] for r in rows_idem]
        cur.execute(
            "SELECT id_evento FROM eventos_idempotencia WHERE idempotency_key = ANY(%s)",
            (idem_strs,),
        )
        eventos = [r["ID_EVENTO"] for r in cur.fetchall()]

        cur.execute("SELECT id_arrendatario FROM arrendatarios WHERE id_persona = ANY(%s)", (personas,))
        ids_arrendatarios = [r["ID_ARRENDATARIO"] for r in cur.fetchall()]
        cur.execute("SELECT id_propietario FROM propietarios WHERE id_persona = ANY(%s)", (personas,))
        ids_propietarios = [r["ID_PROPIETARIO"] for r in cur.fetchall()]
        cur.execute("SELECT id_asesor FROM asesores WHERE id_persona = ANY(%s)", (personas,))
        ids_asesores = [r["ID_ASESOR"] for r in cur.fetchall()]

        print("\n--- Resumen de lo que se borrara ---")
        print(f"  conceptos_recaudo: {len(conceptos)}")
        print(f"  recaudos: {len(recaudos)}")
        print(f"  renovaciones_contratos: {contador(cur, 'renovaciones_contratos', 'id_contrato_a', contratos)}")
        print(f"  ipc_increment_history: {contador(cur, 'ipc_increment_history', 'id_contrato_a', contratos)}")
        print(f"  auditoria_propagacion_canon: {contador(cur, 'auditoria_propagacion_canon', 'contrato_id', contratos)}")
        print(f"  eventos_idempotencia: {len(eventos)}")
        print(f"  idempotency_keys: {len(idem_keys)}")
        print(f"  contratos_arrendamientos: {len(contratos)}")
        print(f"  propiedades: {len(propiedades)}")
        print(f"  municipios: {contador(cur, 'municipios', 'id_municipio', MUNICIPIOS_TEST)}")
        print(f"  arrendatarios: {len(ids_arrendatarios)}")
        print(f"  propietarios: {len(ids_propietarios)}")
        print(f"  asesores: {len(ids_asesores)}")
        print(f"  personas Grupo A: {len(personas)}")
        print(f"  sesiones_usuario: {contador(cur, 'sesiones_usuario', 'id_usuario', USUARIOS_TEST)}")
        print(f"  usuarios: {contador(cur, 'usuarios', 'id_usuario', USUARIOS_TEST)}")
        n_ipc = 0
        for anio, creador in IPC_TEST:
            cur.execute("SELECT COUNT(*) FROM ipc WHERE anio = %s AND created_by = %s", (anio, creador))
            row = cur.fetchone()
            n_ipc += row["COUNT"] if isinstance(row, dict) else row[0]
        print(f"  ipc test (2096/2097): {n_ipc}")

        if not ejecutar:
            return

        print("\nBorrando en una sola transaccion (rollback si algo falla)...")
        with db_manager.transaccion() as txn:
            c = txn.cursor()
            borrar(c, "recaudo_conceptos", "id_recaudo", recaudos)
            borrar(c, "recaudos", "id_recaudo", recaudos)
            borrar(c, "renovaciones_contratos", "id_contrato_a", contratos)
            borrar(c, "ipc_increment_history", "id_contrato_a", contratos)
            borrar(c, "auditoria_propagacion_canon", "contrato_id", contratos)
            borrar(c, "eventos_idempotencia", "id_evento", eventos)
            borrar(c, "idempotency_keys", "id_key", idem_keys)
            borrar(c, "contratos_arrendamientos", "id_contrato_a", contratos)
            borrar(c, "propiedades", "id_propiedad", propiedades)
            borrar(c, "municipios", "id_municipio", MUNICIPIOS_TEST)
            for rol, col, ids in [("arrendatarios", "id_arrendatario", ids_arrendatarios),
                                  ("propietarios", "id_propietario", ids_propietarios),
                                  ("asesores", "id_asesor", ids_asesores)]:
                borrar(c, rol, col, ids)
            borrar(c, "sesiones_usuario", "id_usuario", USUARIOS_TEST)
            borrar(c, "usuarios", "id_usuario", USUARIOS_TEST)
            borrar(c, "personas", "id_persona", personas)
            for anio, creador in IPC_TEST:
                c.execute("DELETE FROM ipc WHERE anio = %s AND created_by = %s", (anio, creador))
                print(f"  ipc ({anio}/{creador}): {c.rowcount} filas eliminadas")
            print("COMMIT OK.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
