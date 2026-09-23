"""Limpieza quirurgica del ruido TEST en PROPIEDADES y PERSONAS Grupo A (produccion).

Elimina SOLO datos inequivocamente de prueba verificados contra la BD:
  * Grupo A personas: 672-675, 696, 703-706 (Test T22/T23 User, Juan Test Renov),
                      999998 (Prop Test), 999999 (Asesor Test)
  * 10 propiedades con matricula TEST-* (100401-100426, 999998)
  * Sus contratos, recaudos, renovaciones, IPC y auditoria asociados
  * Municipios test (99995, 99999, 999998) y usuarios test
    (usuario_prueba, test_diagnostic) con sus sesiones

NO toca personas 219-228 (creadas por usuario_prueba; cedulas reales,
fuera de alcance por decision del usuario).

Uso:
  python src/scripts/limpiar_ruido_test_grupo_a.py --dry-run   # solo informa (defecto)
  python src/scripts/limpiar_ruido_test_grupo_a.py --ejecutar  # borra en una transaccion
"""
import argparse
import sys

sys.path.insert(0, ".")
from src.infraestructura.persistencia.database import db_manager

# Verificado contra la BD de produccion (solo lectura) antes de escribir.
PERSONAS_GRUPO_A = [672, 673, 674, 675, 696, 703, 704, 705, 706, 999998, 999999]
PROPIEDADES_TEST = [100401, 100402, 100403, 100404, 100418, 100423, 100424, 100425, 100426, 999998]
MUNICIPIOS_TEST = [99995, 99999, 999998]
USUARIOS_TEST = [10, 20]  # usuario_prueba, test_diagnostic


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
        # Con este subquery obtenemos contratos ligados a las propiedades test.
        cur.execute(
            "SELECT id_contrato_a FROM contratos_arrendamientos WHERE id_propiedad = ANY(%s)",
            (PROPIEDADES_TEST,),
        )
        contratos = [r["ID_CONTRATO_A"] for r in cur.fetchall()]
        print(f"Contratos test detectados: {contratos}")

        # Resolver hijos de los contratos test
        cur.execute("SELECT id_recaudo FROM recaudos WHERE id_contrato_a = ANY(%s)", (contratos,))
        recaudos = [r["ID_RECAUDO"] for r in cur.fetchall()]
        cur.execute("SELECT id_recaudo_concepto FROM recaudo_conceptos WHERE id_recaudo = ANY(%s)", (recaudos,))
        conceptos = [r["ID_RECAUDO_CONCEPTO"] for r in cur.fetchall()]

        # Resolver ids de rol (arrendatarios/propietarios/asesores) de las personas Grupo A
        cur.execute("SELECT id_arrendatario FROM arrendatarios WHERE id_persona = ANY(%s)", (PERSONAS_GRUPO_A,))
        ids_arrendatarios = [r["ID_ARRENDATARIO"] for r in cur.fetchall()]
        cur.execute("SELECT id_propietario FROM propietarios WHERE id_persona = ANY(%s)", (PERSONAS_GRUPO_A,))
        ids_propietarios = [r["ID_PROPIETARIO"] for r in cur.fetchall()]
        cur.execute("SELECT id_asesor FROM asesores WHERE id_persona = ANY(%s)", (PERSONAS_GRUPO_A,))
        ids_asesores = [r["ID_ASESOR"] for r in cur.fetchall()]

        print("\n--- Resumen de lo que se borrara ---")
        print(f"  conceptos_recaudo: {len(conceptos)}")
        print(f"  recaudos: {len(recaudos)}")
        print(f"  renovaciones_contratos: {contador(cur, 'renovaciones_contratos', 'id_contrato_a', contratos)}")
        print(f"  ipc_increment_history: {contador(cur, 'ipc_increment_history', 'id_contrato_a', contratos)}")
        print(f"  auditoria_propagacion_canon: {contador(cur, 'auditoria_propagacion_canon', 'contrato_id', contratos)}")
        print(f"  contratos_arrendamientos: {len(contratos)}")
        print(f"  propiedades: {contador(cur, 'propiedades', 'id_propiedad', PROPIEDADES_TEST)}")
        print(f"  municipios: {contador(cur, 'municipios', 'id_municipio', MUNICIPIOS_TEST)}")
        print(f"  arrendatarios: {len(ids_arrendatarios)}")
        print(f"  propietarios: {len(ids_propietarios)}")
        print(f"  asesores: {len(ids_asesores)}")
        print(f"  personas Grupo A: {contador(cur, 'personas', 'id_persona', PERSONAS_GRUPO_A)}")
        print(f"  sesiones_usuario: {contador(cur, 'sesiones_usuario', 'id_usuario', USUARIOS_TEST)}")
        print(f"  usuarios: {contador(cur, 'usuarios', 'id_usuario', USUARIOS_TEST)}")

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
            borrar(c, "contratos_arrendamientos", "id_contrato_a", contratos)
            borrar(c, "propiedades", "id_propiedad", PROPIEDADES_TEST)
            borrar(c, "municipios", "id_municipio", MUNICIPIOS_TEST)
            for rol, col, ids in [("arrendatarios", "id_arrendatario", ids_arrendatarios),
                                  ("propietarios", "id_propietario", ids_propietarios),
                                  ("asesores", "id_asesor", ids_asesores)]:
                borrar(c, rol, col, ids)
            borrar(c, "sesiones_usuario", "id_usuario", USUARIOS_TEST)
            borrar(c, "usuarios", "id_usuario", USUARIOS_TEST)
            borrar(c, "personas", "id_persona", PERSONAS_GRUPO_A)
            print("COMMIT OK.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()