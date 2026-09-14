"""
T022 [Transversal]: Atomicidad de la renovación — criterio SC-001.

Induce un fallo a mitad de transacción (tras actualizar el contrato, antes
de la propagación), verifica cero estado parcial en BD (sin filas de
renovación, sin auditoría, sin propagación) y reintenta la misma
idempotency_key: se completa exitosamente sin filas duplicadas.
"""

import os
import uuid

import pytest

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.aplicacion.servicios.servicio_contrato_arrendamiento import (
    ServicioContratoArrendamiento,
)
from src.dominio.entidades.ipc import IPC
from src.infraestructura.persistencia.repositorio_ipc_postgres import (
    RepositorioIPCPostgres,
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
from src.infraestructura.persistencia.repositorio_idempotencia_postgres import (
    RepositorioIdempotenciaPostgres,
)


def _require_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    return DatabaseManager()


def _setup_propiedad(db):
    matricula = f"TEST-T22-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) "
            "VALUES (99997, 'MUN T22', 'DEPTO T22', TRUE) "
            "ON CONFLICT (ID_MUNICIPIO) DO NOTHING"
        )
        conn.commit()
        cursor.execute(
            """INSERT INTO PROPIEDADES (
                MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO,
                ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO,
                DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
            ) VALUES (
                %s, 'Calle T22 Test', TRUE, 99997,
                'Apartamento', 60.0, 3, TRUE, 1000000
            ) RETURNING ID_PROPIEDAD""",
            (matricula,),
        )
        row = cursor.fetchone()
        id_prop = row[0] if isinstance(row, tuple) else row["ID_PROPIEDAD"]
        conn.commit()
    return id_prop


def _setup_arrendatario(db):
    doc = f"DOC-T22-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Test T22 User', TRUE) RETURNING ID_PERSONA",
            (doc,),
        )
        row = cursor.fetchone()
        id_persona = row[0] if isinstance(row, tuple) else row["ID_PERSONA"]
        cursor.execute(
            "INSERT INTO ARRENDATARIOS (ID_PERSONA, ESTADO_ARRENDATARIO) "
            "VALUES (%s, TRUE) RETURNING ID_ARRENDATARIO",
            (id_persona,),
        )
        row2 = cursor.fetchone()
        id_arrendatario = row2[0] if isinstance(row2, tuple) else row2["ID_ARRENDATARIO"]
        conn.commit()
    return id_arrendatario


def _setup_ipc(db, valor_ipc=5.0):
    repo_ipc = RepositorioIPCPostgres(db)
    ipc = IPC(anio=2097, valor_ipc=valor_ipc, fecha_publicacion="2097-01-01")
    try:
        repo_ipc.crear(ipc, "test_t22")
    except Exception:
        pass
    vigente = repo_ipc.obtener_ultimo()
    return vigente.valor_ipc if vigente else 0.0


class RepoPropiedadFallaEnActualizar:
    """Delega al repo real pero lanza al actualizar (fallo inducido a mitad de transacción)."""

    def __init__(self, real):
        self.real = real

    def obtener_por_id(self, *args, **kwargs):
        return self.real.obtener_por_id(*args, **kwargs)

    def actualizar(self, *args, **kwargs):
        raise RuntimeError("Fallo inducido T022: simulación de error en propagación")


def _query(db, sql, params):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if isinstance(row, tuple) else next(iter(row.values()))


def _estado_contrato(db, id_contrato):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT FECHA_FIN_CONTRATO_A, CANON_ARRENDAMIENTO, ESTADO_CONTRATO_A "
            "FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = %s",
            (id_contrato,),
        )
        row = cursor.fetchone()
    if isinstance(row, tuple):
        return row
    return (row["FECHA_FIN_CONTRATO_A"], row["CANON_ARRENDAMIENTO"], row["ESTADO_CONTRATO_A"])


def test_T022_fallo_a_mitad_de_transaccion_zero_estado_parcial():
    """Fallo tras actualizar el contrato → rollback total: sin renovaciones,
    sin auditoría de propagación, contrato intacto."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrend = _setup_arrendatario(db)
    _setup_ipc(db, valor_ipc=5.0)

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'CANCELADO', "
            "MOTIVO_CANCELACION = 'test t22 reset' WHERE ID_PROPIEDAD = %s "
            "AND ESTADO_CONTRATO_A = 'ACTIVO'",
            (id_prop,),
        )
        conn.commit()

    contrato = servicio.crear_arrendamiento(
        {
            "id_propiedad": id_prop,
            "id_arrendatario": id_arrend,
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31",
            "duracion_meses": 12,
            "canon": 1000000,
            "deposito": 0,
        },
        "test_t22",
    )

    # Estado previo
    fin_previo, canon_previo, estado_previo = _estado_contrato(db, contrato.id_contrato_a)
    assert fin_previo == "2024-12-31"

    # Servicio con repo idempotencia real + repo_propiedad que falla en actualizar
    repo_propiedad_fallido = RepoPropiedadFallaEnActualizar(
        RepositorioPropiedadPostgres(db)
    )
    servicio_con_fallo = ServicioContratoArrendamiento(
        RepositorioContratoArrendamientoPostgres(db),
        repo_propiedad_fallido,
        RepositorioRenovacionPostgres(db),
        RepositorioIPCPostgres(db),
        RepositorioContratoMandatoPostgres(db),
        RepositorioIdempotenciaPostgres(),
    )
    servicio_con_fallo.usuario_id = 8  # usuario existente (crisjam)

    with pytest.raises(RuntimeError, match="(?i)fallo inducido T022"):
        servicio_con_fallo.renovar_arrendamiento(
            contrato.id_contrato_a, "test_t22", "2025-12-31"
        )

    # ZERO estado parcial en BD
    n_renovaciones = _query(
        db,
        "SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s",
        (contrato.id_contrato_a,),
    )
    assert n_renovaciones == 0, f"Esperado 0 renovaciones tras rollback, obtuvo {n_renovaciones}"

    n_auditoria = _query(
        db,
        "SELECT COUNT(*) FROM AUDITORIA_PROPAGACION_CANON WHERE CONTRATO_ID = %s",
        (contrato.id_contrato_a,),
    )
    assert n_auditoria == 0, f"Esperado 0 auditorías de propagación, obtuvo {n_auditoria}"

    fin_tras, canon_tras, estado_tras = _estado_contrato(db, contrato.id_contrato_a)
    assert fin_tras == fin_previo, f"Contrato no debe cambiar su fecha: {fin_tras} vs {fin_previo}"
    assert canon_tras == canon_previo, f"Contrato no debe cambiar su canon: {canon_tras} vs {canon_previo}"
    assert estado_tras == estado_previo, f"Contrato no debe cambiar su estado: {estado_tras} vs {estado_previo}"


def test_T022_reintento_misma_idempotency_key_completa_sin_duplicados():
    """Reintento con la misma idempotency_key completa exitosamente y
    produce exactamente 1 fila de RENOVACIONES_CONTRATOS (sin duplicados)."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrend = _setup_arrendatario(db)
    _setup_ipc(db, valor_ipc=5.0)

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'CANCELADO', "
            "MOTIVO_CANCELACION = 'test t22 reset 2' WHERE ID_PROPIEDAD = %s "
            "AND ESTADO_CONTRATO_A = 'ACTIVO'",
            (id_prop,),
        )
        conn.commit()

    contrato = servicio.crear_arrendamiento(
        {
            "id_propiedad": id_prop,
            "id_arrendatario": id_arrend,
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31",
            "duracion_meses": 12,
            "canon": 1000000,
            "deposito": 0,
        },
        "test_t22b",
    )

    repo_propiedad_real = RepositorioPropiedadPostgres(db)
    repo_propiedad_fallido = RepoPropiedadFallaEnActualizar(repo_propiedad_real)
    repo_idem = RepositorioIdempotenciaPostgres()

    servicio_con_fallo = ServicioContratoArrendamiento(
        RepositorioContratoArrendamientoPostgres(db),
        repo_propiedad_fallido,
        RepositorioRenovacionPostgres(db),
        RepositorioIPCPostgres(db),
        RepositorioContratoMandatoPostgres(db),
        repo_idem,
    )
    servicio_con_fallo.usuario_id = 8

    # Primer intento: falla a mitad de transacción
    with pytest.raises(RuntimeError, match="(?i)fallo inducido T022"):
        servicio_con_fallo.renovar_arrendamiento(
            contrato.id_contrato_a, "test_t22b", "2025-12-31"
        )

    n_renovaciones = _query(
        db,
        "SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s",
        (contrato.id_contrato_a,),
    )
    assert n_renovaciones == 0, f"Esperado 0 tras primer fallo, obtuvo {n_renovaciones}"

    # Reintento con repo sano: misma operación → misma idempotency_key
    servicio_reintento = ServicioContratoArrendamiento(
        RepositorioContratoArrendamientoPostgres(db),
        repo_propiedad_real,
        RepositorioRenovacionPostgres(db),
        RepositorioIPCPostgres(db),
        RepositorioContratoMandatoPostgres(db),
        repo_idem,
    )
    servicio_reintento.usuario_id = 8

    resultado = servicio_reintento.renovar_arrendamiento(
        contrato.id_contrato_a, "test_t22b", "2025-12-31"
    )
    assert resultado is not None

    n_final = _query(
        db,
        "SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s",
        (contrato.id_contrato_a,),
    )
    assert n_final == 1, f"Esperado exactamente 1 fila tras reintento, obtuvo {n_final}"

    fin_final, canon_final, _ = _estado_contrato(db, contrato.id_contrato_a)
    assert fin_final == "2025-12-31", f"Fecha fin final 2025-12-31, obtuvo {fin_final}"
    assert canon_final == 1050000, f"Canon final con IPC 5% (1.000.000) = 1.050.000, obtuvo {canon_final}"