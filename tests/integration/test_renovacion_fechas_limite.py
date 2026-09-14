"""
T021 [US3]: Flujo completo de fechas límite — E5 de quickstart.md.

Verifica vía renovación real que `fecha_inicio_renovacion` = fecha_fin + 1 día
y `fecha_fin_renovacion` = +N meses sobre la última fecha del mes destino,
incluidos bordes 31-Dic y 28-Feb en año bisiesto. Jamás fechas vacías "".
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
    matricula = f"TEST-E5-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) "
            "VALUES (99999, 'MUN E5', 'DEPTO E5', TRUE) "
            "ON CONFLICT (ID_MUNICIPIO) DO NOTHING"
        )
        conn.commit()
        cursor.execute(
            """INSERT INTO PROPIEDADES (
                MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO,
                ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO,
                DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
            ) VALUES (
                %s, 'Calle E5 Test', TRUE, 99999,
                'Apartamento', 60.0, 3, TRUE, 1000000
            ) RETURNING ID_PROPIEDAD""",
            (matricula,),
        )
        row = cursor.fetchone()
        id_prop = row[0] if isinstance(row, tuple) else row["ID_PROPIEDAD"]
        conn.commit()
    return id_prop


def _setup_arrendatario(db):
    doc = f"DOC-E5-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Test E5 User', TRUE) RETURNING ID_PERSONA",
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


def _setup_ipc(db, valor_ipc=10.0):
    repo_ipc = RepositorioIPCPostgres(db)
    ipc = IPC(anio=2098, valor_ipc=valor_ipc, fecha_publicacion="2098-01-01")
    try:
        repo_ipc.crear(ipc, "test_e5")
    except Exception:
        pass
    vigente = repo_ipc.obtener_ultimo()
    return vigente.valor_ipc if vigente else 0.0


def _fechas_renovacion(db, id_contrato_a):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT FECHA_INICIO_RENOVACION, FECHA_FIN_RENOVACION "
            "FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s "
            "ORDER BY ID_RENOVACION LIMIT 1",
            (id_contrato_a,),
        )
        row = cursor.fetchone()
        if isinstance(row, tuple):
            return (row[0], row[1])
        return (row["FECHA_INICIO_RENOVACION"], row["FECHA_FIN_RENOVACION"])


def _crear_contrato(servicio, db, id_prop, id_arrend, fecha_inicio, fecha_fin, meses, canon=1000000):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'CANCELADO', "
            "MOTIVO_CANCELACION = 'test e5 reset' WHERE ID_PROPIEDAD = %s "
            "AND ESTADO_CONTRATO_A = 'ACTIVO'",
            (id_prop,),
        )
        conn.commit()
    return servicio.crear_arrendamiento(
        {
            "id_propiedad": id_prop,
            "id_arrendatario": id_arrend,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "duracion_meses": meses,
            "canon": canon,
            "deposito": 0,
        },
        "test_e5",
    )


def test_E5_31_dic_a_01_ene():
    """E5.1: fecha_fin 2026-12-31 → fecha_inicio_renovacion 2027-01-01 (jamás "")."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrend = _setup_arrendatario(db)
    _setup_ipc(db, valor_ipc=5.0)

    contrato = _crear_contrato(servicio, db, id_prop, id_arrend, "2026-01-01", "2026-12-31", 12)
    servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_e5")

    inicio, fin = _fechas_renovacion(db, contrato.id_contrato_a)
    assert inicio is not None and fin is not None, "Fechas de renovación jamás vacías"
    assert inicio == "2027-01-01", f"fecha_inicio_renovacion esperada 2027-01-01, obtuvo {inicio}"
    assert not str(inicio).startswith('""'), "Fecha inicio renovación no debe contener comillas vacías"


def test_E5_28_feb_bisiesto_a_29_feb():
    """E5.2: fecha_fin 2028-02-28 (año bisiesto) → fecha_inicio_renovacion 2028-02-29
    y fecha_fin_renovacion = +12 meses sobre la última fecha del mes destino."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrend = _setup_arrendatario(db)
    _setup_ipc(db, valor_ipc=5.0)

    contrato = _crear_contrato(servicio, db, id_prop, id_arrend, "2027-02-28", "2028-02-28", 12)
    servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_e5")

    inicio, fin = _fechas_renovacion(db, contrato.id_contrato_a)
    assert inicio is not None and fin is not None, "Fechas de renovación jamás vacías"
    assert inicio == "2028-02-29", f"fecha_inicio_renovacion esperada 2028-02-29, obtuvo {inicio}"
    assert fin == "2029-02-28", f"fecha_fin_renovacion esperada 2029-02-28, obtuvo {fin}"


def test_E5_31_ene_fin_de_mes():
    """E5.3: fecha_fin 31-Ene → fecha_inicio_renovacion 01-Feb y
    fecha_fin_renovacion 31-Ene del periodo siguiente (fin de mes)."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrend = _setup_arrendatario(db)
    _setup_ipc(db, valor_ipc=5.0)

    contrato = _crear_contrato(servicio, db, id_prop, id_arrend, "2026-02-01", "2027-01-31", 12)
    servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_e5")

    inicio, fin = _fechas_renovacion(db, contrato.id_contrato_a)
    assert inicio == "2027-02-01", f"fecha_inicio_renovacion esperada 2027-02-01, obtuvo {inicio}"
    assert fin == "2028-01-31", f"fecha_fin_renovacion esperada 2028-01-31, obtuvo {fin}"