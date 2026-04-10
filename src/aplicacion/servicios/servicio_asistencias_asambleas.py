"""
Servicio de aplicación: AsistenciasAsambleas.
Gestiona el seguimiento de asistencia a asambleas de copropiedades.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.dominio.entidades.asistencia_asambleas import AsistenciaAsambleas
from src.dominio.interfaces.repositorio_asistencia import IRepositorioAsistencia
from src.dominio.excepciones.propiedad_horizontal_error import PropiedadSinContratoError
from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
    RepositorioPropiedadPostgres,
)


class ServicioAsistenciasAsambleas:
    """
    Servicio para gestión de Asistencia a Asambleas.
    Aplica SRP al enfocarse únicamente en el dominio de asambleas.
    """

    COSTO_ASISTENTE_INMOBILIARIA = 50000

    def __init__(
        self,
        repo_asistencia: IRepositorioAsistencia,
        repo_propiedad: RepositorioPropiedadPostgres,
    ):
        self.repo_asistencia = repo_asistencia
        self.repo_propiedad = repo_propiedad

    def crear_asistencia(
        self, datos: Dict[str, Any], usuario_sistema: str
    ) -> AsistenciaAsambleas:
        """
        Crea una nueva asistencia validando precondiciones de contrato.
        """
        # Validar campos requeridos
        campos_requeridos = [
            "id_propiedad",
            "fecha_asistencia",
            "hora_asistencia",
            "tipo_reunion",
            "tipo_asistente",
            "direccion_asistencia",
        ]
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                raise ValueError(f"Campo requerido faltante o vacío: {campo}")

        id_propiedad = datos["id_propiedad"]
        tipo_asistente = datos["tipo_asistente"]

        # DIP: Delegar la obtención de info al repositorio de propiedad
        info_propiedad = self.repo_propiedad.obtener_info_completa_contrato(
            id_propiedad
        )

        if not info_propiedad:
            raise PropiedadSinContratoError(id_propiedad)

        costo = (
            Decimal("0")
            if tipo_asistente == "Propietario"
            else Decimal(str(self.COSTO_ASISTENTE_INMOBILIARIA))
        )

        id_asistente_persona = (
            info_propiedad["id_propietario"]
            if tipo_asistente == "Propietario"
            else info_propiedad["id_asesor"]
        )

        asistencia = AsistenciaAsambleas(
            id_propiedad=id_propiedad,
            fecha_asistencia=datos["fecha_asistencia"],
            hora_asistencia=datos["hora_asistencia"],
            tipo_reunion=datos["tipo_reunion"],
            tipo_asistente=tipo_asistente,
            costo_asistente=costo,
            id_asistente_persona=id_asistente_persona,
            direccion_asistencia=datos["direccion_asistencia"],
            estado_asistencia="Programada",
        )

        return self.repo_asistencia.crear(asistencia, usuario_sistema)

    def obtener_asistencia(self, id_asistencia: int) -> Optional[AsistenciaAsambleas]:
        return self.repo_asistencia.obtener_por_id(id_asistencia)

    def listar_asistencias(
        self,
        filtro_estado: Optional[str] = None,
        filtro_fecha_desde: Optional[str] = None,
        filtro_fecha_hasta: Optional[str] = None,
    ) -> List[AsistenciaAsambleas]:
        return self.repo_asistencia.listar_todas(
            filtro_estado=filtro_estado,
            filtro_fecha_desde=filtro_fecha_desde,
            filtro_fecha_hasta=filtro_fecha_hasta,
        )

    def actualizar_estado(
        self, id_asistencia: int, nuevo_estado: str, usuario_sistema: str
    ) -> bool:
        return self.repo_asistencia.actualizar_estado(
            id_asistencia, nuevo_estado, usuario_sistema
        )

    def eliminar_asistencia(self, id_asistencia: int) -> bool:
        return self.repo_asistencia.eliminar(id_asistencia)

    def listar_asistencias_por_mes(
        self,
        año: int,
        mes: int,
    ) -> List[AsistenciaAsambleas]:
        return self.repo_asistencia.listar_por_mes(año, mes)

    def listar_asistencias_enriquecidas(
        self,
        filtro_estado: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Lista asistencias con datos enriquecidos (dirección, propietario, asesor)
        resueltos vía JOIN en el repositorio.

        Returns:
            Lista de dicts con claves: entidad, direccion_propiedad,
            nombre_propietario, nombre_asesor.
        """
        return self.repo_asistencia.listar_todas_enriquecidas(
            filtro_estado=filtro_estado,
        )

    def obtener_calendario_mes_enriquecido(
        self,
        año: int,
        mes: int,
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Obtiene asambleas agrupadas por día con datos enriquecidos vía JOIN.

        Returns:
            Dict[dia, List[dict]] con datos completos por día.
        """
        registros = self.repo_asistencia.listar_por_mes_enriquecidas(año, mes)

        eventos_por_día: Dict[int, List[Dict[str, Any]]] = {}
        for registro in registros:
            entidad = registro["entidad"]
            try:
                if hasattr(entidad.fecha_asistencia, "day"):
                    día = entidad.fecha_asistencia.day
                else:
                    día = int(str(entidad.fecha_asistencia).split("/")[0])
                if día not in eventos_por_día:
                    eventos_por_día[día] = []
                eventos_por_día[día].append(registro)
            except (ValueError, IndexError, AttributeError):
                continue

        return eventos_por_día

    def obtener_calendario_mes(
        self,
        año: int,
        mes: int,
        filtro_estado: Optional[str] = None,
    ) -> Dict[int, List[AsistenciaAsambleas]]:
        asistencia = self.repo_asistencia.listar_por_mes(año, mes)

        eventos_por_día: Dict[int, List[AsistenciaAsambleas]] = {}
        for a in asistencia:
            if filtro_estado and a.estado_asistencia != filtro_estado:
                continue
            try:
                if hasattr(a.fecha_asistencia, "day"):
                    día = a.fecha_asistencia.day
                else:
                    día = int(str(a.fecha_asistencia).split("/")[0])
                if día not in eventos_por_día:
                    eventos_por_día[día] = []
                eventos_por_día[día].append(a)
            except (ValueError, IndexError, AttributeError):
                continue

        return eventos_por_día

