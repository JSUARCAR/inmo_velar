"""
Tests de integración: canon estimado de la propiedad (T011, FR-010).

Tras renovar arrendamiento o mandato, el `CANON_ARRENDAMIENTO_ESTIMADO`
de la PROPIEDAD debe reflejar el nuevo canon del contrato renovado.
"""

import os
import uuid

import pytest

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos


def _require_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    return DatabaseManager()


def _setup(db):
    matricula = f"TEST-CANON-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, "
            "ESTADO_REGISTRO) VALUES (99999, 'MUNICIPIO CANON', 'DEPTO', TRUE) "
            "ON CONFLICT (ID_MUNICIPIO) DO NOTHING"
        )
        conn.commit()
        cursor.execute(
            """INSERT INTO PROPIEDADES (
                   MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO,
                   ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO,
                   DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
               ) VALUES (%s, 'Calle Canon Test', TRUE, 99999, 'Apartamento',
                         60.0, 3, TRUE, 700000) RETURNING ID_PROPIEDAD""",
            (matricula,),
        )
        row = cursor.fetchone()
        id_prop = row[0] if isinstance(row, tuple) else row["ID_PROPIEDAD"]
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Persona Canon Test', TRUE) RETURNING ID_PERSONA",
            (f"DOC-CANON-{uuid.uuid4().hex[:8]}",),
        )
        row_p = cursor.fetchone()
        id_persona = row_p[0] if isinstance(row_p, tuple) else row_p["ID_PERSONA"]
        cursor.execute(
            "INSERT INTO ARRENDATARIOS (ID_PERSONA, ESTADO_ARRENDATARIO) "
            "VALUES (%s, TRUE) RETURNING ID_ARRENDATARIO",
            (id_persona,),
        )
        row_a = cursor.fetchone()
        id_arrend = row_a[0] if isinstance(row_a, tuple) else row_a["ID_ARRENDATARIO"]
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A='CANCELADO', "
            "MOTIVO_CANCELACION='reset canon' WHERE ID_PROPIEDAD=%s "
            "AND ESTADO_CONTRATO_A='ACTIVO'", (id_prop,),
        )
        conn.commit()
    return id_prop, id_arrend


def _canon_estimado(db, id_prop):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT CANON_ARRENDAMIENTO_ESTIMADO FROM PROPIEDADES WHERE ID_PROPIEDAD = %s",
            (id_prop,),
        )
        row = cursor.fetchone()
        if isinstance(row, tuple):
            return row[0]
        return row["CANON_ARRENDAMIENTO_ESTIMADO"]


def test_renovacion_arrendamiento_actualiza_canon_estimado():
    """FR-010: la propiedad refleja el canon renovado del arrendamiento."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop, id_arrend = _setup(db)

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
        "test_canon",
    )

    renovado = servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_canon")

    canon_estimado = _canon_estimado(db, id_prop)
    assert canon_estimado == renovado.canon_arrendamiento, (
        f"FR-010: canon estimado ({canon_estimado}) debe igualar canon renovado "
        f"({renovado.canon_arrendamiento})"
    )