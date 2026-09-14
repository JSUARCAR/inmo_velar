"""
Tests de integración: ContratoNoRenovableError (T012, US1).

Verifica que la renovación de un contrato inactivo o inexistente lanza
`ContratoNoRenovableError` (FR-008) en lugar de `ValueError`.
"""

import os
import uuid

import pytest

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.dominio.excepciones.excepciones_base import ContratoNoRenovableError


def _require_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    return DatabaseManager()


def test_renovar_contrato_inexistente_lanza_contrato_no_renovable():
    """FR-008: renovar un contrato inexistente lanza ContratoNoRenovableError."""
    db = _require_db()
    servicio = ServicioContratos(db)

    with pytest.raises(ContratoNoRenovableError):
        servicio.renovar_arrendamiento(99_999_999, "test_user")


def test_renovar_contrato_inactivo_lanza_contrato_no_renovable():
    """FR-008: renovar un contrato no ACTIVO lanza ContratoNoRenovableError."""
    db = _require_db()
    servicio = ServicioContratos(db)

    # Crear contrato y luego cancelarlo para que quede inactivo
    id_contrato, _ = _crear_arriendo_y_cancelar(db, servicio)
    if id_contrato is None:
        pytest.skip("No se pudo preparar contrato inactivo")

    with pytest.raises(ContratoNoRenovableError):
        servicio.renovar_arrendamiento(id_contrato, "test_user")


def test_mandato_inexistente_lanza_contrato_no_renovable():
    """FR-008: renovar un mandato inexistente lanza ContratoNoRenovableError."""
    db = _require_db()
    servicio = ServicioContratos(db)

    with pytest.raises(ContratoNoRenovableError):
        servicio.renovar_mandato(99_999_999, "test_user")


def _crear_arriendo_y_cancelar(db, servicio):
    """Crea un contrato de arrendamiento y lo cancela. Retorna (id_contrato, propiedad)."""
    id_prop = _setup_propiedad(db)
    if id_prop is None:
        return None, None
    id_arrendatario = _setup_arrendatario(db)
    if id_arrendatario is None:
        return None, None

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
        "test_user",
    )

    # Marcar el contrato como inactivo (no puede renovarse)
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'CANCELADO', "
            "MOTIVO_CANCELACION = 'test cancelado' WHERE ID_CONTRATO_A = %s",
            (contrato.id_contrato_a,),
        )
        conn.commit()

    return contrato.id_contrato_a, id_prop


def _setup_propiedad(db):
    matricula = f"TEST-ERR-{uuid.uuid4().hex[:8]}"
    try:
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
                       %s, 'Calle Err Test', TRUE, 99999,
                       'Apartamento', 60.0, 3, TRUE, 1000000
                   ) RETURNING ID_PROPIEDAD""",
                (matricula,),
            )
            row = cursor.fetchone()
            conn.commit()
            return row[0] if isinstance(row, tuple) else row["ID_PROPIEDAD"]
    except Exception:
        return None


def _setup_arrendatario(db):
    doc = f"DOC-ERR-{uuid.uuid4().hex[:8]}"
    try:
        with db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
                "VALUES (%s, 'Test Err User', TRUE) RETURNING ID_PERSONA",
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
            conn.commit()
            return row2[0] if isinstance(row2, tuple) else row2["ID_ARRENDATARIO"]
    except Exception:
        return None