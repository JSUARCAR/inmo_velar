"""
T019 [US2]: Renovación consecutiva — E4 de quickstart.md.

Verifica que dos renovaciones consecutivas producen dos filas válidas
en RENOVACIONES_CONTRATOS y que la segunda parte del canon de la primera
(sin duplicados por idempotencia en un mismo intento).
"""

import os
import uuid

import pytest

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.dominio.entidades.ipc import IPC
from src.infraestructura.persistencia.repositorio_ipc_postgres import (
    RepositorioIPCPostgres,
)


def _require_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    return DatabaseManager()


def _setup_propiedad(db):
    matricula = f"TEST-E4-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) "
            "VALUES (99998, 'MUN E4', 'DEPTO E4', TRUE) "
            "ON CONFLICT (ID_MUNICIPIO) DO NOTHING"
        )
        conn.commit()
        cursor.execute(
            """INSERT INTO PROPIEDADES (
                MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO,
                ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO,
                DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
            ) VALUES (
                %s, 'Calle E4 Test', TRUE, 99998,
                'Apartamento', 60.0, 3, TRUE, 1000000
            ) RETURNING ID_PROPIEDAD""",
            (matricula,),
        )
        row = cursor.fetchone()
        id_prop = row[0] if isinstance(row, tuple) else row["ID_PROPIEDAD"]
        conn.commit()
    return id_prop


def _setup_arrendatario(db):
    doc = f"DOC-E4-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Test E4 User', TRUE) RETURNING ID_PERSONA",
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
    return id_arrendatario, id_persona


def _limpiar(db, ids):
    """Limpieza total (SC-005): deja la BD sin rastro del test."""
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        c_a = ids.get("id_contrato_a")
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
        if ids.get("anio_ipc"):
            cursor.execute(
                "DELETE FROM IPC WHERE ANIO = %s AND CREATED_BY = 'test_e4'",
                (ids["anio_ipc"],),
            )
        if ids.get("id_prop"):
            cursor.execute(
                "DELETE FROM PROPIEDADES WHERE ID_PROPIEDAD = %s", (ids["id_prop"],)
            )
        if ids.get("id_arrend"):
            cursor.execute(
                "DELETE FROM ARRENDATARIOS WHERE ID_ARRENDATARIO = %s",
                (ids["id_arrend"],),
            )
        if ids.get("id_persona"):
            cursor.execute(
                "DELETE FROM PERSONAS WHERE ID_PERSONA = %s", (ids["id_persona"],)
            )
        conn.commit()


def _setup_ipc(db, valor_ipc=10.0):
    repo_ipc = RepositorioIPCPostgres(db)
    ipc = IPC(anio=2099, valor_ipc=valor_ipc, fecha_publicacion="2099-01-01")
    try:
        repo_ipc.crear(ipc, "test_e4")
    except Exception:
        pass
    vigente = repo_ipc.obtener_ultimo()
    return vigente.valor_ipc if vigente else 0.0


def _canon_esperado(canon_base, valor_ipc):
    return int(canon_base * (1 + valor_ipc / 100))


def _count_renovaciones(db, id_contrato_a):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s",
            (id_contrato_a,),
        )
        row = cursor.fetchone()
        return row[0] if isinstance(row, tuple) else next(iter(row.values()))


def test_E4_dos_renovaciones_consecutivas_dos_filas(request):
    """E4: dos renovaciones consecutivas producen 2 filas válidas
    y la segunda parte del canon de la primera."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrend, id_persona = _setup_arrendatario(db)
    ids = {"id_prop": id_prop, "id_arrend": id_arrend, "id_persona": id_persona, "anio_ipc": 2099}
    request.addfinalizer(lambda: _limpiar(db, ids))
    valor_ipc = _setup_ipc(db, valor_ipc=5.0)

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'CANCELADO', "
            "MOTIVO_CANCELACION = 'test e4 reset' WHERE ID_PROPIEDAD = %s "
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
        "test_e4",
    )
    ids["id_contrato_a"] = contrato.id_contrato_a

    r1 = servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_e4", "2025-12-31")
    filas_1 = _count_renovaciones(db, contrato.id_contrato_a)
    assert filas_1 == 1, f"Tras 1ra renovación: 1 fila esperada, {filas_1} obtenida"
    assert r1.canon_arrendamiento == _canon_esperado(1_000_000, valor_ipc)

    r2 = servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_e4", "2026-12-31")
    filas_2 = _count_renovaciones(db, contrato.id_contrato_a)
    assert filas_2 == 2, f"Tras 2da renovación: 2 filas esperadas, {filas_2} obtenidas"

    canon_r1 = r1.canon_arrendamiento
    assert r2.canon_arrendamiento == _canon_esperado(canon_r1, valor_ipc), (
        f"La segunda renovación debe partir del canon de la primera ({canon_r1}); "
        f"obtuvo {r2.canon_arrendamiento}"
    )
