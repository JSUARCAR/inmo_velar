"""
Pruebas de integración para el filtrado de vencimientos del Dashboard.

Valida que la aritmética de fechas funcione correctamente post-fix ADR-0010.
Usa SQLite temporal para simular el comportamiento del repositorio.
"""

import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Generator

import pytest

from src.infraestructura.persistencia.repositorio_dashboard import RepositorioDashboard
from tests.integration.test_database_manager import TestDatabaseManager


class _TestDBManagerContextManager(TestDatabaseManager):
    """Extiende TestDatabaseManager para que obtener_conexion sea context manager.

    RepositorioDashboard usa ``with self.db.obtener_conexion() as conn:``,
    pero el TestDatabaseManager base retorna la conexión directamente.
    Esta subclase envuelve el retorno con ``@contextmanager``.
    """

    @contextmanager
    def obtener_conexion(self) -> Generator[sqlite3.Connection, None, None]:
        """Retorna la conexión existente como context manager reutilizable."""
        conn = super().obtener_conexion()
        try:
            yield conn
        finally:
            pass  # No cerrar — reutilizar en el mismo test

    def obtener_conexion_directa(self) -> sqlite3.Connection:
        """Acceso directo a la conexión sin context manager.

        Útil para insertar datos de setup antes de las pruebas.
        """
        return super().obtener_conexion()


def _crear_esquema(conn: sqlite3.Connection) -> None:
    """Crea las tablas mínimas necesarias para las queries de vencimientos.

    Solo incluye columnas requeridas por ``_get_sql_vencimientos()`` SQLite.
    """
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS PERSONAS (
            ID_PERSONA INTEGER PRIMARY KEY,
            NOMBRE_COMPLETO TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS MUNICIPIOS (
            ID_MUNICIPIO INTEGER PRIMARY KEY,
            NOMBRE_MUNICIPIO TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS PROPIEDADES (
            ID_PROPIEDAD INTEGER PRIMARY KEY,
            DIRECCION_PROPIEDAD TEXT NOT NULL,
            ID_MUNICIPIO INTEGER,
            DISPONIBILIDAD_PROPIEDAD BOOLEAN DEFAULT 0,
            ESTADO_REGISTRO BOOLEAN DEFAULT 1,
            TIPO_PROPIEDAD TEXT DEFAULT 'CASA',
            CANON_ARRENDAMIENTO_ESTIMADO REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS ARRENDATARIOS (
            ID_ARRENDATARIO INTEGER PRIMARY KEY,
            ID_PERSONA INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS PROPIETARIOS (
            ID_PROPIETARIO INTEGER PRIMARY KEY,
            ID_PERSONA INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS CONTRATOS_ARRENDAMIENTOS (
            ID_CONTRATO_A INTEGER PRIMARY KEY,
            ID_PROPIEDAD INTEGER NOT NULL,
            ID_ARRENDATARIO INTEGER NOT NULL,
            ESTADO_CONTRATO_A TEXT NOT NULL,
            FECHA_FIN_CONTRATO_A TEXT NOT NULL,
            CANON_ARRENDAMIENTO REAL DEFAULT 500000,
            FECHA_PAGO INTEGER DEFAULT 1,
            FECHA_INICIO_CONTRATO_A TEXT DEFAULT '2024-01-01'
        );
        CREATE TABLE IF NOT EXISTS CONTRATOS_MANDATOS (
            ID_CONTRATO_M INTEGER PRIMARY KEY,
            ID_PROPIEDAD INTEGER NOT NULL,
            ID_PROPIETARIO INTEGER NOT NULL,
            ID_ASESOR INTEGER DEFAULT 1,
            ESTADO_CONTRATO_M TEXT NOT NULL,
            FECHA_FIN_CONTRATO_M TEXT NOT NULL,
            CANON_MANDATO REAL DEFAULT 500000,
            COMISION_PORCENTAJE_CONTRATO_M REAL DEFAULT 1000
        );
    """)
    # Datos base compartidos por todos los tests
    conn.execute(
        "INSERT INTO PERSONAS (ID_PERSONA, NOMBRE_COMPLETO) "
        "VALUES (1, 'TEST PERSONA')"
    )
    conn.execute(
        "INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO) "
        "VALUES (1, 'TEST MUNICIPIO')"
    )
    conn.execute(
        "INSERT INTO ARRENDATARIOS (ID_ARRENDATARIO, ID_PERSONA) VALUES (1, 1)"
    )
    conn.commit()


def _insertar_contrato_arrendamiento(
    conn: sqlite3.Connection,
    id_contrato: int,
    fecha_fin: str,
    estado: str = "ACTIVO",
) -> None:
    """Inserta un contrato de arrendamiento con datos mínimos.

    Args:
        conn: Conexión SQLite activa.
        id_contrato: ID único del contrato (también usado como ID_PROPIEDAD).
        fecha_fin: Fecha de fin en formato ISO 8601.
        estado: Estado del contrato (default ``ACTIVO``).
    """
    conn.execute(
        "INSERT OR IGNORE INTO PROPIEDADES "
        "(ID_PROPIEDAD, DIRECCION_PROPIEDAD, ID_MUNICIPIO) VALUES (?, ?, ?)",
        (id_contrato, f"PROPIEDAD TEST {id_contrato}", 1),
    )
    conn.execute(
        "INSERT INTO CONTRATOS_ARRENDAMIENTOS "
        "(ID_CONTRATO_A, ID_PROPIEDAD, ID_ARRENDATARIO, "
        "ESTADO_CONTRATO_A, FECHA_FIN_CONTRATO_A) "
        "VALUES (?, ?, 1, ?, ?)",
        (id_contrato, id_contrato, estado, fecha_fin),
    )
    conn.commit()


def _insertar_contrato_mandato(
    conn: sqlite3.Connection, id_contrato: int, fecha_fin: str, estado: str = "ACTIVO"
) -> None:
    """Inserta un contrato de mandato con datos mínimos."""
    conn.execute(
        "INSERT OR IGNORE INTO PROPIEDADES "
        "(ID_PROPIEDAD, DIRECCION_PROPIEDAD, ID_MUNICIPIO) VALUES (?, ?, ?)",
        (id_contrato, f"PROPIEDAD TEST MANDATO {id_contrato}", 1),
    )
    # Se inserta un propietario ficticio asumiendo ID_PERSONA=1
    conn.execute(
        "INSERT OR IGNORE INTO PROPIETARIOS (ID_PROPIETARIO, ID_PERSONA) VALUES (?, ?)",
        (1, 1),
    )
    conn.execute(
        "INSERT INTO CONTRATOS_MANDATOS "
        "(ID_CONTRATO_M, ID_PROPIEDAD, ID_PROPIETARIO, ESTADO_CONTRATO_M, FECHA_FIN_CONTRATO_M) "
        "VALUES (?, ?, 1, ?, ?)",
        (id_contrato, id_contrato, estado, fecha_fin),
    )
    conn.commit()


@pytest.fixture
def db_manager(tmp_path: Path) -> _TestDBManagerContextManager:
    """Fixture que crea un TestDatabaseManager con esquema y context manager.

    Returns:
        Instancia configurada con esquema de vencimientos.
    """
    db_path = str(tmp_path / "test_vencimientos.db")
    manager = _TestDBManagerContextManager(db_path)
    conn = manager.obtener_conexion_directa()
    _crear_esquema(conn)
    return manager


class TestVencimientosFiltrado:
    """Valida el filtrado por días restantes en obtener_lista_vencimientos."""

    def test_contrato_proximo_incluido_en_90_dias(
        self, db_manager: _TestDBManagerContextManager
    ) -> None:
        """Un contrato que vence en 40 días DEBE aparecer en la lista de 90."""
        fecha_fin = (date.today() + timedelta(days=40)).isoformat()
        conn = db_manager.obtener_conexion_directa()
        _insertar_contrato_arrendamiento(conn, 1, fecha_fin)

        repo = RepositorioDashboard(db_manager)
        resultados = repo.obtener_lista_vencimientos(90)

        assert len(resultados) >= 1
        contrato = next(
            (r for r in resultados if 39 <= r["dias_restantes"] <= 41), None
        )
        assert (
            contrato is not None
        ), f"No se encontró contrato con ~40 días. Resultados: {resultados}"
        assert contrato["tipo_contrato"] == "ARRENDAMIENTO"

    def test_contrato_lejano_excluido_de_90_dias(
        self, db_manager: _TestDBManagerContextManager
    ) -> None:
        """Un contrato que vence en 200 días NO debe aparecer en la lista de 90."""
        fecha_fin = (date.today() + timedelta(days=200)).isoformat()
        conn = db_manager.obtener_conexion_directa()
        _insertar_contrato_arrendamiento(conn, 2, fecha_fin)

        repo = RepositorioDashboard(db_manager)
        resultados = repo.obtener_lista_vencimientos(90)

        contrato_lejano = next(
            (r for r in resultados if r["dias_restantes"] >= 150), None
        )
        assert (
            contrato_lejano is None
        ), f"Contrato lejano NO debería estar. Resultados: {resultados}"

    def test_contrato_vencido_activo_incluido(
        self, db_manager: _TestDBManagerContextManager
    ) -> None:
        """Un contrato ACTIVO cuya fecha ya pasó (días negativos) DEBE aparecer."""
        fecha_fin = (date.today() - timedelta(days=5)).isoformat()
        conn = db_manager.obtener_conexion_directa()
        _insertar_contrato_arrendamiento(conn, 3, fecha_fin)

        repo = RepositorioDashboard(db_manager)
        resultados = repo.obtener_lista_vencimientos(90)

        contrato_vencido = next(
            (r for r in resultados if r["dias_restantes"] < 0), None
        )
        assert (
            contrato_vencido is not None
        ), f"Contrato vencido debería aparecer. Resultados: {resultados}"

    def test_mandato_proximo_incluido_en_90_dias(
        self, db_manager: _TestDBManagerContextManager
    ) -> None:
        """Un contrato de MANDATO que vence en 40 días DEBE aparecer en la lista."""
        fecha_fin = (date.today() + timedelta(days=40)).isoformat()
        conn = db_manager.obtener_conexion_directa()
        _insertar_contrato_mandato(conn, 4, fecha_fin)

        repo = RepositorioDashboard(db_manager)
        resultados = repo.obtener_lista_vencimientos(90)

        contrato = next(
            (
                r
                for r in resultados
                if r["tipo_contrato"] == "MANDATO" and 39 <= r["dias_restantes"] <= 41
            ),
            None,
        )
        assert (
            contrato is not None
        ), f"No se encontró MANDATO con ~40 días. Resultados: {resultados}"
