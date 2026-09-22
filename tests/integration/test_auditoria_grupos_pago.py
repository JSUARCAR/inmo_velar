"""
Tests de integración para el script de auditoría y remediación de grupos de pago (T013, T016).
Cubre Spec §FR-001, §FR-009, §FR-010, §FR-013, §SC-002, §SC-005.
"""

import os
import uuid
import pytest
from src.infraestructura.persistencia.database import DatabaseManager

# Importación diferida del script de remediación (T014 / T015)
try:
    from scripts.remediacion.remediar_grupos_pago_v4 import (
        auditar_y_remediar_grupos_pago,
    )
except ImportError:
    auditar_y_remediar_grupos_pago = None


def _require_db() -> DatabaseManager:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    return DatabaseManager()


def _get_val(row, key: str, idx: int = 0):
    """Extrae un valor de forma segura tanto si row es tuple como si es dict/RealDictRow."""
    if row is None:
        return None
    if isinstance(row, (tuple, list)):
        return row[idx]
    if hasattr(row, "get"):
        val = row.get(key)
        if val is not None:
            return val
        val = row.get(key.upper())
        if val is not None:
            return val
        val = row.get(key.lower())
        if val is not None:
            return val
    try:
        return row[key]
    except Exception:
        try:
            return row[idx]
        except Exception:
            return None


@pytest.fixture
def test_auditoria_ctx():
    """Crea un ecosistema de datos de prueba para auditar y garantiza limpieza estricta (SC-005)."""
    db = _require_db()
    suffix = uuid.uuid4().hex[:8]
    matricula = f"TEST-AUD-{suffix}"
    doc_arrendatario = f"DOC-AUDA-{suffix}"
    doc_propietario = f"DOC-AUDP-{suffix}"

    id_propiedad = None
    id_persona_a = None
    id_arrendatario = None
    id_persona_p = None
    id_propietario = None
    id_asesor = None

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        # Municipio dummy
        cursor.execute(
            """INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO)
               VALUES (99995, 'MUN TEST AUD', 'DEPTO AUD', TRUE)
               ON CONFLICT (ID_MUNICIPIO) DO NOTHING"""
        )
        # Propiedad
        cursor.execute(
            """INSERT INTO PROPIEDADES (
                   MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO,
                   ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO,
                   DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
               ) VALUES (
                   %s, 'Direccion Test AUD', TRUE, 99995,
                   'Apartamento', 80.0, 3, TRUE, 1500000
               ) RETURNING ID_PROPIEDAD""",
            (matricula,),
        )
        id_propiedad = _get_val(cursor.fetchone(), "ID_PROPIEDAD", 0)

        # Persona y Arrendatario
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Arrendatario Test AUD', TRUE) RETURNING ID_PERSONA",
            (doc_arrendatario,),
        )
        id_persona_a = _get_val(cursor.fetchone(), "ID_PERSONA", 0)
        cursor.execute(
            "INSERT INTO ARRENDATARIOS (ID_PERSONA, ESTADO_ARRENDATARIO) "
            "VALUES (%s, TRUE) RETURNING ID_ARRENDATARIO",
            (id_persona_a,),
        )
        id_arrendatario = _get_val(cursor.fetchone(), "ID_ARRENDATARIO", 0)

        # Persona y Propietario
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Propietario Test AUD', TRUE) RETURNING ID_PERSONA",
            (doc_propietario,),
        )
        id_persona_p = _get_val(cursor.fetchone(), "ID_PERSONA", 0)
        cursor.execute(
            "INSERT INTO PROPIETARIOS (ID_PERSONA, ESTADO_PROPIETARIO) "
            "VALUES (%s, TRUE) RETURNING ID_PROPIETARIO",
            (id_persona_p,),
        )
        id_propietario = _get_val(cursor.fetchone(), "ID_PROPIETARIO", 0)

        cursor.execute("SELECT ID_ASESOR FROM ASESORES LIMIT 1")
        row_ase = cursor.fetchone()
        id_asesor = _get_val(row_ase, "ID_ASESOR", 0) if row_ase else 1
        conn.commit()

    contexto = {
        "db": db,
        "matricula": matricula,
        "id_propiedad": id_propiedad,
        "id_arrendatario": id_arrendatario,
        "id_propietario": id_propietario,
        "id_asesor": id_asesor,
        "id_contrato_m": None,
        "id_contrato_a": None,
    }

    yield contexto

    # Limpieza total obligatoria (SC-005, FR-013)
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        c_a = contexto.get("id_contrato_a")
        c_m = contexto.get("id_contrato_m")
        if c_a:
            cursor.execute(
                "DELETE FROM IPC_INCREMENT_HISTORY WHERE ID_CONTRATO_A = %s", (c_a,)
            )
            cursor.execute(
                "DELETE FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s", (c_a,)
            )
            cursor.execute("DELETE FROM RECAUDOS WHERE ID_CONTRATO_A = %s", (c_a,))
            cursor.execute(
                "DELETE FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = %s", (c_a,)
            )
        if c_m:
            cursor.execute(
                "DELETE FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_M = %s", (c_m,)
            )
            cursor.execute(
                "DELETE FROM LIQUIDACIONES_PROPIETARIOS WHERE ID_CONTRATO_M = %s",
                (c_m,),
            )
            cursor.execute(
                "DELETE FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = %s", (c_m,)
            )
        if id_propiedad:
            cursor.execute(
                "DELETE FROM PROPIEDADES WHERE ID_PROPIEDAD = %s", (id_propiedad,)
            )
        if id_arrendatario:
            cursor.execute(
                "DELETE FROM ARRENDATARIOS WHERE ID_ARRENDATARIO = %s",
                (id_arrendatario,),
            )
        if id_persona_a:
            cursor.execute(
                "DELETE FROM PERSONAS WHERE ID_PERSONA = %s", (id_persona_a,)
            )
        if id_propietario:
            cursor.execute(
                "DELETE FROM PROPIETARIOS WHERE ID_PROPIETARIO = %s", (id_propietario,)
            )
        if id_persona_p:
            cursor.execute(
                "DELETE FROM PERSONAS WHERE ID_PERSONA = %s", (id_persona_p,)
            )
        conn.commit()


def test_T013_auditoria_solo_lectura_y_commit_idempotente(test_auditoria_ctx):
    """
    T013 (US2): Prueba que:
    1. Auditoría en modo solo-lectura detecta discrepancias sin modificar datos.
    2. Auditoría con --commit corrige atómicamente las discrepancias.
    3. Una segunda corrida reporta 0 discrepancias (Idempotencia, SC-002).
    """
    if auditar_y_remediar_grupos_pago is None:
        pytest.fail(
            "scripts/remediacion/remediar_grupos_pago_v4.py no está implementado"
        )

    db = test_auditoria_ctx["db"]
    id_prop = test_auditoria_ctx["id_propiedad"]
    id_arr = test_auditoria_ctx["id_arrendatario"]
    id_owner = test_auditoria_ctx["id_propietario"]
    id_ase = test_auditoria_ctx["id_asesor"]

    # Crear contrato con discrepancia intencional:
    # Inicio 2025-05-18 (tramo 18..27 -> esperado G3, día 30 para mandato, día 18 para arriendo)
    # Pero guardamos grupo 1 y día '10' / '1'
    # ORDEN: primero el arriendo y luego el mandato, porque el trigger
    # trg_sync_fechas_mandato reescribe el grupo del mandato activo al
    # insertar/actualizar un arriendo (Spec 075, causa raíz de recurrencia).
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO CONTRATOS_ARRENDAMIENTOS (
                   ID_PROPIEDAD, ID_ARRENDATARIO, FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A,
                   DURACION_CONTRATO_A, CANON_ARRENDAMIENTO, DEPOSITO, FECHA_PAGO,
                   GRUPO_OPERATIVO, ESTADO_CONTRATO_A
               ) VALUES (
                   %s, %s, '2025-05-18', '2026-05-17', 12, 1500000, 0, '1', 0, 'ACTIVO'
               ) RETURNING ID_CONTRATO_A""",
            (id_prop, id_arr),
        )
        id_contrato_a = _get_val(cursor.fetchone(), "ID_CONTRATO_A", 0)
        test_auditoria_ctx["id_contrato_a"] = id_contrato_a

        cursor.execute(
            """INSERT INTO CONTRATOS_MANDATOS (
                   ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR, FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M,
                   DURACION_CONTRATO_M, CANON_MANDATO, FECHA_PAGO, GRUPO_OPERATIVO,
                   ESTADO_CONTRATO_M, COMISION_PORCENTAJE_CONTRATO_M
               ) VALUES (
                   %s, %s, %s, '2025-05-18', '2026-05-17', 12, 1500000, '10', 1, 'ACTIVO', 10
               ) RETURNING ID_CONTRATO_M""",
            (id_prop, id_owner, id_ase),
        )
        id_contrato_m = _get_val(cursor.fetchone(), "ID_CONTRATO_M", 0)
        test_auditoria_ctx["id_contrato_m"] = id_contrato_m
        conn.commit()

    # 1. Ejecutar en solo-lectura (commit=False)
    res_dry = auditar_y_remediar_grupos_pago(commit=False, outputs_dir="outputs")
    assert res_dry["codigo_salida"] == 0
    assert res_dry["total_discrepancias"] >= 2

    # Verificar que NO se modificaron los datos en BD
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT GRUPO_OPERATIVO, FECHA_PAGO FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = %s",
            (id_contrato_m,),
        )
        row_m = cursor.fetchone()
        assert _get_val(row_m, "GRUPO_OPERATIVO", 0) == 1
        assert str(_get_val(row_m, "FECHA_PAGO", 1)) == "10"

        cursor.execute(
            "SELECT GRUPO_OPERATIVO, FECHA_PAGO FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = %s",
            (id_contrato_a,),
        )
        row_a = cursor.fetchone()
        assert _get_val(row_a, "GRUPO_OPERATIVO", 0) == 0

    # 2. Ejecutar con commit=True
    res_commit = auditar_y_remediar_grupos_pago(commit=True, outputs_dir="outputs")
    assert res_commit["codigo_salida"] == 0

    # Verificar que los datos fueron corregidos en BD
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT GRUPO_OPERATIVO, FECHA_PAGO FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = %s",
            (id_contrato_m,),
        )
        row_m2 = cursor.fetchone()
        assert _get_val(row_m2, "GRUPO_OPERATIVO", 0) == 3
        assert str(_get_val(row_m2, "FECHA_PAGO", 1)) == "30"

        cursor.execute(
            "SELECT GRUPO_OPERATIVO, FECHA_PAGO FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = %s",
            (id_contrato_a,),
        )
        row_a2 = cursor.fetchone()
        assert _get_val(row_a2, "GRUPO_OPERATIVO", 0) == 3
        assert str(_get_val(row_a2, "FECHA_PAGO", 1)) == "18"


def test_T013_herencia_periodo_mandato_sin_renovacion_propia(test_auditoria_ctx):
    """
    T013 / Spec §FR-001: Mandato sin renovaciones propias cuya propiedad tiene un
    arrendamiento ACTIVO con renovaciones hereda la fecha efectiva de la última renovación del arriendo.
    """
    if auditar_y_remediar_grupos_pago is None:
        pytest.fail(
            "scripts/remediacion/remediar_grupos_pago_v4.py no está implementado"
        )

    db = test_auditoria_ctx["db"]
    id_prop = test_auditoria_ctx["id_propiedad"]
    id_arr = test_auditoria_ctx["id_arrendatario"]
    id_owner = test_auditoria_ctx["id_propietario"]
    id_ase = test_auditoria_ctx["id_asesor"]

    # Mandato creado con fecha de inicio 2024-01-01 (sin renovaciones propias)
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO CONTRATOS_MANDATOS (
                   ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR, FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M,
                   DURACION_CONTRATO_M, CANON_MANDATO, FECHA_PAGO, GRUPO_OPERATIVO,
                   ESTADO_CONTRATO_M, COMISION_PORCENTAJE_CONTRATO_M
               ) VALUES (
                   %s, %s, %s, '2024-01-01', '2026-05-07', 12, 1500000, '10', 1, 'ACTIVO', 10
               ) RETURNING ID_CONTRATO_M""",
            (id_prop, id_owner, id_ase),
        )
        id_contrato_m = _get_val(cursor.fetchone(), "ID_CONTRATO_M", 0)
        test_auditoria_ctx["id_contrato_m"] = id_contrato_m

        # Arrendamiento activo en la misma propiedad
        cursor.execute(
            """INSERT INTO CONTRATOS_ARRENDAMIENTOS (
                   ID_PROPIEDAD, ID_ARRENDATARIO, FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A,
                   DURACION_CONTRATO_A, CANON_ARRENDAMIENTO, DEPOSITO, FECHA_PAGO,
                   GRUPO_OPERATIVO, ESTADO_CONTRATO_A
               ) VALUES (
                   %s, %s, '2024-01-01', '2026-05-07', 12, 1500000, 0, '8', 2, 'ACTIVO'
               ) RETURNING ID_CONTRATO_A""",
            (id_prop, id_arr),
        )
        id_contrato_a = _get_val(cursor.fetchone(), "ID_CONTRATO_A", 0)
        test_auditoria_ctx["id_contrato_a"] = id_contrato_a

        # Renovación en el arrendamiento: fecha_inicio_renovacion = 2025-05-08 (Tramo 8..17 -> G2, día 20)
        cursor.execute(
            """INSERT INTO RENOVACIONES_CONTRATOS (
                   ID_CONTRATO_A, TIPO_CONTRATO, FECHA_INICIO_ORIGINAL, FECHA_FIN_ORIGINAL,
                   FECHA_INICIO_RENOVACION, FECHA_FIN_RENOVACION, CANON_ANTERIOR, CANON_NUEVO,
                   PORCENTAJE_INCREMENTO, MOTIVO_RENOVACION, FECHA_RENOVACION
               ) VALUES (
                   %s, 'Arrendamiento', '2024-01-01', '2025-05-07', '2025-05-08', '2026-05-07',
                   1500000, 1500000, 0, 'Renovacion Test', '2025-05-07'
               ) RETURNING ID_RENOVACION""",
            (id_contrato_a,),
        )
        conn.commit()

    # Ejecutar remediación
    auditar_y_remediar_grupos_pago(commit=True, outputs_dir="outputs")

    # El mandato debe haber heredado el período 2025-05-08 -> Grupo 2, día 20
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT GRUPO_OPERATIVO, FECHA_PAGO FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = %s",
            (id_contrato_m,),
        )
        row_m = cursor.fetchone()
        assert (
            _get_val(row_m, "GRUPO_OPERATIVO", 0) == 2
        ), f"Mandato debía heredar G2, tiene {_get_val(row_m, 'GRUPO_OPERATIVO', 0)}"
        assert (
            str(_get_val(row_m, "FECHA_PAGO", 1)) == "20"
        ), f"Mandato debía tener día 20, tiene {_get_val(row_m, 'FECHA_PAGO', 1)}"


def test_T016_verificacion_cero_huerfanos_test():
    """
    T016 (SC-005, FR-013): Verifica que no queden huérfanos de prueba en la base de datos.
    Contratos, propiedades, liquidaciones, recaudos, renovaciones y personas con prefijo TEST deben ser 0.
    """
    db = _require_db()
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()

        # Propiedades de prueba
        cursor.execute(
            "SELECT COUNT(*) FROM PROPIEDADES WHERE MATRICULA_INMOBILIARIA LIKE 'TEST-%%'"
        )
        props = _get_val(cursor.fetchone(), "count", 0)
        assert props == 0, f"Existen {props} propiedades huérfanas de TEST"

        # Personas de prueba
        cursor.execute(
            "SELECT COUNT(*) FROM PERSONAS WHERE NUMERO_DOCUMENTO LIKE 'DOC-T%%' OR NUMERO_DOCUMENTO LIKE 'TEST-%%'"
        )
        personas = _get_val(cursor.fetchone(), "count", 0)
        assert personas == 0, f"Existen {personas} personas huérfanas de TEST"

        # Contratos de arrendamiento ligados a propiedades TEST
        cursor.execute("""SELECT COUNT(*) FROM CONTRATOS_ARRENDAMIENTOS ca
               JOIN PROPIEDADES p ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
               WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%%'""")
        arriendos = _get_val(cursor.fetchone(), "count", 0)
        assert arriendos == 0, f"Existen {arriendos} arriendos huérfanos de TEST"

        # Contratos de mandato ligados a propiedades TEST
        cursor.execute("""SELECT COUNT(*) FROM CONTRATOS_MANDATOS cm
               JOIN PROPIEDADES p ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
               WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%%'""")
        mandatos = _get_val(cursor.fetchone(), "count", 0)
        assert mandatos == 0, f"Existen {mandatos} mandatos huérfanos de TEST"

        # Renovaciones ligadas a contratos TEST
        cursor.execute("""SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS r
               WHERE r.ID_CONTRATO_A IN (
                   SELECT ca.ID_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS ca
                   JOIN PROPIEDADES p ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
                   WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%%')
               OR r.ID_CONTRATO_M IN (
                   SELECT cm.ID_CONTRATO_M FROM CONTRATOS_MANDATOS cm
                   JOIN PROPIEDADES p ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
                   WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%%')""")
        renovaciones = _get_val(cursor.fetchone(), "count", 0)
        assert (
            renovaciones == 0
        ), f"Existen {renovaciones} renovaciones huérfanas de TEST"

        # Liquidaciones ligadas a mandatos TEST
        cursor.execute("""SELECT COUNT(*) FROM LIQUIDACIONES_PROPIETARIOS lp
               JOIN CONTRATOS_MANDATOS cm ON cm.ID_CONTRATO_M = lp.ID_CONTRATO_M
               JOIN PROPIEDADES p ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
               WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%%'""")
        liquidaciones = _get_val(cursor.fetchone(), "count", 0)
        assert (
            liquidaciones == 0
        ), f"Existen {liquidaciones} liquidaciones huérfanas de TEST"

        # Recaudos ligados a arriendos TEST
        cursor.execute("""SELECT COUNT(*) FROM RECAUDOS rc
               JOIN CONTRATOS_ARRENDAMIENTOS ca ON ca.ID_CONTRATO_A = rc.ID_CONTRATO_A
               JOIN PROPIEDADES p ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
               WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%%'""")
        recaudos = _get_val(cursor.fetchone(), "count", 0)
        assert recaudos == 0, f"Existen {recaudos} recaudos huérfanos de TEST"
