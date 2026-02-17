from datetime import datetime
from typing import Any, Dict, List, Optional

from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.dominio.entidades.renovacion_contrato import RenovacionContrato
from src.dominio.repositorios.interfaces import (
    RepositorioContratoArrendamiento,
    RepositorioIPC,
    RepositorioPropiedad,
    RepositorioRenovacion,
)
from src.infraestructura.cache.cache_manager import cache_manager


class ServicioContratoArrendamiento:
    """
    Servicio especializado en la gestión de contratos de Arrendamiento (Inquilinos).
    Sigue el Principio de Responsabilidad Única (SRP) y Clean Architecture.
    """

    def __init__(
        self,
        repo_arriendo: RepositorioContratoArrendamiento,
        repo_propiedad: RepositorioPropiedad,
        repo_renovacion: RepositorioRenovacion,
        repo_ipc: RepositorioIPC,
    ):
        self.repo_arriendo = repo_arriendo
        self.repo_propiedad = repo_propiedad
        self.repo_renovacion = repo_renovacion
        self.repo_ipc = repo_ipc

    # =========================================================================
    # HELPERS UI / DROPDOWNS
    # =========================================================================

    def obtener_propiedades_para_arrendamiento(self) -> List[Dict[str, Any]]:
        """Retorna propiedades elegibles para nuevos arrendamientos."""
        rows = self.repo_propiedad.listar_para_arrendamiento()
        return [
            {
                "id": row["ID_PROPIEDAD"],
                "texto": f"{row['MATRICULA_INMOBILIARIA']} - {row['DIRECCION_PROPIEDAD']}",
                "canon": row["CANON_ARRENDAMIENTO_ESTIMADO"],
            }
            for row in rows
        ]

    @cache_manager.invalidates("arriendos:list_paginated")
    def crear_arrendamiento(self, datos: Dict, usuario_sistema: str) -> ContratoArrendamiento:
        """Crea un nuevo contrato de arrendamiento con validaciones."""
        id_propiedad = datos["id_propiedad"]

        # Validar si ya existe arriendo activo
        existente = self.repo_arriendo.obtener_activo_por_propiedad(id_propiedad)
        if existente:
            raise ValueError(
                f"La propiedad ya tiene un contrato de arrendamiento activo (ID: {existente.id_contrato_a})"
            )

        contrato = ContratoArrendamiento(
            id_propiedad=datos["id_propiedad"],
            id_arrendatario=datos["id_arrendatario"],
            id_codeudor=datos.get("id_codeudor"),
            fecha_inicio_contrato_a=datos["fecha_inicio"],
            fecha_fin_contrato_a=datos["fecha_fin"],
            duracion_contrato_a=datos["duracion_meses"],
            canon_arrendamiento=datos["canon"],
            deposito=datos.get("deposito", 0),
            fecha_pago=datos.get("fecha_pago"),
            estado_contrato_a="Activo",
            alerta_vencimiento_contrato_a=True,
            alerta_ipc=True,
        )

        return self.repo_arriendo.crear(contrato, usuario_sistema)

    def obtener_arrendamiento(self, id_contrato: int) -> Optional[ContratoArrendamiento]:
        return self.repo_arriendo.obtener_por_id(id_contrato)

    @cache_manager.invalidates("arriendos:list_paginated")
    def actualizar_arrendamiento(self, id_contrato: int, datos: Dict, usuario_sistema: str) -> None:
        arriendo = self.repo_arriendo.obtener_por_id(id_contrato)
        if not arriendo:
            raise ValueError(f"No existe el contrato de arrendamiento con ID {id_contrato}")

        arriendo.fecha_fin_contrato_a = datos.get("fecha_fin", arriendo.fecha_fin_contrato_a)
        arriendo.canon_arrendamiento = datos.get("canon", arriendo.canon_arrendamiento)
        arriendo.fecha_pago = datos.get("fecha_pago", arriendo.fecha_pago)
        arriendo.updated_by = usuario_sistema
        arriendo.updated_at = datetime.now().isoformat()

        self.repo_arriendo.actualizar(arriendo, usuario_sistema)

    def listar_arrendamientos_paginado(self, **kwargs):
        return self.repo_arriendo.listar_paginado(**kwargs)

    @cache_manager.invalidates("arriendos:list_paginated")
    def renovar_arrendamiento(self, id_contrato: int, usuario_sistema: str) -> ContratoArrendamiento:
        """Lógica de renovación automática con incremento IPC."""
        arriendo = self.repo_arriendo.obtener_por_id(id_contrato)
        if not arriendo or arriendo.estado_contrato_a != "Activo":
            raise ValueError("Contrato no válido para renovación")

        # 1. Calcular nuevas fechas
        fecha_fin_actual = datetime.strptime(arriendo.fecha_fin_contrato_a, "%Y-%m-%d")
        meses_duracion = arriendo.duracion_contrato_a

        # Lógica de suma de meses (simplificada para SRP, reutilizando la existente)
        anio_nuevo = fecha_fin_actual.year + (fecha_fin_actual.month + meses_duracion - 1) // 12
        mes_nuevo = (fecha_fin_actual.month + meses_duracion - 1) % 12 + 1
        
        try:
            nueva_fecha_fin_dt = fecha_fin_actual.replace(year=anio_nuevo, month=mes_nuevo)
        except ValueError:
            # Caso 31 de mes, etc.
            import calendar
            last_day = calendar.monthrange(anio_nuevo, mes_nuevo)[1]
            nueva_fecha_fin_dt = fecha_fin_actual.replace(year=anio_nuevo, month=mes_nuevo, day=last_day)

        nueva_fecha_fin_str = nueva_fecha_fin_dt.strftime("%Y-%m-%d")

        # 2. Calcular incremento IPC si aplica (duración >= 12 meses)
        nuevo_canon = arriendo.canon_arrendamiento
        porcentaje_ipc = 0.0
        motivo_ren = "Prórroga Automática - Sin IPC (< 1 año)"

        if meses_duracion >= 12:
            nuevo_canon, porcentaje_ipc = self._calcular_incremento_ipc(arriendo.canon_arrendamiento)
            motivo_ren = f"Prórroga Automática - Renovación IPC ({porcentaje_ipc}%)"

        # 3. Registrar Renovación
        renovacion = RenovacionContrato(
            id_contrato_a=arriendo.id_contrato_a,
            tipo_contrato="Arrendamiento",
            fecha_inicio_original=arriendo.fecha_inicio_contrato_a,
            fecha_fin_original=arriendo.fecha_fin_contrato_a,
            fecha_fin_renovacion=nueva_fecha_fin_str,
            canon_anterior=arriendo.canon_arrendamiento,
            canon_nuevo=nuevo_canon,
            porcentaje_incremento=int(porcentaje_ipc * 100),
            motivo_renovacion=motivo_ren,
            fecha_renovacion=datetime.now().date().isoformat(),
        )

        self.repo_renovacion.crear(renovacion, usuario_sistema)

        # 4. Actualizar contrato
        arriendo.fecha_fin_contrato_a = nueva_fecha_fin_str
        arriendo.canon_arrendamiento = nuevo_canon
        arriendo.fecha_renovacion_contrato_a = datetime.now().date().isoformat()
        
        self.repo_arriendo.actualizar(arriendo, usuario_sistema)
        return arriendo

    def _calcular_incremento_ipc(self, canon_actual: int) -> tuple[int, float]:
        ipc = self.repo_ipc.obtener_ultimo()
        if not ipc:
            return canon_actual, 0.0
        
        porcentaje = float(ipc.valor_ipc)
        incremento = canon_actual * (porcentaje / 100)
        return int(canon_actual + incremento), porcentaje

    @cache_manager.invalidates("arriendos:list_paginated")
    def terminar_arrendamiento(self, id_contrato: int, motivo: str, usuario_sistema: str) -> None:
        arriendo = self.repo_arriendo.obtener_por_id(id_contrato)
        if not arriendo:
            raise ValueError(f"Contrato {id_contrato} no existe")

        arriendo.estado_contrato_a = "Cancelado"
        arriendo.motivo_cancelacion = motivo
        arriendo.fecha_fin_contrato_a = datetime.now().strftime("%Y-%m-%d")
        
        propiedad = self.repo_propiedad.obtener_por_id(arriendo.id_propiedad)
        if propiedad:
            propiedad.disponibilidad_propiedad = 1 # Libre
            self.repo_propiedad.actualizar(propiedad, usuario_sistema)

        self.repo_arriendo.actualizar(arriendo, usuario_sistema)
