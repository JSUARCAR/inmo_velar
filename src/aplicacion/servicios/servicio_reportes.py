from typing import List, Dict, Any, Tuple, Optional
from src.infraestructura.persistencia.repositorio_reportes import RepositorioReportes

# Constante de módulo: headers del Reporte Financiero Consolidado (46 columnas)
# Actualizar aquí si se agregan columnas al SELECT en repositorio_reportes.py
HEADERS_REPORTE_CONSOLIDADO: List[str] = [
    # 1. Claves e IDs
    "ID_CONTRATO_M",
    "ID_PROPIEDAD",
    "ID_LIQUIDACION",
    # 2. Información del Propietario (Datos desde Contrato Mandato)
    "TIPO_DOCUMENTO_PROPIETARIO",
    "NUMERO_DOCUMENTO_PROPIETARIO",
    "NOMBRE_COMPLETO_PROPIETARIO",
    "BANCO_PROPIETARIO",
    "NUMERO_CUENTA_PROPIETARIO",
    "TIPO_CUENTA_PROPIETARIO",
    "CONSIGNATARIO_PROPIETARIO",
    "DOCUMENTO_CONSIGNATARIO_PROPIETARIO",
    # 3. Información del Inmueble y el Mandato
    "DIRECCION_PROPIEDAD",
    "ESTADO_CONTRATO",
    "FECHA_INICIO_CONTRATO",
    "FECHA_FIN_CONTRATO",
    "FECHA_PAGO_CONTRATO",
    "CANON_MANDATO",
    # 4. Información de la Propiedad Horizontal
    "VALOR_ADMIN_PROPIEDAD_BASE",
    "DIA_PAGO_ADMIN",
    "LINK_PAGO_ADMIN",
    "CUOTA_EXTRA",
    "OBSERVACIONES_ADMIN_PH",
    "ESTADO_PAGO_ADMINISTRACION",
    # 5. Información del Arrendatario y su Contrato
    "ESTADO_ARRIENDO",
    "NUMERO_DOCUMENTO_ARRENDATARIO",
    "NOMBRE_COMPLETO_ARRENDATARIO",
    "NOMBRE_COMPLETO_HABITANTE",
    # 6. Recaudos y Gestión Comercial
    "METODO_PAGO_RECAUDOS",
    "PERIODO_FACTURADO",
    "NOMBRE_ASESOR",
    # 7. Composición Financiera (Ingresos)
    "OTROS_INGRESOS",
    "TOTAL_INGRESOS",
    # 8. Composición Financiera (Egresos y Retenciones)
    "COMISION_PORCENTAJE_ASESOR",
    "COMISION_MONTO_ASESOR",
    "IVA_COMISION",
    "GASTOS_ADMINISTRACION",
    "GASTOS_SERVICIOS",
    "GASTOS_REPARACIONES",
    "PAGO_PREDIAL",
    "OTROS_EGRESOS",
    "TOTAL_EGRESOS",
    # 9. Cierre Financiero (Liquidación)
    "NETO_A_PAGAR",
    "ESTADO_LIQUIDACION",
    "FECHA_PAGO",
    "PERIODO",
    "ESTADO_RECAUDO",
]


class ServicioReportes:
    """Servicio de aplicación para coordinar la generación de reportes."""

    def __init__(self):
        self.repo_reportes = RepositorioReportes()

    @staticmethod
    def _parsear_asesor_id(texto: Optional[str]) -> Optional[int]:
        """Parsea el formato 'Nombre Asesor (id)' retornando el id entero.

        Args:
            texto: String con el formato 'Nombre (id)' o None.

        Returns:
            Entero con el ID del asesor, o None si no aplica.
        """
        if not texto or texto == "Todos":
            return None
        try:
            return int(texto.split("(")[-1].replace(")", "").strip())
        except ValueError:
            return None

    def _extraer_headers_seguro(
        self, data: List[Dict[str, Any]], fallback: List[str] = []
    ) -> List[str]:
        """Extrae las llaves del primer registro de forma segura (Blindaje Élite)."""
        if data and len(data) > 0 and hasattr(data[0], "keys"):
            return list(data[0].keys())
        return fallback

    async def obtener_datos_reporte(
        self,
        report_id: str,
        filtros: Dict[str, Any],
        pagina: int = 1,
        limite: int = 20,
        es_exportacion: bool = False,
    ) -> Tuple[List[Dict[str, Any]], List[str], int]:
        """
        Orquestador principal de datos para reportes.
        Retorna: (datos, headers, total_count)
        """
        if es_exportacion:
            pagina = 1
            limite = 50000  # Límite de seguridad para exportación

        busqueda = filtros.get("busqueda")
        estado = filtros.get("estado", "Todos")

        # 1. Reportes de Entidades Base (Paginación real en PostgreSQL)
        if report_id == "personas":
            solo_activos: Optional[bool] = (
                True
                if estado == "ACTIVO"
                else (False if estado == "Inactivo" else None)
            )
            filtro_rol = filtros.get("rol") if filtros.get("rol") != "Todos" else None
            data, total = self.repo_reportes.obtener_reporte_personas(
                busqueda=busqueda,
                solo_activos=solo_activos,
                filtro_rol=filtro_rol,
                page=pagina,
                limit=limite,
            )
            headers = self._extraer_headers_seguro(
                data,
                [
                    "ID_PERSONA",
                    "TIPO_DOCUMENTO",
                    "NUMERO_DOCUMENTO",
                    "NOMBRE_COMPLETO",
                    "TELEFONO_PRINCIPAL",
                    "CORREO_ELECTRONICO",
                    "DIRECCION_PRINCIPAL",
                    "ESTADO_REGISTRO",
                ],
            )
            return data, headers, total

        if report_id == "propiedades":
            solo_activas: Optional[bool] = (
                True
                if estado == "ACTIVO"
                else (False if estado == "Inactivo" else None)
            )
            data, total = self.repo_reportes.obtener_reporte_propiedades(
                busqueda=busqueda,
                solo_activas=solo_activas,
                page=pagina,
                limit=limite,
            )
            headers = self._extraer_headers_seguro(
                data,
                [
                    "ID_PROPIEDAD",
                    "MATRICULA_INMOBILIARIA",
                    "DIRECCION_PROPIEDAD",
                    "TIPO_PROPIEDAD",
                    "AREA_M2",
                    "HABITACIONES",
                    "ESTRATO",
                    "VALOR_ADMINISTRACION",
                    "CANON_ARRENDAMIENTO_ESTIMADO",
                    "DISPONIBILIDAD_PROPIEDAD",
                    "ESTADO_REGISTRO",
                ],
            )
            return data, headers, total

        # 2. Reportes de Roles (Paginación Real en DB)
        role_map = {
            "reporte_propietarios": "PROPIETARIOS",
            "reporte_arrendatarios": "ARRENDATARIOS",
            "reporte_codeudores": "CODEUDORES",
            "reporte_asesores": "ASESORES",
        }
        if report_id in role_map:
            solo_activos = (
                True
                if estado == "ACTIVO"
                else (False if estado == "Inactivo" else True)
            )
            data, total = self.repo_reportes.obtener_reporte_roles(
                role_table=role_map[report_id],
                busqueda=busqueda,
                solo_activos=solo_activos,
                page=pagina,
                limit=limite,
            )
            headers = self._definir_headers_roles(data)
            return data, headers, total

        # 3. Reporte Recaudos (Paginación Real en DB)
        if report_id == "recaudos":
            data, total = self.repo_reportes.obtener_reporte_recaudos(
                estado=filtros.get("estado_recaudo"),
                metodo_pago=filtros.get("metodo_pago"),
                periodo_inicio=filtros.get("periodo_inicio"),
                periodo_fin=filtros.get("periodo_fin"),
                busqueda=busqueda,
                page=pagina,
                limit=limite,
            )
            headers = [
                "ID_RECAUDO",
                "ID_CONTRATO_A",
                "DIRECCION_INMUEBLE",
                "MATRICULA",
                "NOMBRE_ARRENDATARIO",
                "TELEFONO_ARRENDATARIO",
                "EMAIL_ARRENDATARIO",
                "FECHA_PAGO",
                "VALOR_TOTAL",
                "METODO_PAGO",
                "REFERENCIA_BANCARIA",
                "ESTADO_RECAUDO",
                "PERIODO_FACTURADO",
                "OBSERVACIONES",
                "CREATED_AT",
            ]
            return data, headers, total

        # 4. Reporte Incidentes (Enriquecido)
        if report_id == "incidentes":
            data, total = self.repo_reportes.obtener_reporte_incidentes_enriquecido(
                estado=estado, busqueda=busqueda, page=pagina, limit=limite
            )
            headers = self._extraer_headers_seguro(data)
            return data, headers, total

        # 5. Reporte Liquidaciones (Propietarios)
        if report_id == "liquidaciones":
            asesor_id = self._parsear_asesor_id(filtros.get("asesor_id"))
            data, total = self.repo_reportes.obtener_reporte_liquidaciones(
                asesor_id=asesor_id, busqueda=busqueda, page=pagina, limit=limite
            )
            headers = self._extraer_headers_seguro(data)
            return data, headers, total

        # 5.1 Reporte Liquidación Asesores (Especializado)
        if report_id == "liquidacion_asesores":
            asesor_id = self._parsear_asesor_id(filtros.get("asesor_id"))
            data, total = self.repo_reportes.obtener_reporte_liquidaciones_asesores(
                asesor_id=asesor_id, busqueda=busqueda, page=pagina, limit=limite
            )
            headers = self._extraer_headers_seguro(data)
            return data, headers, total

        # 6. Reporte Consolidado (Información financiera y contractual unificada)
        if report_id == "reporte_consolidado":
            asesor_id = self._parsear_asesor_id(filtros.get("asesor_id"))
            data, total = self.repo_reportes.obtener_reporte_consolidado(
                fecha_pago_inicio=filtros.get("fecha_pago_inicio"),
                fecha_pago_fin=filtros.get("fecha_pago_fin"),
                periodo_inicio=filtros.get("periodo_inicio"),
                periodo_fin=filtros.get("periodo_fin"),
                estado_contrato=filtros.get("estado_contrato"),
                estado_liquidacion=filtros.get("estado_liquidacion"),
                asesor_id=asesor_id,
                propietario_buscar=filtros.get("propietario_buscar"),
                busqueda=busqueda,
                page=pagina,
                limit=limite,
            )
            # Extraer headers dinámicamente si hay datos para evitar desincronización con el repositorio
            headers = self._extraer_headers_seguro(data, HEADERS_REPORTE_CONSOLIDADO)
            return data, headers, total

        # 6.5 Reportes Enriquecidos de Contratos
        if report_id == "contratos_mandato":
            data, total = self.repo_reportes.obtener_reporte_contratos_mandato(
                busqueda=busqueda, page=pagina, limit=limite
            )
            headers = self._extraer_headers_seguro(data)
            return data, headers, total

        if report_id == "contratos_arrendamiento":
            data, total = self.repo_reportes.obtener_reporte_contratos_arrendamiento(
                busqueda=busqueda, page=pagina, limit=limite
            )
            headers = self._extraer_headers_seguro(data)
            return data, headers, total

        # 7. Reportes Genéricos (Paginación Real en DB)
        table_map = {
            "personas_raw": "PERSONAS",
            "proveedores": "PROVEEDORES",
            "desocupaciones": "DESOCUPACIONES",
            "seguros": "SEGUROS",
            "recibos_publicos": "RECIBOS_PUBLICOS",
            "saldos_favor": "SALDOS_FAVOR",
        }
        if report_id in table_map:
            data, total = self.repo_reportes.obtener_reporte_generico(
                tabla=table_map[report_id], busqueda=busqueda, page=pagina, limit=limite
            )
            headers = self._extraer_headers_seguro(data)
            return data, headers, total

        return [], [], 0

    def obtener_asesores_filtro(self) -> List[str]:
        """Obtiene opciones formateadas para el dropdown de asesores."""
        rows = self.repo_reportes.obtener_lista_asesores()
        return ["Todos"] + [f"{r['NOMBRE_COMPLETO']} ({r['ID_ASESOR']})" for r in rows]

    def _limpiar_dict(self, d: Dict) -> Dict:
        """Limpia metadatos de SQLAlchemy/DB."""
        return {k: v for k, v in d.items() if not k.startswith("_")}

    def _definir_headers_roles(self, data: List[Dict]) -> List[str]:
        """Ordena los headers para reportes de roles para mejor legibilidad (Blindaje Élite)."""
        if not data or len(data) == 0:
            return []

        priority = [
            "tipo_documento",
            "numero_documento",
            "nombre_completo",
            "telefono_principal",
            "correo_electronico",
        ]

        # Acceso seguro al primer registro
        first_row = data[0]
        if not hasattr(first_row, "keys"):
            return []

        all_keys = list(first_row.keys())
        headers = []

        # Encontrar nombres exactos (respetando case-sensitivity del driver)
        for p in priority:
            found = next((k for k in all_keys if k.lower() == p), None)
            if found:
                headers.append(found)

        for k in all_keys:
            if k not in headers and not k.startswith("_"):
                headers.append(k)
        return headers
