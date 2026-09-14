"""
Tests unitarios del cast seguro NULLIF y del guard de auditoría (T008, US1).

Cubre:
- E8: las queries de propagación usan `NULLIF(campo,'')::date` (fecha vacía no rompe).
- E10: la auditoría `AUDITORIA_PROPAGACION_CANON` solo registra filas realmente
  modificadas (canon_nuevo != canon_anterior); con 0% o 0 filas, 0 registros.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.aplicacion.servicios.servicio_contrato_arrendamiento import (
    ServicioContratoArrendamiento,
)


def _crear_servicio_con_cursor(records):
    """Construye el servicio con un db mock cuyo cursor captura el SQL ejecutado."""
    db = MagicMock()
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchall.return_value = records
    cursor.rowcount = len(records)
    db.obtener_conexion.return_value = conn
    db.get_dict_cursor.return_value = cursor

    repo_arriendo = MagicMock()
    repo_arriendo.db = db
    repo_propiedad = MagicMock()
    repo_renovacion = MagicMock()
    repo_ipc = MagicMock()
    repo_mandato = MagicMock()

    servicio = ServicioContratoArrendamiento(
        repo_arriendo=repo_arriendo,
        repo_propiedad=repo_propiedad,
        repo_renovacion=repo_renovacion,
        repo_ipc=repo_ipc,
        repo_mandato=repo_mandato,
    )
    return servicio, db, cursor


def _sqls_ejecutados(cursor):
    """Retorna las queries de SELECT (query_sel) y UPDATE capturadas por el mock."""
    sql_selects = []
    sql_updates = []
    for llamada in cursor.execute.call_args_list:
        sql = llamada.args[0]
        if sql.strip().upper().startswith(
            ("SELECT", "WITH")
        ) and "UPDATE" not in sql.upper():
            sql_selects.append(sql)
        elif sql.strip().upper().startswith("UPDATE") or "UPDATE LIQUIDACIONES" in sql:
            sql_updates.append(sql)
    return sql_selects, sql_updates


def _sqls_auditoria(cursor):
    """Retorna las queries INSERT de auditoría capturadas por el mock."""
    return [
        llamada.args[0]
        for llamada in cursor.execute.call_args_list
        if "INSERT INTO AUDITORIA_PROPAGACION_CANON" in llamada.args[0]
    ]


class TestNullifYFechasVacias(unittest.TestCase):
    def test_query_seleccion_liquidaciones_usa_nullif(self):
        """E8: la selección de liquidaciones usa NULLIF(fecha_generacion,'')."""
        servicio, db, cursor = _crear_servicio_con_cursor(records=[])
        servicio.actualizar_canon_liquidaciones_futuras(
            10, 1_100_000, "2026-01-01", "test"
        )
        selects, _ = _sqls_ejecutados(cursor)
        self.assertTrue(selects, "Se esperaba al menos un SELECT")
        self.assertIn("NULLIF(fecha_generacion, '')::date", selects[0])

    def test_query_update_liquidaciones_usa_nullif(self):
        """E8: el UPDATE de liquidaciones usa NULLIF(l.fecha_generacion,'')."""
        records = [{"ID_LIQUIDACION": 1, "CANON_BRUTO": 1_000_000}]
        servicio, db, cursor = _crear_servicio_con_cursor(records=records)
        servicio.actualizar_canon_liquidaciones_futuras(
            10, 1_100_000, "2026-01-01", "test"
        )
        _, updates = _sqls_ejecutados(cursor)
        self.assertTrue(updates, "Se esperaba al menos un UPDATE")
        self.assertIn("NULLIF(l.fecha_generacion, '')::date", updates[0])

    def test_query_recaudos_usa_nullif_en_fecha_pago(self):
        """E8: recaudos usa NULLIF(fecha_pago,'') en selección y update."""
        records = [{"ID_RECAUDO": 1, "VALOR_TOTAL": 1_000_000}]
        servicio, db, cursor = _crear_servicio_con_cursor(records=records)
        servicio.actualizar_valor_recaudos_futuros(10, 1_100_000, "2026-01-01", "test")
        selects, _ = _sqls_ejecutados(cursor)
        self.assertTrue(selects)
        self.assertIn("NULLIF(fecha_pago, '')::date", selects[0])


class TestGuardAuditoria(unittest.TestCase):
    def test_auditoria_solo_registra_filas_modificadas(self):
        """E10: no se inserta auditoría si canon_anterior == canon_nuevo (incremento 0%)."""
        records = [{"ID_LIQUIDACION": 1, "CANON_BRUTO": 1_000_000}]
        servicio, db, cursor = _crear_servicio_con_cursor(records=records)

        servicio.actualizar_canon_liquidaciones_futuras(
            10, 1_000_000, "2026-01-01", "test"
        )
        aud_sqls = _sqls_auditoria(cursor)
        self.assertEqual(
            len(aud_sqls), 0, "No debe auditarse cuando no hubo cambio de canon"
        )

    def test_auditoria_si_registra_filas_con_cambio(self):
        """E10: se audita cada fila real con canon_nuevo != canon_anterior."""
        records = [{"ID_LIQUIDACION": 1, "CANON_BRUTO": 1_000_000}]
        servicio, db, cursor = _crear_servicio_con_cursor(records=records)

        servicio.actualizar_canon_liquidaciones_futuras(
            10, 1_100_000, "2026-01-01", "test"
        )
        aud_sqls = _sqls_auditoria(cursor)
        self.assertEqual(len(aud_sqls), 1, "Debe auditarse la fila modificada")

    def test_auditoria_cero_registros_sin_filas_futuras(self):
        """E10: sin filas futuras no hay filas de auditoría."""
        servicio, db, cursor = _crear_servicio_con_cursor(records=[])
        servicio.actualizar_valor_recaudos_futuros(10, 1_100_000, "2026-01-01", "test")
        aud_sqls = _sqls_auditoria(cursor)
        self.assertEqual(len(aud_sqls), 0)


if __name__ == "__main__":
    unittest.main()