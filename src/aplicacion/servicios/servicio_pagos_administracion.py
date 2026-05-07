"""
Servicio de aplicación: PagosAdministracion.
Gestiona la generación y seguimiento de pagos de administración de PH.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.dominio.entidades.pagos_administracion import PagosAdministracion
from src.dominio.interfaces.repositorio_pagos_admin import IRepositorioPagosAdmin
from src.dominio.excepciones.propiedad_horizontal_error import (
    AdministracionNoConfiguradaError,
)
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.aplicacion.decorators.idempotent import idempotent


class ServicioPagosAdministracion:
    """
    Servicio para gestión de Pagos de Administración.
    Aplica SRP al enfocarse únicamente en el dominio de pagos.
    """

    def __init__(
        self,
        repo_pagos: IRepositorioPagosAdmin,
        repo_idempotencia: Optional[IRepositorioIdempotencia] = None,
    ):
        self.repo_pagos = repo_pagos
        self.repo_idempotencia = repo_idempotencia

    def generar_pagos_mes(self, periodo: str, usuario_sistema: str) -> Dict[str, Any]:
        """
        Genera masivamente los pagos de administración para un periodo dado.
        """
        # Delegar la obtención de elegibles al repositorio
        propiedades_elegibles = self.repo_pagos.obtener_elegibles()

        exitosos = 0
        fallidos = 0
        errores = []

        for prop in propiedades_elegibles:
            try:
                # Verificar si ya existe el pago para evitar duplicados
                existente = self.repo_pagos.obtener_por_propiedad_y_periodo(
                    prop["id_propiedad"], periodo
                )
                if existente:
                    continue

                if (
                    not prop.get("valor_administracion")
                    or prop["valor_administracion"] <= 0
                ):
                    raise AdministracionNoConfiguradaError(prop["id_propiedad"])

                fecha_pago = prop.get("fecha_pago_administracion") or 1

                pago = PagosAdministracion(
                    id_propiedad=prop["id_propiedad"],
                    nombre_propietario=prop["nombre_propietario"],
                    direccion_propiedad=prop["direccion_propiedad"],
                    valor_administracion=Decimal(str(prop["valor_administracion"])),
                    fecha_pago=fecha_pago,
                    link_pago=prop.get("link_pago_administracion"),
                    periodo_pago=periodo,
                    estado_pago="Pendiente",
                )

                self.repo_pagos.crear(pago, usuario_sistema)
                exitosos += 1

            except Exception as e:
                fallidos += 1
                errores.append(f"Propiedad {prop.get('id_propiedad')}: {str(e)}")

        return {
            "periodo": periodo,
            "exitosos": exitosos,
            "fallidos": fallidos,
            "errores": errores,
        }

    def listar_pagos(
        self,
        filtro_periodo: Optional[str] = None,
        filtro_estado: Optional[str] = None,
        filtro_propiedad: Optional[int] = None,
        filtro_nombre: Optional[str] = None,
    ) -> List[PagosAdministracion]:
        return self.repo_pagos.listar(
            filtro_periodo=filtro_periodo,
            filtro_estado=filtro_estado,
            filtro_propiedad=filtro_propiedad,
            filtro_nombre=filtro_nombre,
        )

    @idempotent(key_prefix="pagos_admin:marcar_pagado")
    def marcar_como_pagado(self, id_pago: int, usuario_sistema: str) -> bool:
        return self.repo_pagos.marcar_pagado(id_pago, usuario_sistema)

    def obtener_propiedades_elegibles(self) -> List[Dict[str, Any]]:
        return self.repo_pagos.obtener_elegibles()
