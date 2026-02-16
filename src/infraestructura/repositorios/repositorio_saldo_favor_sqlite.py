"""
Repositorio SQLite para entidad SaldoFavor.
Implementa operaciones CRUD y consultas especializadas.
"""

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.dominio.entidades.saldo_favor import SaldoFavor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioSaldoFavorSQLite:
    """Repositorio para gestión de saldos a favor en SQLite"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def crear(self, saldo: SaldoFavor, usuario: str) -> SaldoFavor:
        """
        Crea un nuevo saldo a favor.

        Args:
            saldo: Entidad SaldoFavor a crear
            usuario: Usuario que crea el registro

        Returns:
            SaldoFavor con ID asignado
        """
        placeholder = self.db_manager.get_placeholder()
        query = f"""
            INSERT INTO SALDOS_FAVOR (
                ID_PROPIETARIO, ID_ASESOR, TIPO_BENEFICIARIO,
                VALOR_SALDO, MOTIVO, FECHA_GENERACION,
                ESTADO, FECHA_RESOLUCION, OBSERVACIONES,
                CREATED_BY, UPDATED_BY
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """

        params = (
            saldo.id_propietario,
            saldo.id_asesor,
            saldo.tipo_beneficiario,
            saldo.valor_saldo,
            saldo.motivo,
            saldo.fecha_generacion or datetime.now().strftime("%Y-%m-%d"),
            saldo.estado,
            saldo.fecha_resolucion,
            saldo.observaciones,
            usuario,
            usuario,
        )

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            saldo.id_saldo_favor = cursor.lastrowid
            return saldo

    def actualizar(self, saldo: SaldoFavor, usuario: str) -> SaldoFavor:
        """
        Actualiza un saldo a favor existente.

        Args:
            saldo: Entidad SaldoFavor con datos actualizados
            usuario: Usuario que actualiza el registro

        Returns:
            SaldoFavor actualizado

        Raises:
            ValueError: Si el saldo no existe
        """
        placeholder = self.db_manager.get_placeholder()
        query = f"""
            UPDATE SALDOS_FAVOR SET
                ID_PROPIETARIO = {placeholder},
                ID_ASESOR = {placeholder},
                TIPO_BENEFICIARIO = {placeholder},
                VALOR_SALDO = {placeholder},
                MOTIVO = {placeholder},
                FECHA_GENERACION = {placeholder},
                ESTADO = {placeholder},
                FECHA_RESOLUCION = {placeholder},
                OBSERVACIONES = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_SALDO_FAVOR = {placeholder}
        """

        params = (
            saldo.id_propietario,
            saldo.id_asesor,
            saldo.tipo_beneficiario,
            saldo.valor_saldo,
            saldo.motivo,
            saldo.fecha_generacion,
            saldo.estado,
            saldo.fecha_resolucion,
            saldo.observaciones,
            datetime.now().isoformat(),
            usuario,
            saldo.id_saldo_favor,
        )

        affected = self.db_manager.execute_write(query, params)
        if affected == 0:
            raise ValueError(f"No se encontró el saldo con ID {saldo.id_saldo_favor}")

        saldo.updated_by = usuario
        saldo.updated_at = datetime.now().isoformat()
        return saldo

    def obtener_por_id(self, id_saldo: int) -> Optional[SaldoFavor]:
        """
        Obtiene un saldo a favor por su ID.

        Args:
            id_saldo: ID del saldo

        Returns:
            SaldoFavor o None si no existe
        """
        placeholder = self.db_manager.get_placeholder()
        query = f"SELECT * FROM SALDOS_FAVOR WHERE ID_SALDO_FAVOR = {placeholder}"

        row = self.db_manager.execute_query_one(query, (id_saldo,))
        return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[SaldoFavor]:
        """
        Lista todos los saldos a favor.

        Returns:
            Lista de SaldoFavor
        """
        query = """
            SELECT * FROM SALDOS_FAVOR
            ORDER BY FECHA_GENERACION DESC
        """

        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_por_propietario(self, id_propietario: int) -> List[SaldoFavor]:
        """
        Lista saldos a favor de un propietario específico.

        Args:
            id_propietario: ID del propietario

        Returns:
            Lista de SaldoFavor
        """
        placeholder = self.db_manager.get_placeholder()
        query = f"""
            SELECT * FROM SALDOS_FAVOR
            WHERE ID_PROPIETARIO = {placeholder}
            ORDER BY FECHA_GENERACION DESC
        """

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_propietario,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_por_asesor(self, id_asesor: int) -> List[SaldoFavor]:
        """
        Lista saldos a favor de un asesor específico.

        Args:
            id_asesor: ID del asesor

        Returns:
            Lista de SaldoFavor
        """
        placeholder = self.db_manager.get_placeholder()
        query = f"""
            SELECT * FROM SALDOS_FAVOR
            WHERE ID_ASESOR = {placeholder}
            ORDER BY FECHA_GENERACION DESC
        """

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_asesor,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_por_estado(self, estado: str) -> List[SaldoFavor]:
        """
        Lista saldos por estado.

        Args:
            estado: Estado a filtrar (Pendiente, Aplicado, Devuelto)

        Returns:
            Lista de SaldoFavor
        """
        placeholder = self.db_manager.get_placeholder()
        query = f"""
            SELECT * FROM SALDOS_FAVOR
            WHERE ESTADO = {placeholder}
            ORDER BY FECHA_GENERACION DESC
        """

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (estado,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_pendientes(self) -> List[SaldoFavor]:
        """
        Lista todos los saldos pendientes de resolución.

        Returns:
            Lista de SaldoFavor pendientes
        """
        return self.listar_por_estado("Pendiente")

    def listar_con_filtros(
        self,
        tipo_beneficiario: Optional[str] = None,
        estado: Optional[str] = None,
        id_propietario: Optional[int] = None,
        id_asesor: Optional[int] = None,
    ) -> List[SaldoFavor]:
        """
        Lista saldos con múltiples filtros.

        Args:
            tipo_beneficiario: Filtrar por tipo (Propietario, Asesor)
            estado: Filtrar por estado
            id_propietario: Filtrar por propietario específico
            id_asesor: Filtrar por asesor específico

        Returns:
            Lista de SaldoFavor filtrados
        """
        placeholder = self.db_manager.get_placeholder()
        query = "SELECT * FROM SALDOS_FAVOR WHERE 1=1"
        params = []

        if tipo_beneficiario:
            query += f" AND TIPO_BENEFICIARIO = {placeholder}"
            params.append(tipo_beneficiario)

        if estado:
            query += f" AND ESTADO = {placeholder}"
            params.append(estado)

        if id_propietario is not None:
            query += f" AND ID_PROPIETARIO = {placeholder}"
            params.append(id_propietario)

        if id_asesor is not None:
            query += f" AND ID_ASESOR = {placeholder}"
            params.append(id_asesor)

        query += " ORDER BY FECHA_GENERACION DESC"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def obtener_total_pendiente_propietario(self, id_propietario: int) -> int:
        """
        Obtiene el total de saldo pendiente para un propietario.

        Args:
            id_propietario: ID del propietario

        Returns:
            Suma total de saldos pendientes
        """
        placeholder = self.db_manager.get_placeholder()
        query = f"""
            SELECT COALESCE(SUM(VALOR_SALDO), 0) as total
            FROM SALDOS_FAVOR
            WHERE ID_PROPIETARIO = {placeholder} AND ESTADO = 'Pendiente'
        """

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_propietario,))
            row = cursor.fetchone()
            # Handle both list/tuple and dict results
            if isinstance(row, dict):
                return row.get("total", 0) or 0
            return row[0] if row else 0

    def obtener_total_pendiente_asesor(self, id_asesor: int) -> int:
        """
        Obtiene el total de saldo pendiente para un asesor.

        Args:
            id_asesor: ID del asesor

        Returns:
            Suma total de saldos pendientes
        """
        placeholder = self.db_manager.get_placeholder()
        query = f"""
            SELECT COALESCE(SUM(VALOR_SALDO), 0) as total
            FROM SALDOS_FAVOR
            WHERE ID_ASESOR = {placeholder} AND ESTADO = 'Pendiente'
        """

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_asesor,))
            row = cursor.fetchone()
            # Handle both list/tuple and dict results
            if isinstance(row, dict):
                return row.get("total", 0) or 0
            return row[0] if row else 0

    def obtener_resumen_general(self) -> Dict[str, Any]:
        """
        Obtiene resumen general de saldos a favor.

        Returns:
            Diccionario con totales por estado y tipo
        """
        query = """
            SELECT 
                TIPO_BENEFICIARIO,
                ESTADO,
                COUNT(*) as cantidad,
                COALESCE(SUM(VALOR_SALDO), 0) as total
            FROM SALDOS_FAVOR
            GROUP BY TIPO_BENEFICIARIO, ESTADO
        """

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            resumen = {
                "propietarios_pendiente": 0,
                "propietarios_aplicado": 0,
                "propietarios_devuelto": 0,
                "asesores_pendiente": 0,
                "asesores_aplicado": 0,
                "asesores_devuelto": 0,
                "total_pendiente": 0,
                "total_resuelto": 0,
            }

            for row in rows:
                tipo = row[0].lower() + "s"  # 'Propietario' -> 'propietarios'
                estado = row[1].lower()  # 'Pendiente' -> 'pendiente'
                key = f"{tipo}_{estado}"
                resumen[key] = row[3]

                if estado == "pendiente":
                    resumen["total_pendiente"] += row[3]
                else:
                    resumen["total_resuelto"] += row[3]

            return resumen

    def eliminar(self, id_saldo: int) -> bool:
        """
        Elimina (físicamente) un saldo a favor.

        Args:
            id_saldo: ID del saldo a eliminar

        Returns:
            True si se eliminó, False si no existía
        """
        placeholder = self.db_manager.get_placeholder()
        query = f"DELETE FROM SALDOS_FAVOR WHERE ID_SALDO_FAVOR = {placeholder}"
        return self.db_manager.execute_write(query, (id_saldo,)) > 0

    def _row_to_entity(self, row: sqlite3.Row) -> SaldoFavor:
        """
        Convierte una fila de BD a entidad SaldoFavor.

        Args:
            row: Fila de SQLite

        Returns:
            SaldoFavor
        """
        return SaldoFavor(
            id_saldo_favor=row["ID_SALDO_FAVOR"],
            id_propietario=row["ID_PROPIETARIO"],
            id_asesor=row["ID_ASESOR"],
            tipo_beneficiario=row["TIPO_BENEFICIARIO"],
            valor_saldo=row["VALOR_SALDO"],
            motivo=row["MOTIVO"],
            fecha_generacion=row["FECHA_GENERACION"],
            estado=row["ESTADO"],
            fecha_resolucion=row["FECHA_RESOLUCION"],
            observaciones=row["OBSERVACIONES"],
            created_at=row["CREATED_AT"],
            created_by=row["CREATED_BY"],
            updated_at=row["UPDATED_AT"],
            updated_by=row["UPDATED_BY"],
        )
