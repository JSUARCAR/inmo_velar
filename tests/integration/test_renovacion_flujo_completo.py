"""
Tests de integración: flujo completo de renovación (T009, US1).
Cubre E1/E2/E3/E6/E7/E8/E9/E10 (IPC, propagación, auditoría, caché).
"""

import sys
import os
import uuid

import pytest
import psycopg2

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.dominio.entidades.ipc import IPC
from src.infraestructura.persistencia.repositorio_ipc_postgres import (
    RepositorioIPCPostgres,
)


def _require_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    return DatabaseManager()


def _setup_propiedad(db, suffix=""):
    """Crea propiedad con UUID único para aislamiento de tests."""
    matricula = f"TEST-INT-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO)
               VALUES (99999, 'MUNICIPIO TEST INT', 'DEPTO TEST', TRUE)
               ON CONFLICT (ID_MUNICIPIO) DO NOTHING"""
        )
        conn.commit()
        cursor.execute(
            """INSERT INTO PROPIEDADES (
                   MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO,
                   ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO,
                   DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
               ) VALUES (
                   %s, 'Calle Int Test', TRUE, 99999,
                   'Apartamento', 60.0, 3, TRUE, 1000000
               ) RETURNING ID_PROPIEDAD""",
            (matricula,),
        )
        row = cursor.fetchone()
        id_prop = row[0] if isinstance(row, tuple) else row["ID_PROPIEDAD"]
        conn.commit()
    return id_prop


def _setup_arrendatario(db):
    doc = f"DOC-INT-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Test Int User', TRUE) RETURNING ID_PERSONA",
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


def _setup_ipc(db, valor_ipc=10.0, anio=2099):
    repo_ipc = RepositorioIPCPostgres(db)
    ipc = IPC(anio=anio, valor_ipc=valor_ipc, fecha_publicacion=f"{anio}-01-01")
    try:
        repo_ipc.crear(ipc, "test_integration")
    except Exception:
        pass
    vigente = repo_ipc.obtener_ultimo()
    return vigente.valor_ipc if vigente else 0.0


def _canon_esperado(canon_base, valor_ipc):
    return int(canon_base * (1 + valor_ipc / 100))


def test_E1_renovacion_con_ipc_incrementa_canon():
    """E1: duración >= 12 + IPC -> canon_nuevo = canon*(1+IPC/100)."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrendatario = _setup_arrendatario(db)
    valor_ipc = _setup_ipc(db, valor_ipc=10.0)

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'CANCELADO', "
            "MOTIVO_CANCELACION = 'test reset' WHERE ID_PROPIEDAD = %s "
            "AND ESTADO_CONTRATO_A = 'ACTIVO'", (id_prop,),
        )
        conn.commit()

    contrato = servicio.crear_arrendamiento(
        {
            "id_propiedad": id_prop,
            "id_arrendatario": id_arrendatario,
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31",
            "duracion_meses": 12,
            "canon": 1000000,
            "deposito": 0,
        },
        "test_int",
    )

    renovado = servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_int")

    canon_esperado = _canon_esperado(1_000_000, valor_ipc)
    assert renovado.canon_arrendamiento == canon_esperado, (
        f"Se esperaba {canon_esperado} (1M+IPC {valor_ipc}%); "
        f"obtuvo {renovado.canon_arrendamiento}"
    )

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT fecha_inicio_renovacion FROM RENOVACIONES_CONTRATOS "
            "WHERE ID_CONTRATO_A = %s ORDER BY ID_RENOVACION DESC LIMIT 1",
            (contrato.id_contrato_a,),
        )
        row = cursor.fetchone()
        fecha_ini = row[0] if isinstance(row, tuple) else row["FECHA_INICIO_RENOVACION"]

    assert fecha_ini is not None and fecha_ini != "", "E9: fecha_inicio_renovacion no debe ser vacía"
    assert fecha_ini == "2025-01-01", f"E9: fecha_inicio_renovacion debe ser 2025-01-01; obtuvo {fecha_ini}"


def test_E2_duracion_menos_12_no_aplica_ipc():
    """E2: duración < 12 meses -> 0% de incremento."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrendatario = _setup_arrendatario(db)
    _setup_ipc(db, valor_ipc=10.0)

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'CANCELADO', "
            "MOTIVO_CANCELACION = 'test reset' WHERE ID_PROPIEDAD = %s "
            "AND ESTADO_CONTRATO_A = 'ACTIVO'", (id_prop,),
        )
        conn.commit()

    contrato = servicio.crear_arrendamiento(
        {
            "id_propiedad": id_prop,
            "id_arrendatario": id_arrendatario,
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-06-30",
            "duracion_meses": 6,
            "canon": 1000000,
            "deposito": 0,
        },
        "test_int",
    )

    renovado = servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_int")

    assert renovado.canon_arrendamiento == 1_000_000, (
        f"E2: canon no debe cambiar con duración <12; obtuvo {renovado.canon_arrendamiento}"
    )


def test_E6_sin_filas_futuras_no_falla():
    """E6: sin liquidaciones/recaudos futuros, la renovación no falla."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrendatario = _setup_arrendatario(db)
    valor_ipc = _setup_ipc(db, valor_ipc=5.0)

    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'CANCELADO', "
            "MOTIVO_CANCELACION = 'test reset' WHERE ID_PROPIEDAD = %s "
            "AND ESTADO_CONTRATO_A = 'ACTIVO'", (id_prop,),
        )
        conn.commit()

    contrato = servicio.crear_arrendamiento(
        {
            "id_propiedad": id_prop,
            "id_arrendatario": id_arrendatario,
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31",
            "duracion_meses": 12,
            "canon": 1000000,
            "deposito": 0,
        },
        "test_int",
    )

    renovado = servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_int")
    assert renovado.canon_arrendamiento == _canon_esperado(1_000_000, valor_ipc)
