"""
Servicio de Aplicación: Gestión Financiera
Coordina la lógica de negocio para recaudos y liquidaciones.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

from src.dominio.entidades.liquidacion import Liquidacion
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto

from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
from src.dominio.interfaces.repositorio_recaudo import IRepositorioRecaudo
from src.dominio.interfaces.repositorio_liquidacion import IRepositorioLiquidacion
from src.dominio.interfaces.repositorio_propiedad import IRepositorioPropiedad
# Interfaces para contratos se inyectarán después si es posible, por ahora usamos base
# Pero para ser estrictos con Fase 3, el servicio financiero debería recibir interfaces.

from src.infraestructura.cache.cache_manager import cache_manager
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF


class ServicioFinanciero:
    """Servicio para gestión de recaudos y liquidaciones"""

    def __init__(
        self,
        db_manager: Any,
        repo_recaudo: Optional[IRepositorioRecaudo] = None,
        repo_liquidacion: Optional[IRepositorioLiquidacion] = None,
        repo_propiedad: Optional[IRepositorioPropiedad] = None,
        repo_arriendo: Optional[Any] = None,
        repo_mandato: Optional[Any] = None,
        pdf_service: Optional[ServicioDocumentosPDF] = None,
        servicio_configuracion: Optional[ServicioConfiguracion] = None,
    ):
        from src.infraestructura.persistencia.repositorio_recaudo import RepositorioRecaudo
        from src.infraestructura.persistencia.repositorio_liquidacion_postgres import (
            RepositorioLiquidacionPostgres,
        )
        from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
            RepositorioPropiedadPostgres,
        )
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
            RepositorioContratoArrendamientoPostgres,
        )
        from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
            RepositorioContratoMandatoPostgres,
        )
        from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF

        self.repo_recaudo = repo_recaudo or RepositorioRecaudo(db_manager)
        self.repo_liquidacion = (
            repo_liquidacion or RepositorioLiquidacionPostgres(db_manager)
        )
        self.repo_propiedad = repo_propiedad or RepositorioPropiedadPostgres(db_manager)
        self.repo_arriendo = (
            repo_arriendo or RepositorioContratoArrendamientoPostgres(db_manager)
        )
        self.repo_mandato = (
            repo_mandato or RepositorioContratoMandatoPostgres(db_manager)
        )
        self.pdf_service = pdf_service or ServicioDocumentosPDF()
        self.servicio_config = servicio_configuracion

    def registrar_recaudo(
        self,
        datos: Dict[str, Any],
        conceptos_data: List[Dict[str, Any]],
        usuario_sistema: str,
    ) -> Recaudo:
        """DEPRECATED - Usar ServicioRecaudo.registrar_pago() en su lugar.
        Registra un nuevo pago del inquilino."""
        recaudo = Recaudo(
            id_contrato_a=datos["id_contrato_a"],
            fecha_pago=datos["fecha_pago"],
            valor_total=datos["valor_total"],
            metodo_pago=datos["metodo_pago"],
            referencia_bancaria=datos.get("referencia_bancaria"),
            observaciones=datos.get("observaciones"),
        )

        conceptos = [
            RecaudoConcepto(
                tipo_concepto=c["tipo_concepto"], periodo=c["periodo"], valor=c["valor"]
            )
            for c in conceptos_data
        ]

        return self.repo_recaudo.crear(recaudo, conceptos, usuario_sistema)

    def calcular_mora(
        self, id_contrato_a: int, fecha_limite: str, fecha_pago: str, valor_canon: int
    ) -> int:
        """Calcula el valor de mora."""
        fecha_lim = datetime.fromisoformat(fecha_limite)
        fecha_pag = datetime.fromisoformat(fecha_pago)
        dias_mora = (fecha_pag - fecha_lim).days
        if dias_mora <= 0:
            return 0
        tasa_diaria = 0.06 / 365
        return int(valor_canon * tasa_diaria * dias_mora)

    def aplicar_pago_anticipado(
        self,
        id_contrato_a: int,
        meses_adelantados: int,
        valor_canon_mensual: int,
        fecha_pago: str,
        metodo_pago: str,
        referencia_bancaria: Optional[str],
        usuario_sistema: str,
    ) -> Recaudo:
        """Registra un pago anticipado."""
        valor_total = valor_canon_mensual * meses_adelantados
        conceptos_data = []
        fecha_base = datetime.fromisoformat(fecha_pago)

        for i in range(meses_adelantados):
            periodo = (fecha_base + relativedelta(months=i)).strftime("%Y-%m")
            conceptos_data.append(
                {
                    "tipo_concepto": "Canon",
                    "periodo": periodo,
                    "valor": valor_canon_mensual,
                }
            )

        return self.registrar_recaudo(
            datos={
                "id_contrato_a": id_contrato_a,
                "fecha_pago": fecha_pago,
                "valor_total": valor_total,
                "metodo_pago": metodo_pago,
                "referencia_bancaria": referencia_bancaria,
                "observaciones": f"Pago anticipado de {meses_adelantados} meses",
            },
            conceptos_data=conceptos_data,
            usuario_sistema=usuario_sistema,
        )

    def generar_liquidacion_mensual(
        self,
        id_contrato_m: int,
        periodo: str,
        datos_adicionales: Dict[str, Any],
        usuario_sistema: str,
    ) -> Liquidacion:
        """Genera la liquidación mensual."""
        contrato = self.repo_mandato.obtener_por_id(id_contrato_m)
        if not contrato:
            raise ValueError(f"No existe el contrato de mandato con ID {id_contrato_m}")

        existente = self.repo_liquidacion.obtener_por_contrato_y_periodo(
            id_contrato_m, periodo
        )
        if existente:
            raise ValueError(f"Ya existe una liquidación para el período {periodo}")

        canon_bruto = contrato.canon_mandato
        otros_ingresos = datos_adicionales.get("otros_ingresos", 0)
        total_ingresos = canon_bruto + otros_ingresos

        comision_porcentaje = datos_adicionales.get(
            "comision_porcentaje", contrato.comision_porcentaje_contrato_m
        )
        comision_monto = int((canon_bruto * comision_porcentaje) / 10000)

        # Sincronización de Parámetros Globales
        iva_val = 1900
        imp_4x1000_val = 4

        if self.servicio_config:
            iva_val = self.servicio_config.obtener_valor_parametro("IVA_DEFAULT", 1900)
            imp_4x1000_val = self.servicio_config.obtener_valor_parametro(
                "IMPUESTO_4X1000", 4
            )

        iva_comision = int(comision_monto * (iva_val / 10000.0))
        impuesto_4x1000 = 0 # Eliminado por política Elite
        seguro_monto = 0 # Eliminado por política Elite

        # Obtención de Valor Administración desde Propiedad
        valor_admin_propiedad = 0
        try:
            from src.infraestructura.persistencia.database import db_manager

            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)
                placeholder = db_manager.get_placeholder()

                # Obtener propiedad del contrato de mandato
                cursor.execute(
                    f"""
                    SELECT cm.ID_PROPIEDAD, p.VALOR_ADMINISTRACION 
                    FROM CONTRATOS_MANDATOS cm 
                    LEFT JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD 
                    WHERE cm.ID_CONTRATO_M = {placeholder}
                    """,
                    (id_contrato_m,),
                )
                row_prop = cursor.fetchone()

                if row_prop:
                    valor_admin_propiedad = row_prop["VALOR_ADMINISTRACION"] or 0
        except Exception:
            valor_admin_propiedad = 0

        liquidacion = Liquidacion(
            id_contrato_m=id_contrato_m,
            periodo=periodo,
            fecha_generacion=datetime.now().date().isoformat(),
            canon_bruto=canon_bruto,
            otros_ingresos=otros_ingresos,
            comision_porcentaje=comision_porcentaje,
            comision_monto=comision_monto,
            iva_comision=iva_comision,
            impuesto_4x1000=impuesto_4x1000,
            gastos_administracion=datos_adicionales.get(
                "gastos_administracion", valor_admin_propiedad
            ),
            gastos_servicios=datos_adicionales.get("gastos_servicios", 0),
            gastos_reparaciones=datos_adicionales.get("gastos_reparaciones", 0),
            pago_predial=datos_adicionales.get("pago_predial", 0),
            seguro_monto=seguro_monto,
            otros_egresos=datos_adicionales.get("otros_egresos", 0),
            estado_liquidacion="En Proceso",
            observaciones=datos_adicionales.get("observaciones"),
        )
        return self.repo_liquidacion.crear(liquidacion, usuario_sistema)

    def generar_liquidacion_propietario(
        self,
        id_propietario: int,
        periodo: str,
        datos_adicionales_por_contrato: Optional[Dict],
        usuario_sistema: str,
    ) -> int:
        """
        Genera liquidaciones individuales para todos los contratos de mandato activos de un propietario.
        Retorna la cantidad de liquidaciones generadas.
        """
        from src.infraestructura.persistencia.database import db_manager

        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            query = """
            SELECT ID_CONTRATO_M 
            FROM CONTRATOS_MANDATOS
            WHERE ID_PROPIETARIO = %s AND ESTADO_CONTRATO_M = 'ACTIVO'
            """
            cursor.execute(query, (id_propietario,))
            contratos = cursor.fetchall()

        if not contratos:
            return 0

        generadas = 0
        for row in contratos:
            id_contrato_m = row["ID_CONTRATO_M"]
            datos_adicionales = {}
            if (
                datos_adicionales_por_contrato
                and id_contrato_m in datos_adicionales_por_contrato
            ):
                datos_adicionales = datos_adicionales_por_contrato[id_contrato_m]

            try:
                self.generar_liquidacion_mensual(
                    id_contrato_m=id_contrato_m,
                    periodo=periodo,
                    datos_adicionales=datos_adicionales,
                    usuario_sistema=usuario_sistema,
                )
                generadas += 1
            except ValueError:
                pass

        if generadas == 0:
            raise ValueError(
                f"Ya existían liquidaciones para las propiedades de este propietario en el período {periodo}"
            )

        return generadas

    def listar_todas_liquidaciones(self) -> List[Dict[str, Any]]:
        return self.repo_liquidacion.listar_todas()

    def aprobar_liquidacion(self, id_liquidacion: int, usuario_sistema: str) -> None:
        self.repo_liquidacion.aprobar(id_liquidacion, usuario_sistema)

    def aprobar_liquidacion_propietario(
        self, id_propietario: int, periodo: str, usuario_sistema: str
    ) -> int:
        """Aprueba todas las liquidaciones en proceso de un propietario para un periodo."""
        return self.repo_liquidacion.aprobar_por_propietario_y_periodo(
            id_propietario, periodo, usuario_sistema
        )

    def marcar_liquidacion_pagada(
        self,
        id_liquidacion: int,
        fecha_pago: str,
        metodo_pago: str,
        referencia_pago: str,
        usuario_sistema: str,
    ) -> None:
        self.repo_liquidacion.marcar_como_pagada(
            id_liquidacion, fecha_pago, metodo_pago, referencia_pago, usuario_sistema
        )

    def marcar_liquidacion_propietario_pagada(
        self,
        id_propietario: int,
        periodo: str,
        fecha_pago: str,
        metodo_pago: str,
        referencia_pago: str,
        usuario_sistema: str,
    ) -> int:
        """Marca como pagadas todas las liquidaciones aprobadas de un propietario para un periodo."""
        liquidaciones = self.repo_liquidacion.listar_por_propietario_y_periodo(
            id_propietario, periodo
        )
        afectadas = 0
        for liq in liquidaciones:
            if liq.estado_liquidacion == "Aprobada":
                self.repo_liquidacion.marcar_como_pagada(
                    liq.id_liquidacion,
                    fecha_pago,
                    metodo_pago,
                    referencia_pago,
                    usuario_sistema,
                )
                afectadas += 1
        return afectadas

    def cancelar_liquidacion(
        self, id_liquidacion: int, motivo: str, usuario_sistema: str
    ) -> None:
        self.repo_liquidacion.cancelar(id_liquidacion, motivo, usuario_sistema)

    def reversar_liquidacion(self, id_liquidacion: int, usuario_sistema: str) -> None:
        self.repo_liquidacion.reversar(id_liquidacion, usuario_sistema)

    def listar_liquidaciones_pendientes(self) -> List[Liquidacion]:
        """Extraído de repo."""
        # Esta lógica debería estar en el repo, pero como ya existe como método, lo usaremos
        all_aps = self.repo_liquidacion.listar_todas()
        # Nota: listar_todas suele retornar dicts. El servicio original devolvía entidades.
        # Implementaremos un método específico en repo si es necesario.
        return [
            self.repo_liquidacion._row_to_entity(r)
            for r in all_aps
            if r.get("estado") == "Aprobada"
        ]

    def listar_recaudos_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        busqueda: Optional[str] = None,
    ):
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams

        params = PaginationParams(page=page, page_size=page_size)
        total = self.repo_recaudo.contar_con_filtros(
            estado, fecha_desde, fecha_hasta, busqueda
        )
        items = self.repo_recaudo.listar_paginado(
            params.page_size, params.offset, estado, fecha_desde, fecha_hasta, busqueda
        )
        return PaginatedResult(
            items=items, total=total, page=params.page, page_size=params.page_size
        )

    def listar_liquidaciones_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
        id_asesor: Optional[int] = None,
        sort_by: str = "periodo",
        sort_order: str = "desc",
    ):
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams

        params = PaginationParams(page=page, page_size=page_size)
        total = self.repo_liquidacion.contar_con_filtros(
            estado, periodo, busqueda, id_asesor
        )
        items = self.repo_liquidacion.listar_paginado(
            params.page_size, params.offset, estado, periodo, busqueda, id_asesor, sort_by, sort_order
        )
        return PaginatedResult(
            items=items, total=total, page=params.page, page_size=params.page_size
        )

    def obtener_detalle_recaudo_ui(self, id_recaudo: int) -> Optional[Dict[str, Any]]:
        recaudo = self.repo_recaudo.obtener_por_id(id_recaudo)
        if not recaudo:
            return None
        contrato = self.repo_arriendo.obtener_por_id(recaudo.id_contrato_a)
        if not contrato:
            return None
        propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
        conceptos = self.repo_recaudo.obtener_conceptos_por_recaudo(id_recaudo)
        return {
            "id_recaudo": recaudo.id_recaudo,
            "fecha_pago": recaudo.fecha_pago,
            "valor_total": recaudo.valor_total,
            "metodo_pago": recaudo.metodo_pago,
            "referencia_bancaria": recaudo.referencia_bancaria or "N/A",
            "estado_recaudo": recaudo.estado_recaudo,
            "observaciones": recaudo.observaciones or "Sin observaciones",
            "id_contrato_a": recaudo.id_contrato_a,
            "direccion_propiedad": propiedad.direccion_propiedad
            if propiedad
            else "N/A",
            "conceptos": [
                {
                    "tipo_concepto": c.tipo_concepto,
                    "periodo": c.periodo,
                    "valor": c.valor,
                }
                for c in conceptos
            ],
            "created_at": recaudo.created_at,
            "created_by": recaudo.created_by or "Sistema",
        }

    def aprobar_recaudo(self, id_recaudo: int, usuario_sistema: str) -> None:
        """DEPRECATED - Usar ServicioRecaudo.aplicar_pago() en su lugar."""
        self.repo_recaudo.cambiar_estado(id_recaudo, "Aplicado", usuario_sistema)

    def reversar_recaudo(self, id_recaudo: int, usuario_sistema: str) -> None:
        """DEPRECATED - Usar ServicioRecaudo.reversar_pago() en su lugar."""
        self.repo_recaudo.cambiar_estado(id_recaudo, "Reversado", usuario_sistema)

    def listar_liquidaciones_propietarios_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
        id_asesor: Optional[int] = None,
        sort_by: str = "periodo",
        sort_order: str = "desc",
    ):
        """Lista liquidaciones agrupadas por propietario (delegada a repo)."""
        return self.repo_liquidacion.listar_agrupadas_por_propietario_paginado(
            page=page,
            page_size=page_size,
            estado=estado,
            periodo=periodo,
            busqueda=busqueda,
            id_asesor=id_asesor,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def obtener_datos_liquidacion_para_pdf(self, id_liquidacion: int) -> Dict[str, Any]:
        """
        Obtiene datos de liquidación formateados para PDF.
        Delega la consulta al repositorio.
        """
        return self.repo_liquidacion.obtener_datos_para_pdf(id_liquidacion)

    def obtener_detalle_liquidacion_ui(
        self, id_liquidacion: int
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos detallados de una liquidación para mostrar en UI (Modales de Detalle/Edición).
        Reutiliza la lógica de obtención de datos para PDF ya que contiene toda la info necesaria.
        """
        return self.repo_liquidacion.obtener_datos_para_pdf(id_liquidacion)

    def obtener_datos_consolidados_para_pdf(
        self, id_propietario: int, periodo: str
    ) -> Dict[str, Any]:
        """
        Obtiene datos consolidados de estado de cuenta para PDF.
        Delega la consulta al repositorio.
        """
        return self.repo_liquidacion.obtener_consolidado_propietario(
            id_propietario, periodo
        )

    def mapear_consolidado_a_pdf_elite(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapea los datos crudos del consolidado al formato estructurado que espera el template Elite.
        Resuelve el error de validación de campos faltantes (estado_id, inmueble, etc).
        """
        # 1. Construir objeto propietario (nested)
        propietario = {
            "nombre": datos["propietario"],
            "documento": datos["documento"],
            "telefono": datos.get("telefono", "N/A"),
            "email": datos.get("email", "N/A"),
        }

        # 2. Usar primera propiedad como inmueble principal (para el header del PDF)
        propiedades = datos.get("propiedades", [])
        if propiedades:
            primera_prop = propiedades[0]
            inmueble = {
                "direccion": primera_prop["direccion"],
                "tipo": "Propiedad",
                "canon": primera_prop["canon"],
            }
        else:
            inmueble = {"direccion": "N/A", "tipo": "Propiedad", "canon": 0}

        # 3. Formatear detalle de propiedades (lista de filas para la tabla detallada)
        detalle_propiedades = []
        lista_propiedades = []
        
        for idx, prop in enumerate(propiedades, 1):
            prop_id = prop.get("id", idx)
            lista_propiedades.append({"id": prop_id, "direccion": prop["direccion"]})
            
            detalle_propiedades.append({
                "id": prop_id,
                "canon": prop.get("canon", 0) or 0,
                "comision": prop.get("comision_monto", 0) or 0,
                "seguro": prop.get("seguro_monto", 0) or 0,
                "iva": prop.get("iva_comision", 0) or 0,
                "impuesto_4x1000": prop.get("impuesto_4x1000", 0) or 0,
                "admin": prop.get("gastos_admin", 0) or 0,
                "servicios": prop.get("gastos_serv", 0) or 0,
                "predial": prop.get("pago_predial", 0) or 0,
                "incidente": (prop.get("gastos_rep", 0) or 0) + (prop.get("otros_egr", 0) or 0),
                "total": prop.get("neto", 0) or 0
            })

        # 4. Construir resumen financiero consolidado
        resumen = {
            "total_ingresos": datos.get("total_ingresos", 0) or 0,
            "total_egresos": datos.get("total_egresos", 0) or 0,
            "honorarios": datos.get("comision_monto", 0) or 0,
            "otros_descuentos": (datos.get("total_egresos", 0) or 0) - (datos.get("comision_monto", 0) or 0),
            "valor_neto": datos.get("neto_pagar", 0) or 0,
            "cuenta_bancaria": f"{datos.get('banco', 'N/A')} - {datos.get('tipo_cuenta', 'N/A')} {datos.get('cuenta_bancaria', 'N/A')}",
            "fecha_pago": datos.get("fecha_pago", ""),
        }

        # 5. Formato final compatible con EstadoCuentaElite
        # Generar un ID numérico para el documento
        estado_id = abs(hash(f"{datos['propietario']}-{datos['periodo']}")) % 1000000

        return {
            "estado_id": estado_id,
            "propietario": propietario,
            "inmueble": inmueble,
            "periodo": datos["periodo"],
            "fecha_generacion": datos.get("fecha_generacion") or datetime.now().strftime("%Y-%m-%d"),
            "lista_propiedades": lista_propiedades,
            "detalle_propiedades": detalle_propiedades,
            "resumen": resumen,
            "observaciones": datos.get("observaciones"), # Propagación vital
            "empresa": datos.get("empresa", {}),
            "modo": "consolidado"
        }

    def exportar_estados_cuenta_periodo_zip(self, periodo: str) -> str:
        """
        Genera un lote de estados de cuenta consolidados por propietario para un periodo.
        Utiliza el motor Élite y devuelve la ruta al archivo ZIP.
        """
        logger.info(f"Iniciando exportación masiva de estados de cuenta para el periodo: {periodo}")
        
        # 1. Obtener lista de propietarios que tienen liquidaciones en este periodo
        resultado_agrupado = self.listar_liquidaciones_propietarios_paginado(
            page=1,
            page_size=1000, 
            periodo=periodo,
            estado="Todos"
        )
        
        propietarios = resultado_agrupado.items
        if not propietarios:
            raise ValueError(f"No se encontraron liquidaciones para exportar en el periodo {periodo}")
            
        logger.debug(f"Se encontraron {len(propietarios)} propietarios para procesar.")
        
        # 2. Preparar lista de datos para el motor PDF Elite
        lista_datos_pdf = []
        for prop in propietarios:
            try:
                id_propietario = prop["id_propietario"]
                # Obtener el consolidado completo desde el repo
                datos_raw = self.obtener_datos_consolidados_para_pdf(id_propietario, periodo)
                
                if datos_raw:
                    # MAPEO CRÍTICO: Transformar formato legacy a Elite estructurado
                    datos_elite = self.mapear_consolidado_a_pdf_elite(datos_raw)
                    lista_datos_pdf.append(datos_elite)
            except Exception as e:
                logger.error(f"Error preparando datos para propietario {prop.get('propietario')}: {e}")
                
        if not lista_datos_pdf:
            raise ValueError("No se pudieron preparar datos para ninguna liquidación en este periodo.")
            
        # 3. Delegar al Facade para generación masiva con motor Elite
        from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
        # Si self.pdf_service es la Facade, la usamos. Si no, instanciamos una localmente.
        facade = self.pdf_service
        if not isinstance(facade, ServicioPDFFacade):
             facade = ServicioPDFFacade()
             
        zip_path = facade.generar_lote_liquidaciones_elite_zip(
            lista_datos=lista_datos_pdf,
            filename_prefix=f"estados_cuenta_{periodo.replace('-', '_')}"
        )
        
        logger.info(f"Exportación masiva completada exitosamente: {zip_path}")
        return zip_path

    def actualizar_liquidacion(
        self,
        id_liquidacion: int,
        datos_actualizados: Dict[str, Any],
        usuario_sistema: str,
    ) -> None:
        """
        Actualiza los datos variables de una liquidación existente.
        Solo permitido si el estado es 'En Proceso'.
        Re-calcula totales, comisiones e impuestos.
        """
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No existe liquidación con ID {id_liquidacion}")

        if liquidacion.estado_liquidacion != "En Proceso":
            raise ValueError(
                "Solo se pueden editar liquidaciones en estado 'En Proceso'"
            )

        # Actualizar campos editables
        liquidacion.otros_ingresos = datos_actualizados.get(
            "otros_ingresos", liquidacion.otros_ingresos
        )
        liquidacion.gastos_administracion = datos_actualizados.get(
            "gastos_administracion", liquidacion.gastos_administracion
        )
        liquidacion.gastos_servicios = datos_actualizados.get(
            "gastos_servicios", liquidacion.gastos_servicios
        )
        liquidacion.gastos_reparaciones = datos_actualizados.get(
            "gastos_reparaciones", liquidacion.gastos_reparaciones
        )
        liquidacion.pago_predial = datos_actualizados.get(
            "pago_predial", liquidacion.pago_predial
        )
        liquidacion.otros_egresos = datos_actualizados.get(
            "otros_egresos", liquidacion.otros_egresos
        )
        liquidacion.observaciones = datos_actualizados.get(
            "observaciones", liquidacion.observaciones
        )

        # Recalcular valores derivados (Comisión e Impuesto dependen de Ingresos)
        # 1. Total Ingresos
        liquidacion.total_ingresos = (
            liquidacion.canon_bruto + liquidacion.otros_ingresos
        )

        # 2. Impuesto 4x1000 (Forzado a 0 por política Elite)
        liquidacion.impuesto_4x1000 = 0

        # El método repository.actualizar llamará a calcular_totales() para sumar egresos y neto
        self.repo_liquidacion.actualizar(liquidacion, usuario_sistema)
