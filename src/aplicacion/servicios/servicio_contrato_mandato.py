from datetime import datetime
from typing import Any, Dict, List, Optional

from src.dominio.entidades.contrato_mandato import ContratoMandato
from src.dominio.entidades.renovacion_contrato import RenovacionContrato
from src.dominio.repositorios.interfaces import (
    RepositorioContratoMandato,
    RepositorioPropiedad,
    RepositorioRenovacion,
)
from src.infraestructura.cache.cache_manager import cache_manager


class ServicioContratoMandato:
    """
    Servicio especializado en la gestión de contratos de Mandato (Propietarios).
    Sigue el Principio de Responsabilidad Única (SRP).
    """

    def __init__(
        self,
        repo_mandato: RepositorioContratoMandato,
        repo_propiedad: RepositorioPropiedad,
        repo_renovacion: RepositorioRenovacion,
    ):
        self.repo_mandato = repo_mandato
        self.repo_propiedad = repo_propiedad
        self.repo_renovacion = repo_renovacion

    # =========================================================================
    # HELPERS UI / DROPDOWNS
    # =========================================================================

    def obtener_propiedades_sin_mandato_activo(self) -> List[Dict[str, Any]]:
        """Retorna propiedades elegibles para nuevos mandatos."""
        rows = self.repo_propiedad.listar_sin_mandato()
        return [
            {
                "id": row["ID_PROPIEDAD"],
                "texto": f"{row['MATRICULA_INMOBILIARIA']} - {row['DIRECCION_PROPIEDAD']}",
                "canon": row["CANON_ARRENDAMIENTO_ESTIMADO"],
            }
            for row in rows
        ]

    @cache_manager.invalidates("mandatos:list_paginated")
    def crear_mandato(self, datos: Dict, usuario_sistema: str) -> ContratoMandato:
        """Crea un nuevo contrato de mandato con validaciones de negocio."""
        id_propiedad = datos["id_propiedad"]

        # 1. Validar que no exista otro mandato activo
        existente = self.repo_mandato.obtener_activo_por_propiedad(id_propiedad)
        if existente:
            raise ValueError(
                f"La propiedad ya tiene un contrato de mandato activo (ID: {existente.id_contrato_m})"
            )

        # 2. Crear Entidad
        contrato = ContratoMandato(
            id_propiedad=datos["id_propiedad"],
            id_propietario=datos["id_propietario"],
            id_asesor=datos["id_asesor"],
            fecha_inicio_contrato_m=datos["fecha_inicio"],
            fecha_fin_contrato_m=datos["fecha_fin"],
            duracion_contrato_m=datos["duracion_meses"],
            canon_mandato=datos["canon"],
            comision_porcentaje_contrato_m=datos["comision_porcentaje"],
            iva_contrato_m=datos.get("iva_porcentaje", 1900),
            estado_contrato_m="Activo",
            alerta_vencimiento_contrato_m=True,
            fecha_pago=datos.get("fecha_pago"),
        )

        return self.repo_mandato.crear(contrato, usuario_sistema)

    def obtener_mandato(self, id_contrato: int) -> Optional[ContratoMandato]:
        return self.repo_mandato.obtener_por_id(id_contrato)

    @cache_manager.invalidates("mandatos:list_paginated")
    def actualizar_mandato(self, id_contrato: int, datos: Dict, usuario_sistema: str) -> None:
        """Actualiza condiciones de un mandato."""
        mandato = self.repo_mandato.obtener_por_id(id_contrato)
        if not mandato:
            raise ValueError(f"No existe el contrato de mandato con ID {id_contrato}")

        # Update fields
        mandato.id_propiedad = datos.get("id_propiedad", mandato.id_propiedad)
        mandato.id_propietario = datos.get("id_propietario", mandato.id_propietario)
        mandato.id_asesor = datos.get("id_asesor", mandato.id_asesor)
        mandato.fecha_inicio_contrato_m = datos.get("fecha_inicio", mandato.fecha_inicio_contrato_m)
        mandato.fecha_fin_contrato_m = datos.get("fecha_fin", mandato.fecha_fin_contrato_m)
        mandato.duracion_contrato_m = datos.get("duracion_meses", mandato.duracion_contrato_m)
        mandato.canon_mandato = datos.get("canon", mandato.canon_mandato)
        mandato.comision_porcentaje_contrato_m = datos.get(
            "comision_porcentaje", mandato.comision_porcentaje_contrato_m
        )
        mandato.fecha_pago = datos.get("fecha_pago", mandato.fecha_pago)

        mandato.updated_by = usuario_sistema
        mandato.updated_at = datetime.now().isoformat()

        self.repo_mandato.actualizar(mandato, usuario_sistema)

    def listar_mandatos_paginado(self, **kwargs):
        """Delega el listado al repositorio (Inyección de Infraestructura)."""
        return self.repo_mandato.listar_paginado(**kwargs)

    @cache_manager.invalidates("mandatos:list_paginated")
    def terminar_mandato(self, id_contrato: int, motivo: str, usuario_sistema: str) -> None:
        """Finaliza un contrato de mandato."""
        if not motivo:
            raise ValueError("El motivo de terminación es obligatorio")

        mandato = self.repo_mandato.obtener_por_id(id_contrato)
        if not mandato:
            raise ValueError(f"Contrato {id_contrato} no existe")

        mandato.estado_contrato_m = "Cancelado"
        mandato.motivo_cancelacion = motivo
        mandato.fecha_fin_contrato_m = datetime.now().strftime("%Y-%m-%d")
        mandato.updated_by = usuario_sistema
        mandato.updated_at = datetime.now().isoformat()

        self.repo_mandato.actualizar(mandato, usuario_sistema)
