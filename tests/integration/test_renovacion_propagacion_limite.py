"""
Tests de integración: propagación del canon sin desbordamiento (T005, T011).

T005 [US1]: canon $2.300.000 × comisión 1000 (magnitud del contrato 73).
T011 [US2]: canon $10.000.000 × comisión 1500 (máximos del sistema).

Aíslan datos con UUID y limpian sus filas al final. Requieren DATABASE_URL
(mismo convenio que el resto de la suite de renovación).
"""

import os
import uuid
from datetime import date
from decimal import Decimal

import pytest

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.dominio.entidades.contrato_mandato import ContratoMandato


def _require_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    return DatabaseManager()


def _setup_propiedad(db, canon_estimado):
    matricula = f"TEST-LIM-{uuid.uuid4().hex[:8]}"
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
               ) VALUES (%s, 'Calle Limite Test', TRUE, 99999,
                   'Apartamento', 60.0, 3, TRUE, %s) RETURNING ID_PROPIEDAD""",
            (matricula, canon_estimado),
        )
        row = cursor.fetchone()
        conn.commit()
        return row[0] if isinstance(row, tuple) else row["ID_PROPIEDAD"]


def _setup_persona_rol(db, tabla_rol, prefijo):
    doc = f"{prefijo}-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Test Limite', TRUE) RETURNING ID_PERSONA",
            (doc,),
        )
        row = cursor.fetchone()
        id_persona = row[0] if isinstance(row, tuple) else row["ID_PERSONA"]
        cursor.execute(
            f"INSERT INTO {tabla_rol} (ID_PERSONA) VALUES (%s)",
            (id_persona,),
        )
        conn.commit()
    return id_persona


def _id_rol(db, tabla_rol, id_persona, col_id):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT {col_id} FROM {tabla_rol} WHERE ID_PERSONA = %s ORDER BY {col_id} DESC LIMIT 1",
            (id_persona,),
        )
        row = cursor.fetchone()
        return row[0] if isinstance(row, tuple) else row[col_id]


def _setup_mandato(servicio, id_prop, id_propietario, id_asesor, canon):
    mandato = ContratoMandato(
        id_propiedad=id_prop,
        id_propietario=id_propietario,
        id_asesor=id_asesor,
        fecha_inicio_contrato_m="2024-01-01",
        fecha_fin_contrato_m="2024-12-31",
        duracion_contrato_m=12,
        canon_mandato=canon,
        comision_porcentaje_contrato_m=1000,
    )
    return servicio.repo_mandato.crear(mandato, "test_limite")


def _setup_liquidacion_futura(db, id_contrato_m, canon, comision):
    hoy = date.today().isoformat()
    periodo = date.today().strftime("%Y-%m")
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO LIQUIDACIONES (
                   ID_CONTRATO_M, PERIODO, FECHA_GENERACION, CANON_BRUTO,
                   TOTAL_INGRESOS, COMISION_PORCENTAJE, COMISION_MONTO,
                   IVA_COMISION, IMPUESTO_4X1000, TOTAL_EGRESOS, NETO_A_PAGAR
               ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s)
               RETURNING ID_LIQUIDACION""",
            (
                id_contrato_m,
                periodo,
                hoy,
                canon,
                canon,
                comision,
                (canon * comision) // 10000,
                int(Decimal((canon * comision) // 10000) * Decimal("0.19")),
                0,
                canon,
            ),
        )
        row = cursor.fetchone()
        conn.commit()
        return row[0] if isinstance(row, tuple) else row["ID_LIQUIDACION"]


def _ipc_vigente(db):
    with db.obtener_conexion() as conn:
        cursor = db.get_dict_cursor(conn)
        cursor.execute("SELECT VALOR_IPC FROM IPC ORDER BY ANIO DESC LIMIT 1")
        row = cursor.fetchone()
        if row is None:
            return 0.0
        val = row["VALOR_IPC"] if isinstance(row, dict) else row[0]
        return float(val)


def _liquidacion(db, id_liq):
    with db.obtener_conexion() as conn:
        cursor = db.get_dict_cursor(conn)
        cursor.execute(
            "SELECT * FROM LIQUIDACIONES WHERE ID_LIQUIDACION = %s", (id_liq,)
        )
        return dict(cursor.fetchone())


def _auditorias(db, id_contrato_a, id_liq):
    with db.obtener_conexion() as conn:
        cursor = db.get_dict_cursor(conn)
        cursor.execute(
            """SELECT * FROM AUDITORIA_PROPAGACION_CANON
               WHERE CONTRATO_ID = %s AND TABLA_AFECTADA = 'LIQUIDACIONES'
               AND REGISTRO_ID = %s""",
            (id_contrato_a, str(id_liq)),
        )
        return [dict(r) for r in cursor.fetchall()]


def _limpiar(db, ids):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM IPC_INCREMENT_HISTORY WHERE ID_CONTRATO_A = %s",
            (ids["arriendo"],),
        )
        cursor.execute(
            "DELETE FROM AUDITORIA_PROPAGACION_CANON WHERE CONTRATO_ID = %s",
            (ids["arriendo"],),
        )
        cursor.execute(
            "DELETE FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s",
            (ids["arriendo"],),
        )
        cursor.execute(
            "DELETE FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_M = %s",
            (ids["mandato"],),
        )
        cursor.execute(
            "DELETE FROM LIQUIDACIONES WHERE ID_CONTRATO_M = %s", (ids["mandato"],)
        )
        cursor.execute(
            "DELETE FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = %s",
            (ids["arriendo"],),
        )
        cursor.execute(
            "DELETE FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = %s", (ids["mandato"],)
        )
        cursor.execute(
            "DELETE FROM PROPIEDADES WHERE ID_PROPIEDAD = %s", (ids["prop"],)
        )
        for tabla, col, valor in [
            ("ARRENDATARIOS", "ID_PERSONA", ids["per_arr"]),
            ("PROPIETARIOS", "ID_PERSONA", ids["per_prop"]),
            ("ASESORES", "ID_PERSONA", ids["per_ase"]),
        ]:
            cursor.execute(f"DELETE FROM {tabla} WHERE ID_PERSONA = %s", (valor,))
        for per in (ids["per_arr"], ids["per_prop"], ids["per_ase"]):
            cursor.execute("DELETE FROM PERSONAS WHERE ID_PERSONA = %s", (per,))
        conn.commit()


def _flujo_limite(canon, comision):
    db = _require_db()
    servicio = ServicioContratos(db)
    ids = {}
    try:
        ids["prop"] = _setup_propiedad(db, canon)
        ids["per_arr"] = _setup_persona_rol(db, "ARRENDATARIOS", "DOC-LIM-A")
        id_arr = _id_rol(db, "ARRENDATARIOS", ids["per_arr"], "ID_ARRENDATARIO")
        ids["per_prop"] = _setup_persona_rol(db, "PROPIETARIOS", "DOC-LIM-P")
        id_propietario = _id_rol(db, "PROPIETARIOS", ids["per_prop"], "ID_PROPIETARIO")
        ids["per_ase"] = _setup_persona_rol(db, "ASESORES", "DOC-LIM-S")
        id_asesor = _id_rol(db, "ASESORES", ids["per_ase"], "ID_ASESOR")

        contrato = servicio.crear_arrendamiento(
            {
                "id_propiedad": ids["prop"],
                "id_arrendatario": id_arr,
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-12-31",
                "duracion_meses": 12,
                "canon": canon,
                "deposito": 0,
            },
            "test_limite",
        )
        ids["arriendo"] = contrato.id_contrato_a
        mandato = _setup_mandato(
            servicio, ids["prop"], id_propietario, id_asesor, canon
        )
        ids["mandato"] = mandato.id_contrato_m
        id_liq = _setup_liquidacion_futura(db, ids["mandato"], canon, comision)

        pct = _ipc_vigente(db)
        esperado_nuevo = int(canon * (1 + pct / 100)) if pct else canon

        renovado = servicio.renovar_arrendamiento(ids["arriendo"], "test_limite")

        assert renovado.canon_arrendamiento == esperado_nuevo
        liq = _liquidacion(db, id_liq)
        com_esp = (esperado_nuevo * comision) // 10000
        iva_esp = int(Decimal(com_esp) * Decimal("0.19"))
        assert liq["CANON_BRUTO"] == esperado_nuevo
        assert liq["COMISION_MONTO"] == com_esp
        assert liq["IVA_COMISION"] == iva_esp
        audit = _auditorias(db, ids["arriendo"], id_liq)
        assert len(audit) >= 1
        return esperado_nuevo
    finally:
        if ids.get("arriendo") and ids.get("mandato"):
            _limpiar(db, ids)


def test_T005_propagacion_canon_alto_sin_desbordamiento():
    """US1: 2.300.000 × 1000 (magnitud contrato 73) propaga exacto."""
    _flujo_limite(2_300_000, 1000)


def test_T011_propagacion_maximos_sistema_sin_desbordamiento():
    """US2: 10.000.000 × 1500 (máximos) propaga exacto."""
    _flujo_limite(10_000_000, 1500)
