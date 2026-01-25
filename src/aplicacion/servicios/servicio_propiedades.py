"""
Servicio de Aplicación: Gestión de Propiedades
Orquesta operaciones CRUD de Propiedad con filtros avanzados.
"""

import csv
import io
from datetime import datetime
from typing import Dict, List, Optional

from src.dominio.entidades.propiedad import Propiedad
from src.dominio.interfaces.repositorio_propiedad import IRepositorioPropiedad
from src.infraestructura.persistencia.repositorio_municipio_sqlite import (
    RepositorioMunicipioSQLite,
)

# Integración Fase 3: CacheManager
from src.infraestructura.cache.cache_manager import cache_manager


class ServicioPropiedades:
    """
    Servicio de aplicación para gestión integral de Propiedades.
    Implementa lógica de negocio para CRUD con filtros avanzados.
    """

    TIPOS_PROPIEDAD = ["Casa", "Apartamento", "Local Comercial", "Bodega", "Oficina", "Lote"]

    def __init__(
        self,
        repo_propiedad: IRepositorioPropiedad,
        repo_municipio: Optional[RepositorioMunicipioSQLite] = None,
    ):
        self.repo = repo_propiedad
        self.repo_municipio = repo_municipio

    @cache_manager.cached("propiedades:list", level=1)
    def listar_propiedades(
        self,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None,
    ) -> List[Propiedad]:
        """
        Lista propiedades con filtros aplicados.
        """
        return self.repo.listar_con_filtros(
            filtro_tipo=filtro_tipo,
            filtro_disponibilidad=filtro_disponibilidad,
            filtro_municipio=filtro_municipio,
            solo_activas=solo_activas,
            busqueda=busqueda
        )

    @cache_manager.cached("propiedades:list_paginated", level=1, ttl=300)
    def listar_propiedades_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None,
    ):
        """
        Lista propiedades con filtros y paginación.
        """
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams

        params = PaginationParams(page=page, page_size=page_size)

        total = self.repo.contar_con_filtros(
            filtro_tipo=filtro_tipo,
            filtro_disponibilidad=filtro_disponibilidad,
            filtro_municipio=filtro_municipio,
            solo_activas=solo_activas,
            busqueda=busqueda
        )

        items = self.repo.listar_con_filtros(
            filtro_tipo=filtro_tipo,
            filtro_disponibilidad=filtro_disponibilidad,
            filtro_municipio=filtro_municipio,
            solo_activas=solo_activas,
            busqueda=busqueda,
            limit=params.page_size,
            offset=params.offset
        )

        return PaginatedResult(
            items=items, total=total, page=params.page, page_size=params.page_size
        )

    def obtener_propiedad(self, id_propiedad: int) -> Optional[Propiedad]:
        """Obtiene una propiedad por su ID."""
        return self.repo.obtener_por_id(id_propiedad)

    def buscar_por_matricula(self, matricula: str) -> Optional[Propiedad]:
        """Busca una propiedad por su matrícula inmobiliaria."""
        return self.repo.obtener_por_matricula(matricula)

    def crear_propiedad(self, datos: Dict, usuario_sistema: str = "sistema") -> Propiedad:
        """Crea una nueva propiedad."""
        if self.repo.obtener_por_matricula(datos["matricula_inmobiliaria"]):
            raise ValueError(
                f"Ya existe una propiedad con matrícula {datos['matricula_inmobiliaria']}"
            )

        if datos.get("tipo_propiedad") not in self.TIPOS_PROPIEDAD:
            raise ValueError(
                f"Tipo de propiedad inválido. Debe ser uno de: {', '.join(self.TIPOS_PROPIEDAD)}"
            )

        if datos.get("area_m2", 0) <= 0:
            raise ValueError("El área debe ser mayor a 0")

        if datos.get("estrato") and not (1 <= datos["estrato"] <= 6):
            raise ValueError("El estrato debe estar entre 1 y 6")

        propiedad = Propiedad(
            matricula_inmobiliaria=datos["matricula_inmobiliaria"],
            id_municipio=datos["id_municipio"],
            direccion_propiedad=datos["direccion_propiedad"],
            tipo_propiedad=datos["tipo_propiedad"],
            disponibilidad_propiedad=datos.get("disponibilidad_propiedad", 1),
            area_m2=datos["area_m2"],
            habitaciones=datos.get("habitaciones"),
            bano=datos.get("bano"),
            parqueadero=datos.get("parqueadero"),
            estrato=datos.get("estrato"),
            valor_administracion=datos.get("valor_administracion"),
            canon_arrendamiento_estimado=datos.get("canon_arrendamiento_estimado"),
            valor_venta_propiedad=datos.get("valor_venta_propiedad"),
            comision_venta_propiedad=datos.get("comision_venta_propiedad"),
            observaciones_propiedad=datos.get("observaciones_propiedad"),
            codigo_energia=datos.get("codigo_energia"),
            codigo_agua=datos.get("codigo_agua"),
            codigo_gas=datos.get("codigo_gas"),
            telefono_administracion=datos.get("telefono_administracion"),
            tipo_cuenta_administracion=datos.get("tipo_cuenta_administracion"),
            numero_cuenta_administracion=datos.get("numero_cuenta_administracion"),
            fecha_ingreso_propiedad=datos.get("fecha_ingreso_propiedad", datetime.now().date().isoformat()),
            created_at=datetime.now().isoformat(),
            created_by=usuario_sistema,
        )

        result = self.repo.crear(propiedad, usuario_sistema)
        cache_manager.invalidate("propiedades")
        return result

    def actualizar_propiedad(
        self, id_propiedad: int, datos: Dict, usuario_sistema: str = "sistema"
    ) -> Propiedad:
        """Actualiza una propiedad existente."""
        propiedad = self.repo.obtener_por_id(id_propiedad)
        if not propiedad:
            raise ValueError(f"No existe propiedad con ID {id_propiedad}")

        if "tipo_propiedad" in datos and datos["tipo_propiedad"] not in self.TIPOS_PROPIEDAD:
            raise ValueError(
                f"Tipo de propiedad inválido. Debe ser uno de: {', '.join(self.TIPOS_PROPIEDAD)}"
            )

        if "area_m2" in datos and datos["area_m2"] <= 0:
            raise ValueError("El área debe ser mayor a 0")

        if "estrato" in datos and datos["estrato"] and not (1 <= datos["estrato"] <= 6):
            raise ValueError("El estrato debe estar entre 1 y 6")

        # Actualizar campos
        for k, v in datos.items():
            if hasattr(propiedad, k):
                setattr(propiedad, k, v)

        propiedad.updated_at = datetime.now().isoformat()
        propiedad.updated_by = usuario_sistema

        self.repo.actualizar(propiedad, usuario_sistema)
        cache_manager.invalidate("propiedades")

        return propiedad

    def cambiar_disponibilidad(
        self, id_propiedad: int, nueva_disponibilidad: int, usuario_sistema: str = "sistema"
    ) -> bool:
        """Cambia la disponibilidad de una propiedad."""
        propiedad = self.repo.obtener_por_id(id_propiedad)
        if not propiedad:
            return False

        propiedad.disponibilidad_propiedad = nueva_disponibilidad
        propiedad.updated_at = datetime.now().isoformat()
        propiedad.updated_by = usuario_sistema

        result = self.repo.actualizar(propiedad, usuario_sistema)
        if result:
            cache_manager.invalidate("propiedades")
        return result

    def desactivar_propiedad(
        self,
        id_propiedad: int,
        motivo: str = "Desactivado por usuario",
        usuario_sistema: str = "sistema",
    ) -> bool:
        """Inactiva una propiedad (soft delete)."""
        propiedad = self.repo.obtener_por_id(id_propiedad)
        if not propiedad:
            return False

        propiedad.estado_registro = 0
        propiedad.motivo_inactivacion = motivo
        propiedad.updated_at = datetime.now().isoformat()
        propiedad.updated_by = usuario_sistema

        return self.repo.actualizar(propiedad, usuario_sistema)

    def activar_propiedad(self, id_propiedad: int, usuario_sistema: str = "sistema") -> bool:
        """Reactiva una propiedad inactiva."""
        propiedad = self.repo.obtener_por_id(id_propiedad)
        if not propiedad:
            return False

        propiedad.estado_registro = 1
        propiedad.motivo_inactivacion = None
        propiedad.updated_at = datetime.now().isoformat()
        propiedad.updated_by = usuario_sistema

        return self.repo.actualizar(propiedad, usuario_sistema)

    def exportar_propiedades_csv(
        self,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None,
    ) -> str:
        """Genera un CSV con las propiedades filtradas."""
        propiedades = self.repo.listar_con_filtros(
            filtro_tipo=filtro_tipo,
            filtro_disponibilidad=filtro_disponibilidad,
            filtro_municipio=filtro_municipio,
            solo_activas=solo_activas,
            busqueda=busqueda
        )

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "Matrícula", "Tipo", "Municipio ID", "Dirección", "Canon",
                "Area (m2)", "Habitaciones", "Baños", "Parqueaderos", "Estrato", "Disponibilidad",
            ]
        )

        for p in propiedades:
            disponibilidad = "Disponible" if p.disponibilidad_propiedad else "Ocupada"
            writer.writerow(
                [
                    p.matricula_inmobiliaria,
                    p.tipo_propiedad,
                    p.id_municipio,
                    p.direccion_propiedad,
                    f"${p.canon_arrendamiento_estimado or 0:,.0f}",
                    p.area_m2,
                    p.habitaciones,
                    p.bano,
                    p.parqueadero,
                    p.estrato,
                    disponibilidad,
                ]
            )

        return output.getvalue()

    def obtener_municipios_disponibles(self) -> List[Dict]:
        """Obtiene la lista de municipios con estado_registro activo."""
        if not self.repo_municipio:
            from src.infraestructura.persistencia.database import db_manager

            self.repo_municipio = RepositorioMunicipioSQLite(db_manager)

        municipios = self.repo_municipio.listar_todos()
        return [{"id": m.id_municipio, "nombre": m.nombre_municipio} for m in municipios]

    def obtener_tipos_propiedad(self) -> List[str]:
        """Retorna los tipos de propiedad permitidos."""
        return self.TIPOS_PROPIEDAD
