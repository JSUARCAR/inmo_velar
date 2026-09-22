"""
Tests de integración: Persistencia y atomicidad del grupo de pago en renovaciones (T011, T018).
Cubre Spec §FR-004, §FR-005, §FR-006, §FR-007, §FR-008, §SC-001, §SC-003, §SC-005.
"""

import os
import uuid
import pytest

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.aplicacion.servicios.servicio_contrato_arrendamiento import (
    ServicioContratoArrendamiento,
)
from src.aplicacion.servicios.servicio_contrato_mandato import (
    ServicioContratoMandato,
)
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
    RepositorioContratoArrendamientoPostgres,
)
from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
    RepositorioContratoMandatoPostgres,
)
from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
    RepositorioPropiedadPostgres,
)
from src.infraestructura.persistencia.repositorio_renovacion_postgres import (
    RepositorioRenovacionPostgres,
)
from src.infraestructura.persistencia.repositorio_ipc_postgres import (
    RepositorioIPCPostgres,
)
from src.infraestructura.persistencia.repositorio_idempotencia_postgres import (
    RepositorioIdempotenciaPostgres,
)


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
    # Fallback to key or index if possible
    try:
        return row[key]
    except Exception:
        try:
            return row[idx]
        except Exception:
            return None


@pytest.fixture
def test_context():
    """Crea entidades aisladas para pruebas de renovación y garantiza limpieza 100% (SC-005)."""
    db = _require_db()
    suffix = uuid.uuid4().hex[:8]
    matricula = f"TEST-GP-{suffix}"
    doc_arrendatario = f"DOC-A-{suffix}"
    doc_propietario = f"DOC-P-{suffix}"

    id_propiedad = None
    id_persona_a = None
    id_arrendatario = None
    id_persona_p = None
    id_propietario = None

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        # Municipio dummy
        cursor.execute(
            """INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO)
               VALUES (99996, 'MUN TEST GP', 'DEPTO GP', TRUE)
               ON CONFLICT (ID_MUNICIPIO) DO NOTHING"""
        )
        # Propiedad
        cursor.execute(
            """INSERT INTO PROPIEDADES (
                   MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO,
                   ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO,
                   DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
               ) VALUES (
                   %s, 'Direccion Test GP', TRUE, 99996,
                   'Apartamento', 75.0, 3, TRUE, 1200000
               ) RETURNING ID_PROPIEDAD""",
            (matricula,),
        )
        id_propiedad = _get_val(cursor.fetchone(), "ID_PROPIEDAD", 0)

        # Persona y Arrendatario
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Arrendatario Test GP', TRUE) RETURNING ID_PERSONA",
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
            "VALUES (%s, 'Propietario Test GP', TRUE) RETURNING ID_PERSONA",
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
        cursor.execute("SELECT ID_USUARIO FROM USUARIOS LIMIT 1")
        row_u = cursor.fetchone()
        id_usuario = _get_val(row_u, "ID_USUARIO", 0) if row_u else 2
        conn.commit()

    contexto = {
        "db": db,
        "id_propiedad": id_propiedad,
        "id_arrendatario": id_arrendatario,
        "id_propietario": id_propietario,
        "id_asesor": id_asesor,
        "id_usuario": id_usuario,
        "id_contrato_m": None,
        "id_contrato_a": None,
    }

    yield contexto

    # Limpieza total (SC-005, FR-013)
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


def test_T011_persistencia_grupo_tras_renovar_arriendo_y_sync_mandato(test_context):
    """
    T011 (US1): Verifica en base de datos PostgreSQL que al renovar un contrato de arrendamiento:
    1. El arriendo recalcula y persiste grupo_operativo y fecha_pago en BD (no 0, no perdido).
    2. El mandato activo asociado adopta el nuevo período y persiste su grupo_operativo y fecha_pago en BD.
    """
    db = test_context["db"]
    id_prop = test_context["id_propiedad"]
    id_arr = test_context["id_arrendatario"]
    id_prop_owner = test_context["id_propietario"]
    id_ase = test_context["id_asesor"]

    # Insertamos un mandato activo en DB:
    # fecha_inicio: 2025-05-01, fecha_fin: 2026-05-07, grupo: 1, pago: 10
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO CONTRATOS_MANDATOS (
                   ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR, FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M,
                   DURACION_CONTRATO_M, CANON_MANDATO, FECHA_PAGO, GRUPO_OPERATIVO,
                   ESTADO_CONTRATO_M, COMISION_PORCENTAJE_CONTRATO_M
               ) VALUES (
                   %s, %s, %s, '2025-05-01', '2026-05-07', 12, 1200000, '10', 1, 'ACTIVO', 10
               ) RETURNING ID_CONTRATO_M""",
            (id_prop, id_prop_owner, id_ase),
        )
        id_contrato_m = _get_val(cursor.fetchone(), "ID_CONTRATO_M", 0)
        test_context["id_contrato_m"] = id_contrato_m

        # Insertamos un arrendamiento activo en DB:
        # fecha_inicio: 2025-05-08, fecha_fin: 2026-05-07, grupo: 1 (viejo/incorrecto), fecha_pago: '1'
        # Al renovar: fecha_fin_original es 2026-05-07 -> fecha_inicio_renovacion es 2026-05-08!
        # Tramo 8..17: Grupo 2!
        # Arrendamiento fecha_pago debe ser '8'
        # Mandato sincronizado debe ser Grupo 2, fecha_pago '20'!
        cursor.execute(
            """INSERT INTO CONTRATOS_ARRENDAMIENTOS (
                   ID_PROPIEDAD, ID_ARRENDATARIO, FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A,
                   DURACION_CONTRATO_A, CANON_ARRENDAMIENTO, DEPOSITO, FECHA_PAGO,
                   GRUPO_OPERATIVO, ESTADO_CONTRATO_A
               ) VALUES (
                   %s, %s, '2025-05-08', '2026-05-07', 12, 1200000, 0, '1', 1, 'ACTIVO'
               ) RETURNING ID_CONTRATO_A""",
            (id_prop, id_arr),
        )
        id_contrato_a = _get_val(cursor.fetchone(), "ID_CONTRATO_A", 0)
        test_context["id_contrato_a"] = id_contrato_a
        conn.commit()

    servicio = ServicioContratos(db)
    renovado = servicio.renovar_arrendamiento(id_contrato_a, "test_t011_user")

    assert renovado is not None

    # Verificar directamente en PostgreSQL
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        # Verificar Arrendamiento
        cursor.execute(
            "SELECT GRUPO_OPERATIVO, FECHA_PAGO, FECHA_FIN_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = %s",
            (id_contrato_a,),
        )
        row_a = cursor.fetchone()
        grupo_a = _get_val(row_a, "GRUPO_OPERATIVO", 0)
        pago_a = _get_val(row_a, "FECHA_PAGO", 1)
        fin_a = _get_val(row_a, "FECHA_FIN_CONTRATO_A", 2)

        assert (
            grupo_a == 2
        ), f"Arriendo en BD debe tener GRUPO_OPERATIVO=2, obtuvo {grupo_a}"
        assert (
            str(pago_a) == "8"
        ), f"Arriendo en BD debe tener FECHA_PAGO='8', obtuvo {pago_a}"

        # Verificar Mandato sincronizado
        cursor.execute(
            "SELECT GRUPO_OPERATIVO, FECHA_PAGO, FECHA_FIN_CONTRATO_M FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = %s",
            (id_contrato_m,),
        )
        row_m = cursor.fetchone()
        grupo_m = _get_val(row_m, "GRUPO_OPERATIVO", 0)
        pago_m = _get_val(row_m, "FECHA_PAGO", 1)
        fin_m = _get_val(row_m, "FECHA_FIN_CONTRATO_M", 2)

        assert (
            grupo_m == 2
        ), f"Mandato sincronizado en BD debe tener GRUPO_OPERATIVO=2, obtuvo {grupo_m}"
        assert (
            str(pago_m) == "20"
        ), f"Mandato sincronizado en BD debe tener FECHA_PAGO='20', obtuvo {pago_m}"
        assert (
            fin_m == fin_a
        ), f"Mandato fin ({fin_m}) debe coincidir con arriendo ({fin_a})"


def test_T011_persistencia_grupo_tras_renovar_mandato_directo(test_context):
    """T011: Verifica en PostgreSQL que renovar_mandato recalcula y persiste grupo y fecha_pago."""
    db = test_context["db"]
    id_prop = test_context["id_propiedad"]
    id_prop_owner = test_context["id_propietario"]
    id_ase = test_context["id_asesor"]

    # Mandato activo con fin 2026-05-17 -> renovación inicia 2026-05-18 (Tramo 18..27 -> G3, día 30)
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO CONTRATOS_MANDATOS (
                   ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR, FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M,
                   DURACION_CONTRATO_M, CANON_MANDATO, FECHA_PAGO, GRUPO_OPERATIVO,
                   ESTADO_CONTRATO_M, COMISION_PORCENTAJE_CONTRATO_M
               ) VALUES (
                   %s, %s, %s, '2025-05-18', '2026-05-17', 12, 1500000, '10', 1, 'ACTIVO', 10
               ) RETURNING ID_CONTRATO_M""",
            (id_prop, id_prop_owner, id_ase),
        )
        id_contrato_m = _get_val(cursor.fetchone(), "ID_CONTRATO_M", 0)
        test_context["id_contrato_m"] = id_contrato_m
        conn.commit()

    servicio = ServicioContratoMandato(
        repo_mandato=RepositorioContratoMandatoPostgres(db),
        repo_propiedad=RepositorioPropiedadPostgres(db),
        repo_renovacion=RepositorioRenovacionPostgres(db),
    )

    renovado = servicio.renovar_mandato(id_contrato_m, "test_t011_mandato")
    assert renovado is not None

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT GRUPO_OPERATIVO, FECHA_PAGO FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = %s",
            (id_contrato_m,),
        )
        row = cursor.fetchone()
        grupo = _get_val(row, "GRUPO_OPERATIVO", 0)
        pago = _get_val(row, "FECHA_PAGO", 1)
        assert grupo == 3, f"Mandato en BD debe tener GRUPO_OPERATIVO=3, obtuvo {grupo}"
        assert (
            str(pago) == "30"
        ), f"Mandato en BD debe tener FECHA_PAGO='30', obtuvo {pago}"


def test_T018_fallo_inducido_rollback_total_y_reintento(test_context):
    """
    T018 (US3): Induce fallo a mitad de renovación de arrendamiento, verifica ausencia
    de cambios parciales (rollback total en BD) y reintento exitoso.
    """
    db = test_context["db"]
    id_prop = test_context["id_propiedad"]
    id_arr = test_context["id_arrendatario"]
    id_prop_owner = test_context["id_propietario"]
    id_ase = test_context["id_asesor"]

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO CONTRATOS_MANDATOS (
                   ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR, FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M,
                   DURACION_CONTRATO_M, CANON_MANDATO, FECHA_PAGO, GRUPO_OPERATIVO,
                   ESTADO_CONTRATO_M, COMISION_PORCENTAJE_CONTRATO_M
               ) VALUES (
                   %s, %s, %s, '2025-01-01', '2025-12-31', 12, 1000000, '10', 1, 'ACTIVO', 10
               ) RETURNING ID_CONTRATO_M""",
            (id_prop, id_prop_owner, id_ase),
        )
        id_contrato_m = _get_val(cursor.fetchone(), "ID_CONTRATO_M", 0)
        test_context["id_contrato_m"] = id_contrato_m

        cursor.execute(
            """INSERT INTO CONTRATOS_ARRENDAMIENTOS (
                   ID_PROPIEDAD, ID_ARRENDATARIO, FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A,
                   DURACION_CONTRATO_A, CANON_ARRENDAMIENTO, DEPOSITO, FECHA_PAGO,
                   GRUPO_OPERATIVO, ESTADO_CONTRATO_A
               ) VALUES (
                   %s, %s, '2025-01-01', '2025-12-31', 12, 1000000, 0, '1', 1, 'ACTIVO'
               ) RETURNING ID_CONTRATO_A""",
            (id_prop, id_arr),
        )
        id_contrato_a = _get_val(cursor.fetchone(), "ID_CONTRATO_A", 0)
        test_context["id_contrato_a"] = id_contrato_a
        conn.commit()

    repo_arr = RepositorioContratoArrendamientoPostgres(db)
    repo_prop = RepositorioPropiedadPostgres(db)
    repo_ren = RepositorioRenovacionPostgres(db)
    repo_ipc = RepositorioIPCPostgres(db)
    repo_man = RepositorioContratoMandatoPostgres(db)
    repo_idem = RepositorioIdempotenciaPostgres()

    # Creamos un repo_renovacion fallido que explota al crear
    class RepoRenovacionFallido(RepositorioRenovacionPostgres):
        def crear(self, entidad, usuario):
            raise RuntimeError("Fallo inducido para test de rollback T018")

    servicio_fallido = ServicioContratoArrendamiento(
        repo_arriendo=repo_arr,
        repo_propiedad=repo_prop,
        repo_renovacion=RepoRenovacionFallido(db),
        repo_ipc=repo_ipc,
        repo_mandato=repo_man,
        repo_idempotencia=repo_idem,
    )
    servicio_fallido.usuario_id = test_context["id_usuario"]

    with pytest.raises(RuntimeError, match="Fallo inducido"):
        servicio_fallido.renovar_arrendamiento(
            id_contrato_a, "test_admin", "2026-12-31"
        )

    # Verificar que NO se modificó nada en BD (rollback total)
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT FECHA_FIN_CONTRATO_A, CANON_ARRENDAMIENTO, GRUPO_OPERATIVO FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = %s",
            (id_contrato_a,),
        )
        row_a = cursor.fetchone()
        fin_a = _get_val(row_a, "FECHA_FIN_CONTRATO_A", 0)
        canon_a = _get_val(row_a, "CANON_ARRENDAMIENTO", 1)
        grupo_a = _get_val(row_a, "GRUPO_OPERATIVO", 2)

        assert (
            fin_a == "2025-12-31"
        ), f"Fecha fin debió revertirse a 2025-12-31, es {fin_a}"
        assert canon_a == 1000000, f"Canon debió revertirse a 1000000, es {canon_a}"
        assert grupo_a == 1, f"Grupo debió revertirse a 1, es {grupo_a}"

        cursor.execute(
            "SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s",
            (id_contrato_a,),
        )
        cnt = _get_val(cursor.fetchone(), "count", 0)
        assert (
            cnt == 0
        ), f"No debe existir ninguna fila en RENOVACIONES_CONTRATOS, obtuvo {cnt}"

    # Reintento con servicio sano: debe completar exitosamente
    servicio_sano = ServicioContratoArrendamiento(
        repo_arriendo=repo_arr,
        repo_propiedad=repo_prop,
        repo_renovacion=repo_ren,
        repo_ipc=repo_ipc,
        repo_mandato=repo_man,
        repo_idempotencia=repo_idem,
    )
    servicio_sano.usuario_id = test_context["id_usuario"]

    resultado_reintento = servicio_sano.renovar_arrendamiento(
        id_contrato_a, "test_admin", "2026-12-31"
    )
    assert resultado_reintento is not None

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s",
            (id_contrato_a,),
        )
        cnt_final = _get_val(cursor.fetchone(), "count", 0)
        assert (
            cnt_final == 1
        ), f"Debe existir exactamente 1 renovación tras el reintento exitoso, obtuvo {cnt_final}"
