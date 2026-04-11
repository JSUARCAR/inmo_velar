from typing import List, Dict, Any, Tuple, Optional
from src.infraestructura.persistencia.repositorio_reportes import RepositorioReportes
from src.infraestructura.persistencia.repositorio_persona_sqlite import (
    RepositorioPersonaSQLite,
)
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
    RepositorioPropiedadSQLite,
)
from src.infraestructura.persistencia.database import db_manager


class ServicioReportes:
    """Servicio de aplicación para coordinar la generación de reportes."""

    def __init__(self):
        self.repo_reportes = RepositorioReportes()
        # Nota: Usamos db_manager para mantener compatibilidad con repositorios existentes
        self.repo_personas = RepositorioPersonaSQLite(db_manager)
        self.repo_propiedades = RepositorioPropiedadSQLite(db_manager)

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

        # 1. Reportes de Entidades Base (Uso de repositorios existentes)
        if report_id == "personas":
            solo_activos = (
                True
                if estado == "Activo"
                else (False if estado == "Inactivo" else None)
            )
            rol = filtros.get("rol") if filtros.get("rol") != "Todos" else None

            # Nota: Estos repositorios cargan todo en memoria, se debe mejorar en sus clases base
            personas = self.repo_personas.obtener_todos(
                busqueda=busqueda,
                solo_activos=solo_activos if solo_activos is not None else False,
                filtro_rol=rol,
            )

            if estado == "Inactivo":
                personas = [p for p in personas if not p.estado_registro]
            elif estado == "Activo":
                personas = [p for p in personas if p.estado_registro]

            total = len(personas)
            offset = (pagina - 1) * limite
            paginated = personas[offset : offset + limite]

            data = [self._limpiar_dict(p.__dict__) for p in paginated]
            headers = list(data[0].keys()) if data else []
            return data, headers, total

        if report_id == "propiedades":
            solo_activas = (
                True
                if estado == "Activo"
                else (False if estado == "Inactivo" else None)
            )
            props = self.repo_propiedades.listar_con_filtros(
                busqueda=busqueda, solo_activas=solo_activas
            )
            total = len(props)
            offset = (pagina - 1) * limite
            paginated = props[offset : offset + limite]
            data = [self._limpiar_dict(p.__dict__) for p in paginated]
            headers = list(data[0].keys()) if data else []
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
                if estado == "Activo"
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
            headers = list(data[0].keys()) if data else []
            return data, headers, total

        # 5. Reporte Liquidaciones (Paginación Real en DB)
        if report_id == "liquidaciones":
            asesor_id = None
            if filtros.get("asesor_id") and filtros.get("asesor_id") != "Todos":
                try:
                    asesor_id = int(
                        filtros.get("asesor_id").split("(")[-1].replace(")", "")
                    )
                except:
                    pass

            data, total = self.repo_reportes.obtener_reporte_liquidaciones(
                asesor_id=asesor_id, busqueda=busqueda, page=pagina, limit=limite
            )
            headers = list(data[0].keys()) if data else []
            return data, headers, total

        # 6. Reporte Consolidado (Información financiera y contractual unificada)
        if report_id == "reporte_consolidado":
            # Parsear asesor_id si viene formateado
            asesor_id = None
            if filtros.get("asesor_id") and filtros.get("asesor_id") != "Todos":
                try:
                    asesor_id = int(
                        filtros.get("asesor_id").split("(")[-1].replace(")", "")
                    )
                except:
                    pass

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
            # Headers predefinidos para consistencia
            headers = [
                "TIPO_DOCUMENTO_PROPIETARIO",
                "NUMERO_DOCUMENTO_PROPIETARIO",
                "NOMBRE_COMPLETO_PROPIETARIO",
                "BANCO_PROPIETARIO",
                "NUMERO_CUENTA_PROPIETARIO",
                "TIPO_CUENTA_PROPIETARIO",
                "CONSIGNATARIO_PROPIETARIO",
                "DOCUMENTO_CONSIGNATARIO_PROPIETARIO",
                "TIPO_DOCUMENTO_ARRENDATARIO",
                "NUMERO_DOCUMENTO_ARRENDATARIO",
                "NOMBRE_COMPLETO_ARRENDATARIO",
                "FECHA_INICIO_CONTRATO",
                "ESTADO_CONTRATO",
                "DIRECCION_PROPIEDAD",
                "METODO_PAGO_RECAUDOS",
                "ESTADO_RECAUDO",
                "PERIODO_FACTURADO",
                "NOMBRE_ASESOR",
                "CANON_ARRENDAMIENTO",
                "OTROS_INGRESOS",
                "TOTAL_INGRESOS",
                "COMISION_PORCENTAJE_ASESOR",
                "COMISION_MONTO_ASESOR",
                "IVA_COMISION",
                "IMPUESTO_4X1000",
                "VALOR_ADMINISTRACION_PROPIEDAD",
                "ESTADO_PAGO_ADMINISTRACION",
                "GASTOS_SERVICIOS",
                "GASTOS_REPARACIONES",
                "PAGO_PREDIAL",
                "OTROS_EGRESOS",
                "TOTAL_EGRESOS",
                "NETO_A_PAGAR",
                "ESTADO_LIQUIDACION",
                "FECHA_PAGO",
            ]
            return data, headers, total

        # 6. Reportes Genéricos (Paginación Real en DB)
        table_map = {
            "contratos_mandato": "CONTRATOS_MANDATOS",
            "contratos_arrendamiento": "CONTRATOS_ARRENDAMIENTOS",
            "proveedores": "PROVEEDORES",
            "liquidacion_asesores": "LIQUIDACIONES_ASESORES",
            "desocupaciones": "DESOCUPACIONES",
            "seguros": "SEGUROS",
            "recibos_publicos": "RECIBOS_PUBLICOS",
            "saldos_favor": "SALDOS_FAVOR",
        }
        if report_id in table_map:
            data, total = self.repo_reportes.obtener_reporte_generico(
                tabla=table_map[report_id], busqueda=busqueda, page=pagina, limit=limite
            )
            headers = list(data[0].keys()) if data else []
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
        """Ordena los headers para reportes de roles para mejor legibilidad."""
        if not data:
            return []
        priority = [
            "tipo_documento",
            "numero_documento",
            "nombre_completo",
            "telefono_principal",
            "correo_electronico",
        ]
        all_keys = list(data[0].keys())
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
