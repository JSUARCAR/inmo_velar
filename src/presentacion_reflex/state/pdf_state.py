"""
PDF State para Integracin con Reflex
=====================================
Estado de Reflex para manejar generacin de PDFs desde la UI.

Autor: Sistema de Gestin Inmobiliaria
Fecha: 2026-01-18
"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import reflex as rx
import rxconfig

# Importar facade
from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade

# Configurar logger lite
logger = logging.getLogger("PDFElite")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("\n[SEARCH] [PDF-ELITE] %(asctime)s - %(levelname)s\n%(message)s\n")
    )
    logger.addHandler(handler)


# ========================================================================
# SERVICIO PDF SINGLETON (Module Level)
# ========================================================================
_pdf_service_instance: Optional[ServicioPDFFacade] = None


def get_pdf_service() -> ServicioPDFFacade:
    """Obtiene instancia del servicio PDF (singleton a nivel de mdulo)"""
    global _pdf_service_instance
    if _pdf_service_instance is None:
        _pdf_service_instance = ServicioPDFFacade()
    return _pdf_service_instance


class PDFState(rx.State):
    """
    Estado para manejo de PDFs en Reflex
    """

    # Estado
    generating: bool = False
    last_pdf_path: str = ""
    error_message: str = ""
    success_message: str = ""
    
    @rx.event
    def descargar_pdf_script(self, pdf_path: str):
        """Script del lado del cliente para descargar el PDF."""
        import rxconfig
        from pathlib import Path
        
        filename = Path(pdf_path).name
        # Fallback para desarrollo local si api_url no está configurado correctamente
        api_url = rxconfig.api_url if rxconfig.api_url else "http://127.0.0.1:8000"
        
        logger.debug(f"[DOWNLOAD-SCRIPT] Iniciando para: {filename}")
        logger.debug(f"[DOWNLOAD-SCRIPT] API URL: {api_url}")

        # Preparar script de descarga


        return rx.call_script(
            f"""
            (async () => {{
                const filename = "{filename}";
                const apiUrl = "{api_url}";
                
                console.log("[PDF] Intentando descargar:", filename, "desde:", apiUrl);
                
                try {{
                    const downloadUrl = `${{apiUrl}}/api/pdf/download/${{filename}}`;
                    const res = await fetch(downloadUrl, {{
                        credentials: 'include'
                    }});
                    
                    if (!res.ok) {{
                        const errorText = await res.text();
                        console.error("[PDF] Error en descarga:", res.status, errorText);
                        alert(`Error al descargar PDF (${{res.status}}): ${{errorText}}`);
                        return;
                    }}
                    
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    console.log("[PDF] Descarga iniciada exitosamente");
                }} catch (err) {{
                    console.error("[PDF] Error critico en script de descarga:", err);
                    alert("Error crítico al procesar la descarga del PDF. Revise la consola.");
                }}
            }})();
            """
        )

    # ========================================================================
    # EVENT HANDLERS - DOCUMENTOS LEGACY
    # ========================================================================

    def generar_comprobante_recaudo(self, datos: Dict[str, Any]):
        """
        Genera comprobante de recaudo (legacy)

        Args:
            datos: Datos del comprobante
        """
        self.generating = True
        self.error_message = ""
        self.success_message = ""

        try:
            pdf_path = get_pdf_service().generar_comprobante_recaudo(datos)
            self.last_pdf_path = pdf_path
            self.success_message = f"Comprobante generado: {Path(pdf_path).name}"

            # ESTRATEGIA LITE: Fetch + Blob URL
            # Esto evita problemas de navegacin cross-origin y garantiza la descarga
            return self.descargar_pdf_script(pdf_path)

        except Exception as e:
            self.error_message = f"Error generando comprobante: {str(e)}"
            return rx.toast.error(self.error_message)
        finally:
            self.generating = False

    def generar_estado_cuenta_propietario(self, datos: Dict[str, Any]):
        """
        Genera estado de cuenta de propietario (legacy)

        Args:
            datos: Datos del estado de cuenta
        """
        self.generating = True
        self.error_message = ""

        try:
            pdf_path = get_pdf_service().generar_estado_cuenta(datos)
            self.last_pdf_path = pdf_path
            self.success_message = f"Estado de cuenta generado: {Path(pdf_path).name}"

            # ESTRATEGIA LITE: Fetch + Blob URL
            return self.descargar_pdf_script(pdf_path)

        except Exception as e:
            self.error_message = f"Error generando estado de cuenta: {str(e)}"
            return rx.toast.error(self.error_message)
        finally:
            self.generating = False

    # ========================================================================
    # EVENT HANDLERS - DOCUMENTOS LITE
    # ========================================================================

    @rx.event
    def generar_contrato_oficial_elite(
        self, contrato_id: int, tipo_contrato: str, es_borrador: bool = False
    ):
        """
        Punto de entrada seguro para evitar colisiones de eventos en Reflex (rx.cond en lambdas).

        Args:
            contrato_id: ID del contrato
            tipo_contrato: 'Mandato' o 'Arrendamiento'
            es_borrador: Si es formato borrador u oficial
        """
        if tipo_contrato == "Mandato":
            return PDFState.generar_contrato_mandato_elite(contrato_id, es_borrador)
        else:
            return PDFState.generar_contrato_arrendamiento_elite(
                contrato_id, es_borrador
            )

    @rx.event
    def generar_contrato_arrendamiento_elite(
        self, contrato_id: int, es_borrador: bool = False
    ):
        """
        Genera contrato de arrendamiento lite

        Args:
            contrato_id: ID del contrato
            es_borrador: Si es borrador
        """
        logger.info("=" * 80)
        logger.info("[CLICK]  FRONTEND: Button clicked! Event handler triggered")
        logger.info(
            f"[PARAM] Parameters received: contrato_id={contrato_id}, es_borrador={es_borrador}"
        )
        logger.info(f"[TIME]  Timestamp: {datetime.now().isoformat()}")
        logger.info("[LOC] Call stack entry point: generar_contrato_arrendamiento_elite")
        logger.info("[START] INICIANDO GENERACIN DE CONTRATO LITE")
        logger.info(f"Contrato ID: {contrato_id}")
        logger.info(f"Es Borrador: {es_borrador}")

        self.generating = True
        self.error_message = ""

        try:
            logger.debug("[DATA] Paso 1: Obteniendo datos del contrato...")
            datos = self._get_datos_contrato(contrato_id)
            logger.debug(f"[OK] Datos obtenidos: {list(datos.keys())}")

            logger.debug("[PDF] Paso 2: Generando PDF con facade...")
            pdf_path = get_pdf_service().generar_contrato_elite(
                datos, usar_borrador=es_borrador
            )
            logger.debug(f"[OK] PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path
            self.success_message = f"Contrato lite generado: {Path(pdf_path).name}"

            logger.info("[OK] CONTRATO GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success(self.success_message)

            # ESTRATEGIA EXPERTA: API Backend Directa
            yield type(self).descargar_pdf_script(pdf_path)

        except Exception as e:
            logger.error("[ERROR] ERROR EN GENERACIN DE CONTRATO")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            self.error_message = f"Error: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.generating = False
            logger.info("=" * 80)

    @rx.event
    def generar_contrato_mandato_elite(
        self, contrato_id: int, es_borrador: bool = False
    ):
        """
        Genera contrato de mandato lite

        Args:
            contrato_id: ID del contrato de mandato
            es_borrador: Si es borrador
        """
        logger.info("=" * 80)
        logger.info("[CLICK]  FRONTEND: Button clicked - Mandato Contract!")
        logger.info(
            f"[PARAM] Parameters: contrato_id={contrato_id}, es_borrador={es_borrador}"
        )
        logger.info(f"[TIME]  Timestamp: {datetime.now().isoformat()}")
        logger.info("[START] INICIANDO GENERACIN DE CONTRATO MANDATO LITE")

        self.generating = True
        self.error_message = ""

        try:
            logger.debug("[DATA] Paso 1: Obteniendo datos del contrato mandato...")
            datos = self._get_datos_contrato_mandato(contrato_id)
            logger.debug(f"[OK] Datos obtenidos: {list(datos.keys())}")

            logger.debug("[PDF] Paso 2: Generando PDF con facade...")
            pdf_path = get_pdf_service().generar_contrato_elite(
                datos, usar_borrador=es_borrador
            )
            logger.debug(f"[OK] PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path
            self.success_message = (
                f"Contrato mandato lite generado: {Path(pdf_path).name}"
            )

            logger.info("[OK] CONTRATO MANDATO GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success(self.success_message)

            # ESTRATEGIA LITE: Fetch + Blob URL
            yield type(self).descargar_pdf_script(pdf_path)

        except Exception as e:
            logger.error("[ERROR] ERROR EN GENERACIN DE CONTRATO MANDATO")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            self.error_message = f"Error: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.generating = False
            logger.info("=" * 80)

    @rx.event
    def generar_certificado_paz_y_salvo(
        self, contrato_id: int, beneficiario_nombre: str
    ):
        """
        Genera certificado de paz y salvo

        Args:
            contrato_id: ID del contrato
            beneficiario_nombre: Nombre del beneficiario
        """
        self.generating = True

        try:
            datos = {
                "certificado_id": contrato_id * 1000,  # ID nico
                "tipo": "paz_y_salvo",
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "beneficiario": {
                    "nombre": beneficiario_nombre,
                    "documento": "N/A",  # TODO: obtener de DB
                },
                "contenido": (
                    f"El seor(a) {beneficiario_nombre} se encuentra a PAZ Y SALVO "
                    f"con la INMOBILIARIA VELAR SAS por concepto de arrendamiento "
                    f"del inmueble objeto del contrato No. {contrato_id}.\n\n"
                    f"No presenta deudas pendientes por canon de arrendamiento, "
                    f"servicios pblicos, ni otras obligaciones contractuales."
                ),
                "firmante": {
                    "nombre": "Gerencia General",
                    "cargo": "Representante Legal",
                    "documento": "NIT 900.123.456-7",
                },
            }

            pdf_path = get_pdf_service().generar_certificado_elite(datos)
            self.last_pdf_path = pdf_path

            yield rx.toast.success("Certificado de paz y salvo generado")

            # ESTRATEGIA EXPERTA: API Backend Directa
            yield type(self).descargar_pdf_script(pdf_path)

        except Exception as e:
            logger.error("[ERROR] ERROR EN GENERACIN DE CERTIFICADO PAZ Y SALVO")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error: {str(e)}")
        finally:
            self.generating = False

    @rx.event
    def generar_liquidacion_pdf(self, id_liquidacion: int):
        """
        Genera PDF de liquidación individual usando el servicio Élite (ReportLab).

        Args:
            id_liquidacion: ID de la liquidación
        """
        logger.info("=" * 80)
        logger.info("[MONEY] INICIANDO GENERACIN DE PDF LIQUIDACIN ELITE")
        logger.info(f"Liquidacin ID: {id_liquidacion}")
        logger.info(f"Timestamp: {datetime.now()}")

        self.generating = True

        try:
            logger.debug("[DATA] Paso 1: Obteniendo datos de liquidacin desde BD...")
            datos = self._get_datos_liquidacion(id_liquidacion)
            logger.debug(f"[OK] Datos obtenidos: {list(datos.keys())}")

            # Transformar a formato Élite
            logger.debug("[TRANSFORM] Paso 2: Transformando datos a formato Élite...")
            datos_pdf = self._transform_individual_to_pdf_format(datos)

            logger.debug("[PDF] Paso 3: Generando PDF con facade (Elite mode)...")
            pdf_path = get_pdf_service().generar_estado_cuenta_elite(datos_pdf)
            logger.debug(f"[OK] PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path

            logger.info("[OK] LIQUIDACIN PDF GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success("Estado de cuenta generado exitosamente (Modo Élite)")

            # ESTRATEGIA EXPERTA: API Backend Directa
            yield type(self).descargar_pdf_script(pdf_path)

        except Exception as e:
            logger.error("[ERROR] ERROR EN GENERACIN DE PDF LIQUIDACIN")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error al generar PDF: {str(e)}")
        finally:
            self.generating = False
            logger.info("=" * 80)

    @rx.event
    def generar_estado_cuenta_elite(
        self,
        propietario_id: int = None,
        periodo: str = None,
        liquidacion_id: int = None,
    ):
        """
        Genera estado de cuenta lite - ahora soporta dos modos:
        1. Por propietario/perodo (usa mock data - legacy)
        2. Por liquidacion_id (usa datos reales de BD - nuevo)

        Args:
            propietario_id: ID del propietario (modo legacy)
            periodo: Perodo (YYYY-MM) (modo legacy)
            liquidacion_id: ID de liquidacin especfica (modo nuevo - preferido)
        """
        logger.info("=" * 80)
        logger.info("[MONEY] INICIANDO GENERACIN DE ESTADO DE CUENTA LITE")

        # Determinar modo de operacin
        if liquidacion_id:
            logger.info(f"Modo: Liquidacin especfica (ID: {liquidacion_id})")
            logger.info(f"Timestamp: {datetime.now()}")

            # Delegar al nuevo mtodo especializado
            yield from self.generar_liquidacion_pdf(liquidacion_id)
            return  # [OK] EXIT HERE - Don't continue to legacy code!

        # Modo legacy por propietario/perodo
        logger.info("Modo: Legacy por propietario/perodo")
        logger.info(f"Propietario ID: {propietario_id}")
        logger.info(f"Perodo: {periodo}")
        logger.info(f"Timestamp: {datetime.now()}")

        logger.info("[CLICK]  FRONTEND: Estado de Cuenta button clicked!")
        logger.info("[SYNC] Estado generando: False  True")
        self.generating = True

        try:
            logger.debug("[DATA] Paso 1: Obteniendo datos del estado cuenta...")
            datos = self._get_datos_estado_cuenta(propietario_id, periodo)
            logger.debug(f"[OK] Datos obtenidos: {list(datos.keys())}")

            # Transform consolidated data to PDF format
            logger.debug("[SYNC] Transformando datos consolidados a formato PDF...")
            datos_pdf = self._transform_consolidated_to_pdf_format(datos)
            logger.debug(f"[OK] Datos transformados: {list(datos_pdf.keys())}")
            logger.debug(f"  - Movimientos: {len(datos_pdf.get('movimientos', []))}")
            logger.debug(
                f"  - Resumen keys: {list(datos_pdf.get('resumen', {}).keys())}"
            )

            logger.debug("[PDF] Paso 2: Generando PDF con facade...")
            pdf_path = get_pdf_service().generar_estado_cuenta_elite(datos_pdf)
            logger.debug(f"[OK] PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path

            logger.info("[OK] ESTADO DE CUENTA GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success("Estado de cuenta lite generado")

            # ESTRATEGIA EXPERTA: API Backend Directa
            yield type(self).descargar_pdf_script(pdf_path)

        except Exception as e:
            logger.error("[ERROR] ERROR EN GENERACIN DE ESTADO DE CUENTA")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error: {str(e)}")
        finally:
            self.generating = False
            logger.info("=" * 80)

    # ========================================================================
    # MTODOS AUXILIARES - CONECTADOS A MOCK REPOSITORY
    # ========================================================================

    def _get_datos_contrato(self, contrato_id: int) -> Dict[str, Any]:
        """
        Obtiene datos del contrato desde la base de datos real
        """
        from src.aplicacion.servicios.servicio_contratos import ServicioContratos
        from src.infraestructura.persistencia.database import db_manager
        from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
            RepositorioContratoMandatoPostgres,
        )
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
            RepositorioContratoArrendamientoPostgres,
        )
        from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
            RepositorioPropiedadPostgres,
        )
        from src.infraestructura.persistencia.repositorio_renovacion_postgres import (
            RepositorioRenovacionPostgres,
        )
        from src.infraestructura.persistencia.repositorio_ipc_postgres import (
            RepositorioIPCPostgres,
        )
        from src.infraestructura.persistencia.repositorio_arrendatario_postgres import (
            RepositorioArrendatarioPostgres,
        )
        from src.infraestructura.persistencia.repositorio_codeudor_postgres import (
            RepositorioCodeudorPostgres,
        )

        # Instanciar repositorios requeridos
        repo_mandato = RepositorioContratoMandatoPostgres(db_manager)
        repo_arriendo = RepositorioContratoArrendamientoPostgres(db_manager)
        repo_propiedad = RepositorioPropiedadPostgres(db_manager)
        repo_renovacion = RepositorioRenovacionPostgres(db_manager)
        repo_ipc = RepositorioIPCPostgres(db_manager)
        repo_arrendatario = RepositorioArrendatarioPostgres(db_manager)
        repo_codeudor = RepositorioCodeudorPostgres(db_manager)

        servicio = ServicioContratos(
            db_manager,
            repo_mandato,
            repo_arriendo,
            repo_propiedad,
            repo_renovacion,
            repo_ipc,
            repo_arrendatario,
            repo_codeudor,
        )

        # Obtener detalles del contrato de arrendamiento desde la DB
        detalle = servicio.obtener_detalle_contrato_ui(contrato_id, "Arrendamiento")

        if not detalle:
            raise ValueError(f"Contrato {contrato_id} no encontrado")

        from src.aplicacion.servicios.servicio_configuracion import (
            ServicioConfiguracion,
        )

        # Obtener configuracin de empresa para el logo
        servicio_config = ServicioConfiguracion(db_manager)
        config_empresa = servicio_config.obtener_configuracion_empresa()
        logo_data = config_empresa.logo_base64 if config_empresa else None

        # Transformar el formato de la BD al formato esperado por el generador PDF
        return {
            "contrato_id": detalle["id"],
            "logo_base64": logo_data,  # Logo inyectado
            "fecha": detalle["fecha_inicio"],
            "fecha_inicio": detalle["fecha_inicio"],
            "fecha_fin": detalle["fecha_fin"],
            "estado": detalle["estado"],
            "arrendador": {
                "nombre": detalle.get("propietario", "N/A"),
                "documento": detalle.get("documento_propietario", "N/A"),
                "telefono": detalle.get("telefono_propietario", "N/A"),
                "email": detalle.get("email_propietario", "N/A"),
                "direccion": detalle.get("direccion_propietario", "N/A"),
            },
            "arrendatario": {
                "nombre": detalle.get("arrendatario", "N/A"),
                "documento": detalle.get("documento", "N/A"),
                "telefono": detalle.get("telefono", "N/A"),
                "email": detalle.get("email", "N/A"),
                "direccion": detalle.get("direccion_arrendatario", "N/A"),
                "codigo_seguro": detalle.get("codigo_seguro", "N/A"),
            },
            "codeudor": {
                "nombre": detalle.get("codeudor", "N/A"),
                "documento": detalle.get("documento_codeudor", "N/A"),
                "telefono": detalle.get("telefono_codeudor", "N/A"),
                "email": detalle.get("email_codeudor", "N/A"),
                "direccion": detalle.get("direccion_codeudor", "N/A"),
            },
            "inmueble": {
                "direccion": detalle.get("direccion", "N/A"),
                "matricula_inmobiliaria": detalle.get("matricula", "N/A"),
                "tipo": detalle.get("tipo_propiedad", "Apartamento"),
                "area": str(detalle.get("area_m2", "0")),
                "municipio": detalle.get("municipio", "N/A"),
                "departamento": detalle.get("departamento", "N/A"),
                "habitaciones": "0",  # TODO: Agregar a la query si est disponible
                "banos": "0",  # TODO: Agregar a la query si est disponible
                "estrato": "0",  # TODO: Agregar a la query si est disponible
            },
            "condiciones": {
                "canon": detalle.get("canon", 0),
                "duracion_meses": detalle.get("duracion", 12),
                "fecha_pago": detalle.get("fecha_pago", 5),
                "deposito": detalle.get("deposito", 0),
                "administracion": 0,  # Not in query explicitly
            },
        }

    def _get_datos_contrato_mandato(self, contrato_id: int) -> Dict[str, Any]:
        """
        Obtiene datos del contrato de mandato desde la base de datos real
        """
        from src.aplicacion.servicios.servicio_contratos import ServicioContratos
        from src.infraestructura.persistencia.database import db_manager
        from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
            RepositorioContratoMandatoPostgres,
        )
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
            RepositorioContratoArrendamientoPostgres,
        )
        from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
            RepositorioPropiedadPostgres,
        )
        from src.infraestructura.persistencia.repositorio_renovacion_postgres import (
            RepositorioRenovacionPostgres,
        )
        from src.infraestructura.persistencia.repositorio_ipc_postgres import (
            RepositorioIPCPostgres,
        )
        from src.infraestructura.persistencia.repositorio_arrendatario_postgres import (
            RepositorioArrendatarioPostgres,
        )
        from src.infraestructura.persistencia.repositorio_codeudor_postgres import (
            RepositorioCodeudorPostgres,
        )

        # Instanciar repositorios requeridos
        repo_mandato = RepositorioContratoMandatoPostgres(db_manager)
        repo_arriendo = RepositorioContratoArrendamientoPostgres(db_manager)
        repo_propiedad = RepositorioPropiedadPostgres(db_manager)
        repo_renovacion = RepositorioRenovacionPostgres(db_manager)
        repo_ipc = RepositorioIPCPostgres(db_manager)
        repo_arrendatario = RepositorioArrendatarioPostgres(db_manager)
        repo_codeudor = RepositorioCodeudorPostgres(db_manager)

        servicio = ServicioContratos(
            db_manager,
            repo_mandato,
            repo_arriendo,
            repo_propiedad,
            repo_renovacion,
            repo_ipc,
            repo_arrendatario,
            repo_codeudor,
        )

        # Obtener detalles del contrato de mandato desde la DB
        detalle = servicio.obtener_detalle_contrato_ui(contrato_id, "Mandato")

        if not detalle:
            raise ValueError(f"Contrato mandato {contrato_id} no encontrado")

        from src.aplicacion.servicios.servicio_configuracion import (
            ServicioConfiguracion,
        )

        # Obtener configuracin de empresa para el logo y datos del mandatario
        servicio_config = ServicioConfiguracion(db_manager)
        config_empresa = servicio_config.obtener_configuracion_empresa()
        logo_data = config_empresa.logo_base64 if config_empresa else None

        # Datos Inmobiliaria (Mandatario) desde config o fallback
        nombre_inmo = (
            config_empresa.nombre_empresa
            if config_empresa
            else "INMOBILIARIA VELAR S.A.S."
        )
        nit_inmo = config_empresa.nit if config_empresa else "901703515-7"
        direccion_inmo = (
            config_empresa.direccion
            if config_empresa
            else "Calle 19 No. 16  44 Centro Comercial Manhatan Local 15"
        )
        telefono_inmo = config_empresa.telefono if config_empresa else "3011281684"
        email_inmo = (
            config_empresa.email
            if config_empresa
            else "inmobiliariavelarsasaxm@gmail.com"
        )
        rep_legal = (
            config_empresa.representante_legal
            if config_empresa
            else "CRISTIAN FERNANDO JAMIOY FONSECA"
        )
        rep_legal_cc = (
            config_empresa.cedula_representante if config_empresa else "1.094.959.215"
        )

        # Clculo de fechas
        fecha_inicio_str = detalle["fecha_inicio"]
        duracion_meses = detalle.get("duracion", 12)
        try:
            # Intentar calcular fecha fin
            f_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
            # Aproximacin simple de meses (se puede mejorar con relativedelta si est disponible)
            import calendar

            def add_months(sourcedate, months):
                month = sourcedate.month - 1 + months
                year = sourcedate.year + month // 12
                month = month % 12 + 1
                day = min(sourcedate.day, calendar.monthrange(year, month)[1])
                return sourcedate.replace(year=year, month=month, day=day)

            f_fin = add_months(f_inicio, duracion_meses)
            fecha_fin_str = f_fin.strftime("%Y-%m-%d")
        except Exception:
            # Fallback si falla el parseo
            fecha_fin_str = "N/A"

        # Transformar el formato de la BD al formato esperado por el generador PDF
        return {
            "contrato_id": detalle["id"],
            "fecha": detalle["fecha_inicio"],  # Fecha de firma/generacin
            "fecha_inicio": detalle["fecha_inicio"],
            "fecha_fin": fecha_fin_str,
            "estado": detalle["estado"],
            "tipo_contrato": "MANDATO",
            "logo_base64": logo_data,
            "mandante": {  # Propietario en mandato
                "nombre": detalle.get("propietario", "N/A"),
                "documento": detalle.get("documento", "N/A"),
                "telefono": detalle.get("telefono", "N/A"),
                "email": detalle.get("email", "N/A"),
                "consignatario": detalle.get("consignatario", ""),
                "documento_consignatario": detalle.get("documento_consignatario", ""),
                "direccion": detalle.get("direccion_propietario", "N/A"),
                "banco": detalle.get("banco", "N/A"),
                "tipo_cuenta": detalle.get("tipo_cuenta", "N/A"),
                "numero_cuenta": detalle.get("numero_cuenta", "N/A"),
            },
            "inmobiliaria": {  # Mandatario
                "nombre": nombre_inmo,
                "nit": nit_inmo,
                "direccion": direccion_inmo,
                "telefono": telefono_inmo,
                "email": email_inmo,
                "representante": rep_legal,
                "documento_rep": rep_legal_cc,
            },
            "inmueble": {
                "direccion": detalle.get(
                    "direccion", "N/A"
                ),  # Corregido: llave correcta es 'direccion'
                "matricula_inmobiliaria": detalle.get("matricula", "N/A"),
                "tipo": detalle.get("tipo_propiedad", "Apartamento"),
                "area": str(detalle.get("area", "0")),
                "municipio": detalle.get("municipio", "N/A"),
                "departamento": detalle.get("departamento", "N/A"),
            },
            "condiciones": {
                "comision": int(float(detalle.get("comision_pct", 0))),
                "duracion_meses": detalle.get("duracion", 12),
                "valor_canon_sugerido": detalle.get(
                    "canon", 0
                ),  # Valor del canon de arrendamiento
                "fecha_pago": detalle.get("fecha_pago", "5"),  # Default 5 if missing
            },
        }

    def _get_datos_estado_cuenta(
        self, propietario_id: int, periodo: str
    ) -> Dict[str, Any]:
        """
        Obtiene datos consolidados del estado de cuenta para un propietario/perodo.
        Usa datos reales de la base de datos.

        Args:
            propietario_id: ID del propietario
            periodo: Perodo (YYYY-MM)

        Returns:
            Diccionario con datos consolidados

        Raises:
            ValueError: Si no se encuentran liquidaciones
        """
        from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
        from src.infraestructura.persistencia.database import db_manager

        servicio = ServicioFinanciero(db_manager)

        datos = servicio.obtener_datos_consolidados_para_pdf(propietario_id, periodo)

        if not datos:
            raise ValueError("No se encontraron datos para generar el estado de cuenta")

        # --- OBTENER CONFIGURACIN DE EMPRESA ---
        from src.aplicacion.servicios.servicio_configuracion import (
            ServicioConfiguracion,
        )

        servicio_config = ServicioConfiguracion(db_manager)
        config_empresa = servicio_config.obtener_configuracion_empresa()

        if config_empresa:
            datos["empresa"] = {
                "nombre": config_empresa.nombre_empresa,
                "nit": config_empresa.nit,
                "direccion": config_empresa.direccion,
                "telefono": config_empresa.telefono,
                "email": config_empresa.email,
                "logo_base64": config_empresa.logo_base64,
                "website": config_empresa.website,
            }

        return datos

    def _transform_individual_to_pdf_format(
        self, datos: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transforma datos de una liquidación individual al formato esperado por el generador Élite.
        """
        # 1. Propietario
        propietario = {
            "nombre": datos.get("propietario", "N/A"),
            "documento": datos.get("documento", "N/A"),
            "telefono": datos.get("telefono", "N/A"),
            "email": datos.get("email", "N/A"),
        }

        # 2. Inmueble
        inmueble = {
            "direccion": datos.get("propiedad", "N/A"),
            "tipo": datos.get("tipo_propiedad", "Propiedad"),
            "canon": datos.get("canon", 0),
        }

        # 3. Detalle (Fila única)
        prop_id = datos.get("id_contrato", 1)
        
        # Calcular incidentes (agrupados)
        gastos_rep = datos.get("gastos_rep", 0) or 0
        otros_egr = datos.get("otros_egr", 0) or 0
        incidentes = gastos_rep + otros_egr

        detalle = {
            "id": prop_id,
            "canon": datos.get("canon", 0) or 0,
            "comision": datos.get("comision_monto", 0) or 0,
            "seguro": datos.get("seguro_monto", 0) or 0,
            "iva": datos.get("iva_comision", 0) or 0,
            "impuesto_4x1000": datos.get("impuesto_4x1000", 0) or 0,
            "admin": datos.get("gastos_admin", 0) or 0,
            "servicios": datos.get("gastos_serv", 0) or 0,
            "predial": datos.get("pago_predial", 0) or 0,
            "incidente": incidentes,
            "total": datos.get("neto_pagar", 0) or 0,
        }

        # 4. Resumen
        resumen = {
            "total_ingresos": datos.get("total_ingresos", 0) or 0,
            "total_egresos": datos.get("total_egresos", 0) or 0,
            "honorarios": datos.get("comision_monto", 0) or 0,
            "otros_descuentos": (datos.get("total_egresos", 0) or 0) - (datos.get("comision_monto", 0) or 0),
            "valor_neto": datos.get("neto_pagar", 0) or 0,
            "cuenta_bancaria": f"{datos.get('banco', 'N/A')} - {datos.get('tipo_cuenta', '')} {datos.get('numero_cuenta', '')}"
        }

        # 5. Formato Final
        return {
            "estado_id": datos.get("id"),
            "periodo": datos.get("periodo"),
            "fecha_generacion": datos.get("fecha_generacion"),
            "propietario": propietario,
            "inmueble": inmueble,
            "lista_propiedades": [{"id": prop_id, "direccion": inmueble["direccion"]}],
            "detalle_propiedades": [detalle],
            "resumen": resumen,
            "observaciones": datos.get("observaciones"), # Propagación vital
            "empresa": datos.get("empresa", {}),
            "modo": "individual",
        }

    def _transform_consolidated_to_pdf_format(
        self, datos: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transforma datos consolidados al formato esperado por el generador PDF.

        Args:
            datos: Datos consolidados de obtener_datos_consolidados_para_pdf

        Returns:
            Datos en formato compatible con EstadoCuentaElite
        """
        # Construir objeto propietario (nested)
        propietario = {
            "nombre": datos["propietario"],
            "documento": datos["documento"],
            "telefono": datos.get("telefono", "N/A"),
            "email": datos.get("email", "N/A"),
        }

        # Usar primera propiedad como inmueble principal
        propiedades = datos.get("propiedades", [])
        if propiedades:
            primera_prop = propiedades[0]
            inmueble = {
                "direccion": primera_prop["direccion"],
                "tipo": "Propiedad",
                "canon": primera_prop["canon"],
            }
        else:
            # Fallback si no hay propiedades
            inmueble = {"direccion": "N/A", "tipo": "Propiedad", "canon": 0}

        # Convertir propiedades a detalle detallado (lista de filas para la tabla)
        detalle_propiedades = []
        lista_propiedades = []

        total_seguro_global = 0

        for idx, prop in enumerate(propiedades, 1):
            prop_id = prop.get("id", idx)  # Fallback to index if no ID

            # Agregar a lista de identificacin de propiedades
            lista_propiedades.append({"id": prop_id, "direccion": prop["direccion"]})

            # Calcular valores para la fila de detalle
            canon = prop["canon"]
            comision = prop["comision_monto"]
            iva = prop["iva_comision"]
            imp_4x1000 = prop["impuesto_4x1000"]
            admin = prop["gastos_admin"]
            servicios = prop["gastos_serv"]

            # Clculo de Seguro (Usar valor persistido, no recalcular)
            valor_seguro = prop.get("seguro_monto", 0) or 0
            total_seguro_global += valor_seguro

            # Incidentes y Otros
            incidente = prop["gastos_rep"] + prop["otros_egr"]

            predial = 0  # No disponible en modelo actual, default 0

            # Total Fila (Usar valor persistido si existe, si no recalcular)
            total_fila = prop.get("neto")
            if total_fila is None:
                total_fila = canon - (
                    comision
                    + valor_seguro
                    + iva
                    + imp_4x1000
                    + admin
                    + servicios
                    + predial
                    + incidente
                )

            detalle_propiedades.append(
                {
                    "id": prop_id,
                    "canon": canon,
                    "comision": comision,
                    "seguro": valor_seguro,
                    "iva": iva,
                    "impuesto_4x1000": imp_4x1000,
                    "admin": admin,
                    "servicios": servicios,
                    "predial": predial,
                    "incidente": incidente,
                    "total": total_fila,
                }
            )

        # Construir resumen (Confiar en los totales calculados por el repositorio/dominio)
        resumen = {
            "total_ingresos": datos["total_ingresos"],
            "total_egresos": datos["total_egresos"],
            "honorarios": datos["comision_monto"],
            "otros_descuentos": (datos["total_egresos"] or 0) - (datos["comision_monto"] or 0),
            "valor_neto": datos["neto_pagar"],
            "cuenta_bancaria": f"{datos['banco']} - {datos['tipo_cuenta']} {datos['cuenta_bancaria']}",
        }

        # Formato final compatible con EstadoCuentaElite
        return {
            "estado_id": abs(hash(f"{datos['propietario']}-{datos['periodo']}"))
            % 1000000,  # Generate pseudo ID
            "propietario": propietario,
            "inmueble": inmueble,
            "periodo": datos["periodo"],
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d"),
            "lista_propiedades": lista_propiedades,
            "detalle_propiedades": detalle_propiedades,
            "resumen": resumen,
            "empresa": datos.get("empresa", {}),
            "observaciones": datos.get("observaciones"), # Usar la nueva clave unificada
            "notas": [
                f"Estado de cuenta consolidado - {datos['cantidad_propiedades']} propiedades",
            ],
            "modo": "consolidado",
        }

    @rx.event
    def generar_liquidacion_asesor_pdf(self, id_liquidacion_asesor: int):
        """
        Genera PDF de liquidacin de asesor (Cuenta de Cobro).

        Args:
            id_liquidacion_asesor: ID de la liquidacin del asesor
        """
        logger.info("=" * 80)
        logger.info(" INICIANDO GENERACIN DE PDF LIQUIDACIN ASESOR")
        logger.info(f"ID Liquidacin Asesor: {id_liquidacion_asesor}")
        logger.info(f"Timestamp: {datetime.now()}")

        self.generating = True

        try:
            logger.debug(
                "[DATA] Paso 1: Inicializando servicio de liquidaciones asesores..."
            )

            from src.aplicacion.servicios.servicio_liquidacion_asesores import (
                ServicioLiquidacionAsesores,
            )
            from src.infraestructura.persistencia.database import db_manager
            from src.infraestructura.persistencia.repositorio_asesor_postgres import (
                RepositorioAsesorPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_persona_postgres import (
                RepositorioPersonaPostgres,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
                RepositorioPropiedadPostgres,
            )
            from src.infraestructura.repositorios.repositorio_bonificacion_asesor import (
                RepositorioBonificacionAsesor,
            )
            from src.infraestructura.repositorios.repositorio_descuento_asesor import (
                RepositorioDescuentoAsesor,
            )
            from src.infraestructura.repositorios.repositorio_liquidacion_asesor import (
                RepositorioLiquidacionAsesor,
            )
            from src.infraestructura.repositorios.repositorio_pago_asesor import (
                RepositorioPagoAsesor,
            )
            from src.infraestructura.servicios.servicio_documentos_pdf import (
                ServicioDocumentosPDF,
            )

            # Create only required repositories (matching pattern from liquidacion_asesores_state.py)
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_descuento = RepositorioDescuentoAsesor(db_manager)
            repo_pago = RepositorioPagoAsesor(db_manager)
            repo_bonificacion = RepositorioBonificacionAsesor(db_manager)
            repo_contrato = RepositorioContratoArrendamientoPostgres(db_manager)
            repo_propiedad = RepositorioPropiedadPostgres(db_manager)
            repo_asesor = RepositorioAsesorPostgres(db_manager)
            repo_persona = RepositorioPersonaPostgres(db_manager)
            servicio_pdf = ServicioDocumentosPDF()

            # Initialize service with all dependencies for PDF generation
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago,
                repo_bonificacion=repo_bonificacion,
                repo_contrato_arrendamiento=repo_contrato,
                repo_propiedad=repo_propiedad,
                servicio_pdf=servicio_pdf,
                repo_asesor=repo_asesor,
                repo_persona=repo_persona,
            )
            logger.debug("[OK] Servicio inicializado correctamente")

            logger.debug("[PDF] Paso 2: Generando PDF de cuenta de cobro...")
            pdf_path = servicio.generar_pdf_comprobante(id_liquidacion_asesor)
            logger.debug(f"[OK] PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path

            logger.info("[OK] PDF LIQUIDACIN ASESOR GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success("PDF de liquidacin de asesor generado")

            # ESTRATEGIA LITE: Fetch + Blob URL (same as Propietarios)
            yield type(self).descargar_pdf_script(pdf_path)

        except Exception as e:
            logger.error("[ERROR] ERROR EN GENERACIN DE PDF LIQUIDACIN ASESOR")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error: {str(e)}")
        finally:
            self.generating = False
            logger.info("=" * 80)

    @rx.event
    def generar_recibo_pago_pdf(self, id_recaudo: int):
        """
        Genera PDF de recibo de pago para un recaudo.

        Args:
            id_recaudo: ID del recaudo
        """
        logger.info("=" * 80)
        logger.info(" INICIANDO GENERACIN DE PDF RECIBO DE PAGO")
        logger.info(f"ID Recaudo: {id_recaudo}")
        logger.info(f"Timestamp: {datetime.now()}")

        self.generating = True

        try:
            logger.debug("[DATA] Paso 1: Obteniendo datos del recaudo...")

            from src.infraestructura.persistencia.database import db_manager
            from src.infraestructura.persistencia.repositorio_recaudo import (
                RepositorioRecaudo,
            )

            repo_recaudo = RepositorioRecaudo(db_manager)

            # Fetch recaudo with all related data
            placeholder = (
                db_manager.get_placeholder()
            )  # Get correct placeholder for DB type

            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)

                # Main query using placeholder from db_manager (not hardcoded $1)
                # Main query using placeholder from db_manager (not hardcoded $1)
                query = f"""
                SELECT 
                    r.ID_RECAUDO,
                    r.ID_CONTRATO_A,
                    r.FECHA_PAGO,
                    r.VALOR_TOTAL,
                    r.METODO_PAGO,
                    r.REFERENCIA_BANCARIA,
                    r.ESTADO_RECAUDO,
                    r.OBSERVACIONES,
                    p.DIRECCION_PROPIEDAD,
                    p.MATRICULA_INMOBILIARIA,
                    m.NOMBRE_MUNICIPIO as MUNICIPIO,
                    m.DEPARTAMENTO,
                    per.NOMBRE_COMPLETO as NOMBRE_ARRENDATARIO,
                    per.NUMERO_DOCUMENTO as DOCUMENTO_ARRENDATARIO,
                    per.CORREO_ELECTRONICO as EMAIL_ARRENDATARIO,
                    per.TELEFONO_PRINCIPAL as TELEFONO_ARRENDATARIO
                FROM RECAUDOS r
                INNER JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
                INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                LEFT JOIN MUNICIPIOS m ON p.ID_MUNICIPIO = m.ID_MUNICIPIO
                INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                INNER JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                WHERE r.ID_RECAUDO = {placeholder}
                """

                cursor.execute(query, (id_recaudo,))
                row = cursor.fetchone()

                if not row:
                    raise ValueError(f"Recaudo {id_recaudo} no encontrado")

                # Fetch conceptos (correct column names: tipo_concepto, valor, periodo)
                query_conceptos = f"""
                SELECT tipo_concepto, valor, periodo
                FROM recaudo_conceptos
                WHERE id_recaudo = {placeholder}
                ORDER BY tipo_concepto
                """
                cursor.execute(query_conceptos, (id_recaudo,))
                conceptos_rows = cursor.fetchall()

                # Fetch bank account info if available (Optional, strictly speaking not in RECAUDOS but useful)
                # For now using placeholders or derived data

            logger.debug(
                f"[OK] Datos obtenidos: Recaudo {row['ID_RECAUDO']}, Valor ${row['VALOR_TOTAL']:,}"
            )

            # Debug: Log what keys are in conceptos_rows
            if conceptos_rows:
                logger.debug(f" Conceptos keys: {list(conceptos_rows[0].keys())}")
                logger.debug(f" First concepto: {conceptos_rows[0]}")

            # Get PERIODO from first concepto (defensive with .get())
            periodo = datetime.now().strftime("%Y-%m")  # Default
            if conceptos_rows:
                # Try different possible key names
                periodo = (
                    conceptos_rows[0].get("periodo")
                    or conceptos_rows[0].get("PERIODO")
                    or periodo
                )
            logger.debug(f" Periodo usado: {periodo}")

            # Transform to PDF format (adapt to estado_cuenta template structure)
            # Transform to PDF format - FLAT structure (template expects root-level fields)
            datos_pdf = {
                # IDs and period
                "id": row["ID_RECAUDO"],
                "periodo": periodo,
                "fecha_generacion": row["FECHA_PAGO"],
                "estado": row["ESTADO_RECAUDO"],
                # Propietario (flat strings, NOT nested dict)
                "propietario": "Inmobiliaria Velar",  # Schema doesn't have owner info
                "documento": "N/A",
                "telefono": "N/A",
                "email": "N/A",
                "direccion_propietario": "N/A",
                # Propiedad (flat strings)
                "propiedad": row["DIRECCION_PROPIEDAD"],
                "matricula": row["MATRICULA_INMOBILIARIA"] or "Sin matrcula",
                "municipio": row.get("MUNICIPIO", "Armenia").upper(),
                "departamento": row.get("DEPARTAMENTO", "Quindo").upper(),
                # Arrendatario
                "arrendatario": row["NOMBRE_ARRENDATARIO"],
                "arrendatario_doc": row["DOCUMENTO_ARRENDATARIO"],
                "email": row.get("EMAIL_ARRENDATARIO") or "No registrado",
                "telefono": row.get("TELEFONO_ARRENDATARIO") or "No registrado",
                # Financial details
                "valor_total": row["VALOR_TOTAL"],
                "canon": row["VALOR_TOTAL"],
                "otros_ingresos": 0,
                "total_ingresos": row["VALOR_TOTAL"],
                # Egresos
                "comision_pct": 0,
                "comision_monto": 0,
                "iva_comision": 0,
                "impuesto_4x1000": 0,
                "gastos_admin": 0,
                "gastos_serv": 0,
                "gastos_rep": 0,
                "otros_egr": 0,
                "total_egresos": 0,
                # Neto
                "neto_pagar": row["VALOR_TOTAL"],
                # Payment info
                "fecha_pago": row["FECHA_PAGO"],
                "metodo_pago": row["METODO_PAGO"] or "N/A",
                "referencia_pago": row.get("REFERENCIA_BANCARIA") or "N/A",
                # Banking
                "cuenta_bancaria": "No aplica",  # Usually for payments made TO the entity
                "tipo_cuenta": row["METODO_PAGO"],
                "banco": "Caja General",  # Default for cash
                # Notes with arrendatario info
                "observaciones": f"Arrendatario: {row['NOMBRE_ARRENDATARIO']} ({row['DOCUMENTO_ARRENDATARIO']}). {row['OBSERVACIONES'] or ''}".strip(),
                # Audit
                "created_at": datetime.now().isoformat(),
                "created_by": "Sistema",
            }

            # --- INYECTAR DATOS EMPRESA (LOGO) ---
            try:
                from src.aplicacion.servicios.servicio_configuracion import (
                    ServicioConfiguracion,
                )

                servicio_config = ServicioConfiguracion(db_manager)
                config_empresa = servicio_config.obtener_configuracion_empresa()

                if config_empresa:
                    datos_pdf["empresa"] = {
                        "nombre": config_empresa.nombre_empresa,
                        "nit": config_empresa.nit,
                        "direccion": config_empresa.direccion,
                        "telefono": config_empresa.telefono,
                        "email": config_empresa.email,
                        "logo_base64": config_empresa.logo_base64,  # <--- CLAVE PARA EL LOGO
                        "website": config_empresa.website,
                    }
                    # Copia directa para compatibilidad extra
                    datos_pdf["logo_base64"] = config_empresa.logo_base64
            except Exception as e:
                logger.error(f" No se pudo cargar config empresa: {e}")

            logger.debug("[PDF] Paso 2: Generando PDF...")
            pdf_path = get_pdf_service().generar_recibo_recaudo_elite(datos_pdf)
            logger.debug(f"[OK] PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path

            logger.info("[OK] PDF RECIBO DE PAGO GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success("Recibo de pago generado")

            # ESTRATEGIA LITE: Fetch + Blob URL
            yield type(self).descargar_pdf_script(pdf_path)

        except Exception as e:
            logger.error("[ERROR] ERROR EN GENERACIN DE PDF RECIBO DE PAGO")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error: {str(e)}")
        finally:
            self.generating = False
            logger.info("=" * 80)

    def _get_datos_liquidacion(self, id_liquidacion: int) -> Dict[str, Any]:
        """
        Obtiene datos de una liquidacin desde la base de datos real.
        Se conecta directamente a ServicioFinanciero para obtener datos reales.

        Args:
            id_liquidacion: ID de la liquidacin

        Returns:
            Diccionario con datos formateados para PDF

        Raises:
            ValueError: Si la liquidacin no existe
        """
        from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
        from src.infraestructura.persistencia.database import db_manager

        servicio = ServicioFinanciero(db_manager)

        # Get real liquidation data from database
        datos = servicio.obtener_datos_liquidacion_para_pdf(id_liquidacion)

        if not datos:
            raise ValueError(f"Liquidacin {id_liquidacion} no encontrada")

        # --- OBTENER CONFIGURACIN DE EMPRESA ---
        from src.aplicacion.servicios.servicio_configuracion import (
            ServicioConfiguracion,
        )

        servicio_config = ServicioConfiguracion(db_manager)
        config_empresa = servicio_config.obtener_configuracion_empresa()

        if config_empresa:
            datos["empresa"] = {
                "nombre": config_empresa.nombre_empresa,
                "nit": config_empresa.nit,
                "direccion": config_empresa.direccion,
                "telefono": config_empresa.telefono,
                "email": config_empresa.email,
                "logo_base64": config_empresa.logo_base64,
                "website": config_empresa.website,
            }

        return datos

    def _get_datos_certificado(
        self, contrato_id: int, tipo: str = "paz_y_salvo"
    ) -> Dict[str, Any]:
        """
        Obtiene datos para certificado desde el repository

        PRODUCCIN: El MockPDFRepository ya tiene TODOs de cmo conectar a DB real
        """
        from src.infraestructura.servicios.pdf_elite.utils.mock_data_repository import (
            MockPDFRepository,
        )

        datos = MockPDFRepository.get_certificado_data(contrato_id, tipo)

        if not datos:
            raise ValueError(
                f"No se pudo generar certificado para contrato {contrato_id}"
            )

        return datos


__all__ = ["PDFState"]
