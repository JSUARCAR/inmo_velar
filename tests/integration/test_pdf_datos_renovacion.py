"""
Tests de integración: datos del PDF reflejan canon renovado (T010, SC-004).

Verifica que el origen de datos del generador PDF
(`_get_datos_contrato` → `obtener_detalle_contrato_ui`) refleja el canon y
las fechas renovadas tras ejecutar la renovación.
"""

import os
import uuid

import pytest

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.infraestructura.persistencia.repositorio_ipc_postgres import RepositorioIPCPostgres


def _require_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    return DatabaseManager()


def _setup(db):
    matricula = f"TEST-PDF-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, "
            "ESTADO_REGISTRO) VALUES (99999, 'MUNICIPIO PDF', 'DEPTO', TRUE) "
            "ON CONFLICT (ID_MUNICIPIO) DO NOTHING"
        )
        conn.commit()
        cursor.execute(
            """INSERT INTO PROPIEDADES (
                   MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO,
                   ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO,
                   DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
               ) VALUES (%s, 'Calle PDF Test', TRUE, 99999, 'Apartamento',
                         60.0, 3, TRUE, 1000000) RETURNING ID_PROPIEDAD""",
            (matricula,),
        )
        row = cursor.fetchone()
        id_prop = row[0] if isinstance(row, tuple) else row["ID_PROPIEDAD"]
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Persona PDF Test', TRUE) RETURNING ID_PERSONA",
            (f"DOC-PDF-{uuid.uuid4().hex[:8]}",),
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
            "MOTIVO_CANCELACION='reset pdf' WHERE ID_PROPIEDAD=%s "
            "AND ESTADO_CONTRATO_A='ACTIVO'", (id_prop,),
        )
        conn.commit()
    return id_prop, id_arrend, id_persona


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


def _ipc_vigente(db):
    repo_ipc = RepositorioIPCPostgres(db)
    vigente = repo_ipc.obtener_ultimo()
    return vigente.valor_ipc if vigente else 0.0


def test_pdf_datos_reflejan_canon_renovado(request):
    """SC-004: tras renovar, el detalle para PDF muestra canon y fechas nuevos."""
    db = _require_db()
    servicio = ServicioContratos(db)
    valor_ipc = _ipc_vigente(db)

    id_prop, id_arrend, id_persona = _setup(db)
    ids = {"id_prop": id_prop, "id_arrend": id_arrend, "id_persona": id_persona}
    request.addfinalizer(lambda: _limpiar(db, ids))
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
        "test_pdf",
    )
    ids["id_contrato_a"] = contrato.id_contrato_a

    renovado = servicio.renovar_arrendamiento(contrato.id_contrato_a, "test_pdf")

    detalle = servicio.obtener_detalle_contrato_ui(contrato.id_contrato_a, "Arrendamiento")

    canon_esperado = int(1_000_000 * (1 + valor_ipc / 100))
    assert detalle is not None, "El detalle para PDF no debe ser None tras renovar"
    assert detalle["canon"] == canon_esperado, (
        f"SC-004: canon del PDF debe ser {canon_esperado} tras IPC {valor_ipc}%; "
        f"obtuvo {detalle['canon']}"
    )
    assert renovado.canon_arrendamiento == detalle["canon"]
    assert detalle["fecha_fin"] == renovado.fecha_fin_contrato_a, (
        "SC-004: fecha_fin del PDF debe coincidir con la fecha renovada"
    )