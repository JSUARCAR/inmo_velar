"""
Servicio de Aplicación: Saldos a Favor
Gestiona la lógica de negocio para saldos a favor de propietarios y asesores.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from src.dominio.entidades.saldo_favor import SaldoFavor
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.repositorios.repositorio_saldo_favor_sqlite import (
    RepositorioSaldoFavorSQLite,
)


class ServicioSaldosFavor:
    """
    Servicio para gestión de saldos a favor.

    Maneja la lógica de negocio para registrar, aplicar y devolver
    saldos a favor de propietarios y asesores.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.repositorio = RepositorioSaldoFavorSQLite(db_manager)

    def registrar_saldo(
        self,
        tipo_beneficiario: str,
        id_beneficiario: int,
        valor: int,
        motivo: str,
        observaciones: Optional[str] = None,
        usuario: str = "sistema",
    ) -> SaldoFavor:
        """
        Registra un nuevo saldo a favor.

        Args:
            tipo_beneficiario: 'Propietario' o 'Asesor'
            id_beneficiario: ID del propietario o asesor
            valor: Monto del saldo en centavos (> 0)
            motivo: Razón del saldo
            observaciones: Notas adicionales
            usuario: Usuario que registra

        Returns:
            SaldoFavor creado

        Raises:
            ValueError: Si los datos son inválidos
        """
        if tipo_beneficiario not in ["Propietario", "Asesor"]:
            raise ValueError("Tipo de beneficiario debe ser 'Propietario' o 'Asesor'")

        if valor <= 0:
            raise ValueError("El valor del saldo debe ser mayor que cero")

        if not motivo or not motivo.strip():
            raise ValueError("El motivo es obligatorio")

        # Crear entidad según tipo
        saldo = SaldoFavor(
            id_propietario=id_beneficiario if tipo_beneficiario == "Propietario" else None,
            id_asesor=id_beneficiario if tipo_beneficiario == "Asesor" else None,
            tipo_beneficiario=tipo_beneficiario,
            valor_saldo=valor,
            motivo=motivo.strip(),
            fecha_generacion=date.today().isoformat(),
            estado="Pendiente",
            observaciones=observaciones,
        )

        return self.repositorio.crear(saldo, usuario)

    def aplicar_saldo(
        self, id_saldo: int, observacion: Optional[str] = None, usuario: str = "sistema"
    ) -> SaldoFavor:
        """
        Aplica un saldo a una liquidación futura.

        Args:
            id_saldo: ID del saldo a aplicar
            observacion: Nota sobre cómo se aplicó
            usuario: Usuario que aplica

        Returns:
            SaldoFavor actualizado

        Raises:
            ValueError: Si el saldo no existe o ya está resuelto
        """
        saldo = self.repositorio.obtener_por_id(id_saldo)
        if not saldo:
            raise ValueError(f"No se encontró el saldo con ID {id_saldo}")

        if saldo.esta_resuelto:
            raise ValueError(f"El saldo ya está {saldo.estado.lower()}")

        saldo.aplicar(observacion)
        return self.repositorio.actualizar(saldo, usuario)

    def devolver_saldo(
        self, id_saldo: int, observacion: Optional[str] = None, usuario: str = "sistema"
    ) -> SaldoFavor:
        """
        Marca un saldo como devuelto al beneficiario.

        Args:
            id_saldo: ID del saldo a devolver
            observacion: Nota sobre cómo se devolvió
            usuario: Usuario que procesa

        Returns:
            SaldoFavor actualizado

        Raises:
            ValueError: Si el saldo no existe o ya está resuelto
        """
        saldo = self.repositorio.obtener_por_id(id_saldo)
        if not saldo:
            raise ValueError(f"No se encontró el saldo con ID {id_saldo}")

        if saldo.esta_resuelto:
            raise ValueError(f"El saldo ya está {saldo.estado.lower()}")

        saldo.devolver(observacion)
        return self.repositorio.actualizar(saldo, usuario)

    def obtener_saldo(self, id_saldo: int) -> Optional[SaldoFavor]:
        """
        Obtiene un saldo por su ID.
        """
        return self.repositorio.obtener_por_id(id_saldo)

    def listar_saldos(
        self,
        tipo_beneficiario: Optional[str] = None,
        estado: Optional[str] = None,
        id_propietario: Optional[int] = None,
        id_asesor: Optional[int] = None,
    ) -> List[SaldoFavor]:
        """
        Lista saldos a favor con filtros opcionales.

        Args:
            tipo_beneficiario: Filtrar por tipo (Propietario, Asesor)
            estado: Filtrar por estado (Pendiente, Aplicado, Devuelto)
            id_propietario: Filtrar por propietario específico
            id_asesor: Filtrar por asesor específico

        Returns:
            Lista de SaldoFavor
        """
        return self.repositorio.listar_con_filtros(
            tipo_beneficiario=tipo_beneficiario,
            estado=estado,
            id_propietario=id_propietario,
            id_asesor=id_asesor,
        )

    def listar_pendientes(self) -> List[SaldoFavor]:
        """
        Lista todos los saldos pendientes de resolución.
        """
        return self.repositorio.listar_pendientes()

    def obtener_resumen_propietario(self, id_propietario: int) -> Dict[str, Any]:
        """
        Obtiene resumen de saldos para un propietario.

        Args:
            id_propietario: ID del propietario

        Returns:
            Diccionario con total pendiente y lista de saldos
        """
        saldos = self.repositorio.listar_por_propietario(id_propietario)
        total_pendiente = self.repositorio.obtener_total_pendiente_propietario(id_propietario)

        return {
            "id_propietario": id_propietario,
            "total_pendiente": total_pendiente,
            "cantidad_saldos": len(saldos),
            "saldos": saldos,
        }

    def obtener_resumen_asesor(self, id_asesor: int) -> Dict[str, Any]:
        """
        Obtiene resumen de saldos para un asesor.

        Args:
            id_asesor: ID del asesor

        Returns:
            Diccionario con total pendiente y lista de saldos
        """
        saldos = self.repositorio.listar_por_asesor(id_asesor)
        total_pendiente = self.repositorio.obtener_total_pendiente_asesor(id_asesor)

        return {
            "id_asesor": id_asesor,
            "total_pendiente": total_pendiente,
            "cantidad_saldos": len(saldos),
            "saldos": saldos,
        }

    def obtener_resumen_general(self) -> Dict[str, Any]:
        """
        Obtiene resumen general de todos los saldos a favor.

        Returns:
            Diccionario con totales por tipo y estado
        """
        return self.repositorio.obtener_resumen_general()

    def obtener_detalle_para_ui(self, id_saldo: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos completos de un saldo para mostrar en UI.

        Args:
            id_saldo: ID del saldo

        Returns:
            Diccionario con datos del saldo y nombre del beneficiario
        """
        saldo = self.repositorio.obtener_por_id(id_saldo)
        if not saldo:
            return None

        # Obtener nombre del beneficiario
        nombre_beneficiario = "Desconocido"

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()

            if saldo.tipo_beneficiario == "Propietario" and saldo.id_propietario:
                placeholder = self.db_manager.get_placeholder()
                cursor.execute(
                    f"""
                    SELECT p.NOMBRE_COMPLETO 
                    FROM PERSONAS p
                    JOIN PROPIETARIOS pr ON p.ID_PERSONA = pr.ID_PERSONA
                    WHERE pr.ID_PROPIETARIO = {placeholder}
                """,
                    (saldo.id_propietario,),
                )
            elif saldo.tipo_beneficiario == "Asesor" and saldo.id_asesor:
                placeholder = self.db_manager.get_placeholder()
                cursor.execute(
                    f"""
                    SELECT p.NOMBRE_COMPLETO 
                    FROM PERSONAS p
                    JOIN ASESORES a ON p.ID_PERSONA = a.ID_PERSONA
                    WHERE a.ID_ASESOR = {placeholder}
                """,
                    (saldo.id_asesor,),
                )

            row = cursor.fetchone()
            if row:
                nombre_beneficiario = row[0]

        return {
            "saldo": saldo,
            "nombre_beneficiario": nombre_beneficiario,
            "valor_formateado": saldo.valor_formateado,
            "dias_pendiente": saldo.dias_pendiente,
        }

    def eliminar_saldo(self, id_saldo: int, usuario: str = "sistema") -> bool:
        """
        Elimina un saldo a favor (solo si está pendiente).

        Args:
            id_saldo: ID del saldo a eliminar
            usuario: Usuario que elimina

        Returns:
            True si se eliminó

        Raises:
            ValueError: Si el saldo no existe o ya está resuelto
        """
        saldo = self.repositorio.obtener_por_id(id_saldo)
        if not saldo:
            raise ValueError(f"No se encontró el saldo con ID {id_saldo}")

        if saldo.esta_resuelto:
            raise ValueError(f"No se puede eliminar un saldo que ya fue {saldo.estado.lower()}")

        return self.repositorio.eliminar(id_saldo)
