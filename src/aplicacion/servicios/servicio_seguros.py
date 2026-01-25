"""
Servicio de aplicación para gestión de Seguros.
Orquesta la lógica de negocio para seguros de arrendamiento.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.dominio.entidades.poliza import PolizaSeguro
from src.dominio.entidades.seguro import Seguro
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_poliza_sqlite import RepositorioPolizaSQLite
from src.infraestructura.persistencia.repositorio_seguro_sqlite import RepositorioSeguroSQLite


class ServicioSeguros:
    """
    Servicio de aplicación para gestionar seguros.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.repo_seguros = RepositorioSeguroSQLite(db_manager)
        self.repo_polizas = RepositorioPolizaSQLite(db_manager)

    def listar_seguros_activos(self) -> List[Seguro]:
        """
        Lista todos los seguros activos disponibles.

        Returns:
            Lista de seguros activos ordenados por nombre
        """
        return self.repo_seguros.listar_todos(solo_activos=True)

    def listar_seguros(self, solo_activos: Optional[bool] = True) -> List[Seguro]:
        """
        Lista todos los seguros.

        Args:
            solo_activos: Si True, solo retorna seguros activos. Si False, solo inactivos. Si None, retorna todos.

        Returns:
            Lista de seguros
        """
        return self.repo_seguros.listar_todos(solo_activos=solo_activos)

    def obtener_seguro(self, id_seguro: int) -> Optional[Seguro]:
        """
        Obtiene un seguro por su ID.

        Args:
            id_seguro: ID del seguro

        Returns:
            Seguro encontrado o None
        """
        return self.repo_seguros.obtener_por_id(id_seguro)

    def crear_seguro(self, datos: Dict[str, Any], usuario_sistema: str) -> Seguro:
        """
        Crea un nuevo seguro.

        Args:
            datos: Diccionario con datos del seguro
            usuario_sistema: Usuario que realiza la operación

        Returns:
            Seguro creado

        Raises:
            ValueError: Si los datos son inválidos o el seguro ya existe
        """
        # Validar datos obligatorios
        if not datos.get("nombre_seguro"):
            raise ValueError("El nombre del seguro es obligatorio")

        if not isinstance(datos.get("porcentaje_seguro"), int) or datos["porcentaje_seguro"] <= 0:
            raise ValueError("El porcentaje del seguro debe ser un número entero positivo")

        # Verificar que no exista un seguro con el mismo nombre
        seguro_existente = self.repo_seguros.obtener_por_nombre(datos["nombre_seguro"])
        if seguro_existente:
            raise ValueError(f"Ya existe un seguro con el nombre '{datos['nombre_seguro']}'")

        # Crear entidad
        seguro = Seguro(
            id_seguro=None,
            nombre_seguro=datos["nombre_seguro"],
            fecha_inicio_seguro=datos.get("fecha_inicio_seguro"),
            porcentaje_seguro=datos["porcentaje_seguro"],
            estado_seguro=True,  # Activo por defecto
            fecha_ingreso_seguro=datetime.now().date().isoformat(),
            motivo_inactivacion=None,
            created_at=None,
            created_by=None,
            updated_at=None,
            updated_by=None,
        )

        return self.repo_seguros.crear(seguro, usuario_sistema)

    def actualizar_seguro(
        self, id_seguro: int, datos: Dict[str, Any], usuario_sistema: str
    ) -> Seguro:
        """
        Actualiza un seguro existente.

        Args:
            id_seguro: ID del seguro a actualizar
            datos: Diccionario con datos actualizados
            usuario_sistema: Usuario que realiza la operación

        Returns:
            Seguro actualizado

        Raises:
            ValueError: Si el seguro no existe o los datos son inválidos
        """
        seguro = self.repo_seguros.obtener_por_id(id_seguro)
        if not seguro:
            raise ValueError(f"No existe el seguro con ID {id_seguro}")

        # Actualizar campos
        if "nombre_seguro" in datos:
            # Verificar que no exista otro seguro con el mismo nombre
            otro_seguro = self.repo_seguros.obtener_por_nombre(datos["nombre_seguro"])
            if otro_seguro and otro_seguro.id_seguro != id_seguro:
                raise ValueError(f"Ya existe otro seguro con el nombre '{datos['nombre_seguro']}'")
            seguro.nombre_seguro = datos["nombre_seguro"]

        if "fecha_inicio_seguro" in datos:
            seguro.fecha_inicio_seguro = datos["fecha_inicio_seguro"]

        if "porcentaje_seguro" in datos:
            if not isinstance(datos["porcentaje_seguro"], int) or datos["porcentaje_seguro"] <= 0:
                raise ValueError("El porcentaje del seguro debe ser un número entero positivo")
            seguro.porcentaje_seguro = datos["porcentaje_seguro"]

        return self.repo_seguros.actualizar(seguro, usuario_sistema)

    def desactivar_seguro(self, id_seguro: int, motivo: str, usuario_sistema: str) -> bool:
        """
        Desactiva un seguro.

        Args:
            id_seguro: ID del seguro a desactivar
            motivo: Motivo de la desactivación
            usuario_sistema: Usuario que realiza la operación

        Returns:
            True si se desactivó exitosamente

        Raises:
            ValueError: Si el seguro no existe
        """
        seguro = self.repo_seguros.obtener_por_id(id_seguro)
        if not seguro:
            raise ValueError(f"No existe el seguro con ID {id_seguro}")

        if not motivo or not motivo.strip():
            raise ValueError("Debe proporcionar un motivo de desactivación")

        return self.repo_seguros.desactivar(id_seguro, motivo, usuario_sistema)

    def activar_seguro(self, id_seguro: int, usuario_sistema: str) -> bool:
        """
        Reactiva un seguro desactivado.

        Args:
            id_seguro: ID del seguro a activar
            usuario_sistema: Usuario que realiza la operación

        Returns:
            True si se activó exitosamente

        Raises:
            ValueError: Si el seguro no existe
        """
        seguro = self.repo_seguros.obtener_por_id(id_seguro)
        if not seguro:
            raise ValueError(f"No existe el seguro con ID {id_seguro}")

        return self.repo_seguros.activar(id_seguro, usuario_sistema)

    # --- GESTIÓN DE PÓLIZAS ---

    def listar_polizas(self) -> List[PolizaSeguro]:
        """Lista todas las pólizas registradas."""
        return self.repo_polizas.listar_todas()

    def crear_poliza(
        self,
        id_contrato: int,
        id_seguro: int,
        fecha_inicio: str,
        fecha_fin: str,
        numero_poliza: str,
        usuario: str,
    ):
        """Asigna una póliza a un contrato."""
        poliza = PolizaSeguro(
            id_poliza=None,
            id_contrato=id_contrato,
            id_seguro=id_seguro,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            numero_poliza=numero_poliza,
            estado="Activa",
        )
        return self.repo_polizas.crear(poliza, usuario)

    def cambiar_estado_poliza(self, id_poliza: int, nuevo_estado: str, usuario: str):
        """Cambia el estado de una póliza (ej: Cancelada)."""
        self.repo_polizas.actualizar_estado(id_poliza, nuevo_estado, usuario)

    def listar_contratos_candidatos(self):
        """
        Lista contratos de arrendamiento activos para asignarles seguro.
        Helper method para el frontend.
        """
        # Esto podría ir en ServicioContratos, pero por conveniencia de UI lo ponemos aquí o lo llamamos desde la vista
        # Usamos SQL directo por eficiencia para este dropdown
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(
                """
                SELECT 
                    ca.ID_CONTRATO_A, 
                    p.DIRECCION_PROPIEDAD as DIRECCION,
                    per.NOMBRE_COMPLETO as INQUILINO
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                WHERE ca.ESTADO_CONTRATO_A = 'Activo'
            """
            )
            return [dict(row) for row in cursor.fetchall()]
