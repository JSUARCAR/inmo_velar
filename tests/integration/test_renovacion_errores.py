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


def test_renovar_contrato_inactivo_lanza_contrato_no_renovable(request):
    """FR-008: renovar un contrato no ACTIVO lanza ContratoNoRenovableError."""
    db = _require_db()
    servicio = ServicioContratos(db)

    # Crear contrato y luego cancelarlo para que quede inactivo
    ids = _crear_arriendo_y_cancelar(db, servicio)
    if ids.get("id_contrato_a") is None:
        pytest.skip("No se pudo preparar contrato inactivo")
    request.addfinalizer(lambda: _limpiar(db, ids))

    with pytest.raises(ContratoNoRenovableError):
        servicio.renovar_arrendamiento(ids["id_contrato_a"], "test_user")


def test_mandato_inexistente_lanza_contrato_no_renovable():
    """FR-008: renovar un mandato inexistente lanza ContratoNoRenovableError."""
    db = _require_db()
    servicio = ServicioContratos(db)

    with pytest.raises(ContratoNoRenovableError):
        servicio.renovar_mandato(99_999_999, "test_user")


def _crear_arriendo_y_cancelar(db, servicio):
    """Crea un contrato de arrendamiento y lo cancela. Retorna dict de IDs."""
    id_prop = _setup_propiedad(db)
    if id_prop is None:
        return {"id_prop": None, "id_arrend": None, "id_persona": None, "id_contrato_a": None}
    id_arrendatario, id_persona = _setup_arrendatario(db)
    if id_arrendatario is None:
        return {"id_prop": id_prop, "id_arrend": None, "id_persona": None, "id_contrato_a": None}

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

    return {
        "id_prop": id_prop,
        "id_arrend": id_arrendatario,
        "id_persona": id_persona,
        "id_contrato_a": contrato.id_contrato_a,
    }


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
            return row2[0] if isinstance(row2, tuple) else row2["ID_ARRENDATARIO"], id_persona
    except Exception:
        return None, None


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