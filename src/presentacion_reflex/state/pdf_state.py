"""
PDF State para Integración con Reflex
=====================================
Estado de Reflex para manejar generación de PDFs desde la UI.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import reflex as rx

# Importar facade
from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade

# Configurar logger élite
logger = logging.getLogger("PDFElite")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("\n🔍 [PDF-ELITE] %(asctime)s - %(levelname)s\n%(message)s\n")
    )
    logger.addHandler(handler)


class PDFState(rx.State):
    """
    Estado para manejo de PDFs en Reflex

    Proporciona event handlers para generar PDFs desde la UI
    y manejar descargas automáticas.

    Attributes:
        generating: Si está generando un PDF
        last_pdf_path: Path del último PDF generado
        error_message: Mensaje de error si hubo problema
        success_message: Mensaje de éxito

    Example:
        En una página de Reflex:
        >>> rx.button(
        ...     "Generar Contrato",
        ...     on_click=PDFState.generar_contrato_arrendamiento(contrato_id)
        ... )
    """

    # Estado
    generating: bool = False
    last_pdf_path: str = ""
    error_message: str = ""
    success_message: str = ""

    # Servicio PDF
    _pdf_service: Optional[ServicioPDFFacade] = None

    @property
    def pdf_service(self) -> ServicioPDFFacade:
        """Obtiene instancia del servicio PDF (singleton)"""
        if self._pdf_service is None:
            self._pdf_service = ServicioPDFFacade()
        return self._pdf_service

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
            pdf_path = self.pdf_service.generar_comprobante_recaudo(datos)
            self.last_pdf_path = pdf_path
            self.success_message = f"Comprobante generado: {Path(pdf_path).name}"

            # ESTRATEGIA ÉLITE: Fetch + Blob URL
            # Esto evita problemas de navegación cross-origin y garantiza la descarga
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            js_download = f"""
            fetch('{download_url}')
              .then(res => {{
                  if (!res.ok) throw new Error('Error en descarga: ' + res.statusText);
                  return res.blob();
              }})
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            return rx.call_script(js_download)

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
            pdf_path = self.pdf_service.generar_estado_cuenta(datos)
            self.last_pdf_path = pdf_path
            self.success_message = f"Estado de cuenta generado: {Path(pdf_path).name}"

            # ESTRATEGIA ÉLITE: Fetch + Blob URL
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            js_download = f"""
            fetch('{download_url}')
              .then(res => {{
                  if (!res.ok) throw new Error('Error en descarga: ' + res.statusText);
                  return res.blob();
              }})
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            return rx.call_script(js_download)

        except Exception as e:
            self.error_message = f"Error generando estado de cuenta: {str(e)}"
            return rx.toast.error(self.error_message)
        finally:
            self.generating = False

    # ========================================================================
    # EVENT HANDLERS - DOCUMENTOS ÉLITE
    # ========================================================================

    def generar_contrato_arrendamiento_elite(self, contrato_id: int, es_borrador: bool = False):
        """
        Genera contrato de arrendamiento élite

        Args:
            contrato_id: ID del contrato
            es_borrador: Si es borrador
        """
        logger.info("=" * 80)
        logger.info("🖱️  FRONTEND: Button clicked! Event handler triggered")
        logger.info(f"🔢 Parameters received: contrato_id={contrato_id}, es_borrador={es_borrador}")
        logger.info(f"⏱️  Timestamp: {datetime.now().isoformat()}")
        logger.info("📍 Call stack entry point: generar_contrato_arrendamiento_elite")
        logger.info("🚀 INICIANDO GENERACIÓN DE CONTRATO ÉLITE")
        logger.info(f"Contrato ID: {contrato_id}")
        logger.info(f"Es Borrador: {es_borrador}")

        self.generating = True
        self.error_message = ""

        try:
            logger.debug("📊 Paso 1: Obteniendo datos del contrato...")
            datos = self._get_datos_contrato(contrato_id)
            logger.debug(f"✅ Datos obtenidos: {list(datos.keys())}")

            logger.debug("📄 Paso 2: Generando PDF con facade...")
            pdf_path = self.pdf_service.generar_contrato_elite(datos, usar_borrador=es_borrador)
            logger.debug(f"✅ PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path
            self.success_message = f"Contrato élite generado: {Path(pdf_path).name}"

            logger.info("✅ CONTRATO GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success(self.success_message)

            # ESTRATEGIA EXPERTA: API Backend Directa
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            logger.info(f"✅ Iniciando descarga con Fetch API: {download_url}")

            js_download = f"""
            fetch('{download_url}')
              .then(res => {{
                  if (!res.ok) throw new Error('Error en descarga: ' + res.statusText);
                  return res.blob();
              }})
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            yield rx.call_script(js_download)

        except Exception as e:
            logger.error("❌ ERROR EN GENERACIÓN DE CONTRATO")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            self.error_message = f"Error: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.generating = False
            logger.info("=" * 80)

    def generar_contrato_mandato_elite(self, contrato_id: int, es_borrador: bool = False):
        """
        Genera contrato de mandato élite

        Args:
            contrato_id: ID del contrato de mandato
            es_borrador: Si es borrador
        """
        logger.info("=" * 80)
        logger.info("🖱️  FRONTEND: Button clicked - Mandato Contract!")
        logger.info(f"🔢 Parameters: contrato_id={contrato_id}, es_borrador={es_borrador}")
        logger.info(f"⏱️  Timestamp: {datetime.now().isoformat()}")
        logger.info("🚀 INICIANDO GENERACIÓN DE CONTRATO MANDATO ÉLITE")

        self.generating = True
        self.error_message = ""

        try:
            logger.debug("📊 Paso 1: Obteniendo datos del contrato mandato...")
            datos = self._get_datos_contrato_mandato(contrato_id)
            logger.debug(f"✅ Datos obtenidos: {list(datos.keys())}")

            logger.debug("📄 Paso 2: Generando PDF con facade...")
            pdf_path = self.pdf_service.generar_contrato_elite(datos, usar_borrador=es_borrador)
            logger.debug(f"✅ PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path
            self.success_message = f"Contrato mandato élite generado: {Path(pdf_path).name}"

            logger.info("✅ CONTRATO MANDATO GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success(self.success_message)

            # ESTRATEGIA ÉLITE: Fetch + Blob URL
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            logger.info(f"✅ Iniciando descarga con Fetch API: {download_url}")

            js_download = f"""
            fetch('{download_url}')
              .then(res => {{
                  if (!res.ok) throw new Error('Error en descarga: ' + res.statusText);
                  return res.blob();
              }})
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            yield rx.call_script(js_download)

        except Exception as e:
            logger.error("❌ ERROR EN GENERACIÓN DE CONTRATO MANDATO")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            self.error_message = f"Error: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.generating = False
            logger.info("=" * 80)

    def generar_certificado_paz_y_salvo(self, contrato_id: int, beneficiario_nombre: str):
        """
        Genera certificado de paz y salvo

        Args:
            contrato_id: ID del contrato
            beneficiario_nombre: Nombre del beneficiario
        """
        self.generating = True

        try:
            datos = {
                "certificado_id": contrato_id * 1000,  # ID único
                "tipo": "paz_y_salvo",
                "fecha": rx.moment().format("YYYY-MM-DD"),
                "beneficiario": {
                    "nombre": beneficiario_nombre,
                    "documento": "N/A",  # TODO: obtener de DB
                },
                "contenido": (
                    f"El señor(a) {beneficiario_nombre} se encuentra a PAZ Y SALVO "
                    f"con la INMOBILIARIA VELAR SAS por concepto de arrendamiento "
                    f"del inmueble objeto del contrato No. {contrato_id}.\n\n"
                    f"No presenta deudas pendientes por canon de arrendamiento, "
                    f"servicios públicos, ni otras obligaciones contractuales."
                ),
                "firmante": {
                    "nombre": "Gerencia General",
                    "cargo": "Representante Legal",
                    "documento": "NIT 900.123.456-7",
                },
            }

            pdf_path = self.pdf_service.generar_certificado_elite(datos)
            self.last_pdf_path = pdf_path

            yield rx.toast.success("Certificado de paz y salvo generado")

            # ESTRATEGIA EXPERTA: API Backend Directa
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            # ESTRATEGIA ÉLITE: Fetch + Blob URL
            js_download = f"""
            fetch('{download_url}')
              .then(res => {{
                  if (!res.ok) throw new Error('Error en descarga: ' + res.statusText);
                  return res.blob();
              }})
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            yield rx.call_script(js_download)

        except Exception as e:
            logger.error("❌ ERROR EN GENERACIÓN DE CERTIFICADO PAZ Y SALVO")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error: {str(e)}")
        finally:
            self.generating = False

    def generar_liquidacion_pdf(self, id_liquidacion: int):
        """
        Genera PDF de liquidación individual con datos reales de la base de datos.

        Args:
            id_liquidacion: ID de la liquidación
        """
        logger.info("=" * 80)
        logger.info("💰 INICIANDO GENERACIÓN DE PDF LIQUIDACIÓN")
        logger.info(f"Liquidación ID: {id_liquidacion}")
        logger.info(f"Timestamp: {datetime.now()}")

        self.generating = True

        try:
            logger.debug("📊 Paso 1: Obteniendo datos de liquidación desde BD...")
            datos = self._get_datos_liquidacion(id_liquidacion)
            logger.debug(f"✅ Datos obtenidos: {list(datos.keys())}")
            logger.debug(f"  - Propietario: {datos.get('propietario')}")
            logger.debug(f"  - Propiedad: {datos.get('propiedad')}")
            logger.debug(f"  - Período: {datos.get('periodo')}")
            logger.debug(f"  - Neto: ${datos.get('neto_pagar'):,}")

            logger.debug("📄 Paso 2: Generando PDF con servicio legacy...")
            # Use legacy PDF service directly
            from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF

            pdf_service = ServicioDocumentosPDF()
            pdf_path = pdf_service.generar_estado_cuenta(datos)
            logger.debug(f"✅ PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path

            logger.info("✅ LIQUIDACIÓN PDF GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success("PDF de liquidación generado exitosamente")

            # ESTRATEGIA ÉLITE: Fetch + Blob URL
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            js_download = f"""
            fetch('{download_url}')
              .then(res => {{
                  if (!res.ok) throw new Error('Error en descarga: ' + res.statusText);
                  return res.blob();
              }})
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            yield rx.call_script(js_download)

        except Exception as e:
            logger.error("❌ ERROR EN GENERACIÓN DE PDF LIQUIDACIÓN")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error al generar PDF: {str(e)}")
        finally:
            self.generating = False
            logger.info("=" * 80)

    def generar_estado_cuenta_elite(
        self, propietario_id: int = None, periodo: str = None, liquidacion_id: int = None
    ):
        """
        Genera estado de cuenta élite - ahora soporta dos modos:
        1. Por propietario/período (usa mock data - legacy)
        2. Por liquidacion_id (usa datos reales de BD - nuevo)

        Args:
            propietario_id: ID del propietario (modo legacy)
            periodo: Período (YYYY-MM) (modo legacy)
            liquidacion_id: ID de liquidación específica (modo nuevo - preferido)
        """
        logger.info("=" * 80)
        logger.info("💰 INICIANDO GENERACIÓN DE ESTADO DE CUENTA ÉLITE")

        # Determinar modo de operación
        if liquidacion_id:
            logger.info(f"Modo: Liquidación específica (ID: {liquidacion_id})")
            logger.info(f"Timestamp: {datetime.now()}")

            # Delegar al nuevo método especializado
            yield from self.generar_liquidacion_pdf(liquidacion_id)
            return  # ✅ EXIT HERE - Don't continue to legacy code!

        # Modo legacy por propietario/período
        logger.info("Modo: Legacy por propietario/período")
        logger.info(f"Propietario ID: {propietario_id}")
        logger.info(f"Período: {periodo}")
        logger.info(f"Timestamp: {datetime.now()}")

        logger.info("🖱️  FRONTEND: Estado de Cuenta button clicked!")
        logger.info("🔄 Estado generando: False → True")
        self.generating = True

        try:
            logger.debug("📊 Paso 1: Obteniendo datos del estado cuenta...")
            datos = self._get_datos_estado_cuenta(propietario_id, periodo)
            logger.debug(f"✅ Datos obtenidos: {list(datos.keys())}")

            # Transform consolidated data to PDF format
            logger.debug("🔄 Transformando datos consolidados a formato PDF...")
            datos_pdf = self._transform_consolidated_to_pdf_format(datos)
            logger.debug(f"✅ Datos transformados: {list(datos_pdf.keys())}")
            logger.debug(f"  - Movimientos: {len(datos_pdf.get('movimientos', []))}")
            logger.debug(f"  - Resumen keys: {list(datos_pdf.get('resumen', {}).keys())}")

            logger.debug("📄 Paso 2: Generando PDF con facade...")
            pdf_path = self.pdf_service.generar_estado_cuenta_elite(datos_pdf)
            logger.debug(f"✅ PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path

            logger.info("✅ ESTADO DE CUENTA GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success("Estado de cuenta élite generado")

            # ESTRATEGIA EXPERTA: API Backend Directa
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            # ESTRATEGIA ÉLITE: Fetch + Blob URL
            js_download = f"""
            fetch('{download_url}')
              .then(res => {{
                  if (!res.ok) throw new Error('Error en descarga: ' + res.statusText);
                  return res.blob();
              }})
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            yield rx.call_script(js_download)

        except Exception as e:
            logger.error("❌ ERROR EN GENERACIÓN DE ESTADO DE CUENTA")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error: {str(e)}")
        finally:
            self.generating = False
            logger.info("=" * 80)

    # ========================================================================
    # MÉTODOS AUXILIARES - CONECTADOS A MOCK REPOSITORY
    # ========================================================================

    def _get_datos_contrato(self, contrato_id: int) -> Dict[str, Any]:
        """
        Obtiene datos del contrato desde la base de datos real
        """
        from src.aplicacion.servicios.servicio_contratos import ServicioContratos
        from src.infraestructura.persistencia.database import db_manager
        from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite
        from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
        from src.infraestructura.persistencia.repositorio_renovacion_sqlite import RepositorioRenovacionSQLite
        from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
        from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import RepositorioArrendatarioSQLite
        from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite

        # Instanciar repositorios requeridos
        repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
        repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
        repo_propiedad = RepositorioPropiedadSQLite(db_manager)
        repo_renovacion = RepositorioRenovacionSQLite(db_manager)
        repo_ipc = RepositorioIPCSQLite(db_manager)
        repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
        repo_codeudor = RepositorioCodeudorSQLite(db_manager)

        servicio = ServicioContratos(
            db_manager,
            repo_mandato,
            repo_arriendo,
            repo_propiedad,
            repo_renovacion,
            repo_ipc,
            repo_arrendatario,
            repo_codeudor
        )

        # Obtener detalles del contrato de arrendamiento desde la DB
        detalle = servicio.obtener_detalle_contrato_ui(contrato_id, "Arrendamiento")

        if not detalle:
            raise ValueError(f"Contrato {contrato_id} no encontrado")

        from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
        
        # Obtener configuración de empresa para el logo
        servicio_config = ServicioConfiguracion(db_manager)
        config_empresa = servicio_config.obtener_configuracion_empresa()
        logo_data = config_empresa.logo_base64 if config_empresa else None
        
        # Transformar el formato de la BD al formato esperado por el generador PDF
        return {
            "contrato_id": detalle["id"],
            "logo_base64": logo_data, # Logo inyectado
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
                "habitaciones": "0",  # TODO: Agregar a la query si está disponible
                "banos": "0",  # TODO: Agregar a la query si está disponible
                "estrato": "0",  # TODO: Agregar a la query si está disponible
            },
            "condiciones": {
                "canon": detalle.get("canon", 0),
                "duracion_meses": detalle.get("duracion", 12),
                "dia_pago": 5,  # Default, not in result set directly yet? Check query. Query has logic? No field dia_pago in query.
                "deposito": detalle.get("deposito", 0),
                "administracion": 0, # Not in query explicitly
            },
        }

    def _get_datos_contrato_mandato(self, contrato_id: int) -> Dict[str, Any]:
        """
        Obtiene datos del contrato de mandato desde la base de datos real
        """
        from src.aplicacion.servicios.servicio_contratos import ServicioContratos
        from src.infraestructura.persistencia.database import db_manager
        from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite
        from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
        from src.infraestructura.persistencia.repositorio_renovacion_sqlite import RepositorioRenovacionSQLite
        from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
        from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import RepositorioArrendatarioSQLite
        from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite

        # Instanciar repositorios requeridos
        repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
        repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
        repo_propiedad = RepositorioPropiedadSQLite(db_manager)
        repo_renovacion = RepositorioRenovacionSQLite(db_manager)
        repo_ipc = RepositorioIPCSQLite(db_manager)
        repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
        repo_codeudor = RepositorioCodeudorSQLite(db_manager)

        servicio = ServicioContratos(
            db_manager,
            repo_mandato,
            repo_arriendo,
            repo_propiedad,
            repo_renovacion,
            repo_ipc,
            repo_arrendatario,
            repo_codeudor
        )

        # Obtener detalles del contrato de mandato desde la DB
        detalle = servicio.obtener_detalle_contrato_ui(contrato_id, "Mandato")

        if not detalle:
            raise ValueError(f"Contrato mandato {contrato_id} no encontrado")

        from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
        
        # Obtener configuración de empresa para el logo y datos del mandatario
        servicio_config = ServicioConfiguracion(db_manager)
        config_empresa = servicio_config.obtener_configuracion_empresa()
        logo_data = config_empresa.logo_base64 if config_empresa else None
        
        # Datos Inmobiliaria (Mandatario) desde config o fallback
        nombre_inmo = config_empresa.nombre_empresa if config_empresa else "INMOBILIARIA VELAR S.A.S."
        nit_inmo = config_empresa.nit if config_empresa else "901703515-7"
        direccion_inmo = config_empresa.direccion if config_empresa else "Calle 19 No. 16 – 44 Centro Comercial Manhatan Local 15"
        telefono_inmo = config_empresa.telefono if config_empresa else "3011281684"
        email_inmo = config_empresa.email if config_empresa else "inmobiliariavelarsasaxm@gmail.com"
        rep_legal = config_empresa.representante_legal if config_empresa else "CRISTIAN FERNANDO JAMIOY FONSECA"
        rep_legal_cc = config_empresa.cedula_representante if config_empresa else "1.094.959.215"

        # Cálculo de fechas
        fecha_inicio_str = detalle["fecha_inicio"]
        duracion_meses = detalle.get("duracion", 12)
        try:
            # Intentar calcular fecha fin
            f_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
            # Aproximación simple de meses (se puede mejorar con relativedelta si está disponible)
            import calendar
            
            def add_months(sourcedate, months):
                month = sourcedate.month - 1 + months
                year = sourcedate.year + month // 12
                month = month % 12 + 1
                day = min(sourcedate.day, calendar.monthrange(year,month)[1])
                return sourcedate.replace(year=year, month=month, day=day)
                
            f_fin = add_months(f_inicio, duracion_meses)
            fecha_fin_str = f_fin.strftime("%Y-%m-%d")
        except Exception:
            # Fallback si falla el parseo
            fecha_fin_str = "N/A"

        # Transformar el formato de la BD al formato esperado por el generador PDF
        return {
            "contrato_id": detalle["id"],
            "fecha": detalle["fecha_inicio"], # Fecha de firma/generación
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
                "documento_rep": rep_legal_cc
            },
            "inmueble": {
                "direccion": detalle.get("direccion", "N/A"), # Corregido: llave correcta es 'direccion'
                "matricula_inmobiliaria": detalle.get("matricula", "N/A"),
                "tipo": detalle.get("tipo_propiedad", "Apartamento"),
                "area": str(detalle.get("area", "0")),
                "municipio": detalle.get("municipio", "N/A"),
                "departamento": detalle.get("departamento", "N/A"),
            },
            "condiciones": {
                "comision": float(detalle.get("canon", 0)) * float(detalle.get("comision_pct", 0)),
                "duracion_meses": detalle.get("duracion", 12),
                "valor_canon_sugerido": detalle.get("canon", 0),  # Valor del canon de arrendamiento
            },
        }

    def _get_datos_estado_cuenta(self, propietario_id: int, periodo: str) -> Dict[str, Any]:
        """
        Obtiene datos consolidados del estado de cuenta para un propietario/período.
        Usa datos reales de la base de datos.
        
        Args:
            propietario_id: ID del propietario
            periodo: Período (YYYY-MM)
            
        Returns:
            Diccionario con datos consolidados
            
        Raises:
            ValueError: Si no se encuentran liquidaciones
        """
        from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
        from src.infraestructura.persistencia.database import db_manager
        
        # Importar repositorios requeridos para ServicioFinanciero
        from src.infraestructura.persistencia.repositorio_recaudo_sqlite import RepositorioRecaudoSQLite
        from src.infraestructura.persistencia.repositorio_liquidacion_sqlite import RepositorioLiquidacionSQLite
        from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite
        from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite
        from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
        
        # Instanciar dependencias
        repo_recaudo = RepositorioRecaudoSQLite(db_manager)
        repo_liquidacion = RepositorioLiquidacionSQLite(db_manager)
        repo_propiedad = RepositorioPropiedadSQLite(db_manager)
        repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
        repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
        servicio_pdf = ServicioDocumentosPDF()
        
        # Instanciar servicio financiero con todas sus dependencias
        servicio = ServicioFinanciero(
            repo_recaudo=repo_recaudo,
            repo_liquidacion=repo_liquidacion,
            repo_propiedad=repo_propiedad,
            repo_arriendo=repo_arriendo,
            repo_mandato=repo_mandato,
            pdf_service=servicio_pdf
        )
        
        datos = servicio.obtener_datos_consolidados_para_pdf(propietario_id, periodo)
        
        if not datos:
            raise ValueError("No se encontraron datos para generar el estado de cuenta")

        # --- OBTENER CONFIGURACIÓN DE EMPRESA ---
        from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
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
                "website": config_empresa.website
            }
        
        return datos

    def _transform_consolidated_to_pdf_format(self, datos: Dict[str, Any]) -> Dict[str, Any]:
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
            prop_id = prop.get("id", idx) # Fallback to index if no ID
            
            # Agregar a lista de identificación de propiedades
            lista_propiedades.append({
                "id": prop_id,
                "direccion": prop["direccion"]
            })
            
            # Calcular valores para la fila de detalle
            canon = prop["canon"]
            comision = prop["comision_monto"]
            iva = prop["iva_comision"]
            imp_4x1000 = prop["impuesto_4x1000"]
            admin = prop["gastos_admin"]
            servicios = prop["gastos_serv"]
            
            # Cálculo de Seguro
            pct_seguro = prop.get("porcentaje_seguro", 0)
            # Sistema usa puntos básicos (10000 = 100%). Ejemplo: 200 = 2%
            valor_seguro = int(canon * (pct_seguro / 10000)) if pct_seguro else 0
            
            total_seguro_global += valor_seguro
            
            # Incidentes y Otros
            incidente = prop["gastos_rep"] + prop["otros_egr"]
            
            predial = 0 # No disponible en modelo actual, default 0
            
            # Total Fila (Neto: Canon - Egresos)
            total_fila = (
                canon - (comision + valor_seguro + iva + imp_4x1000 + 
                admin + servicios + predial + incidente)
            )
            
            detalle_propiedades.append({
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
                "total": total_fila
            })

        # Construir resumen (legacy support, though visual table replaces movements)
        # Ajustamos los totales para incluir el Seguro calculado (que no viene en 'datos' DB)
        resumen = {
            "total_ingresos": datos["total_ingresos"],
            "total_egresos": datos["total_egresos"] + total_seguro_global,
            "honorarios": datos["comision_monto"],
            "otros_descuentos": (
                datos["iva_comision"]
                + datos["impuesto_4x1000"]
                + datos["gastos_admin"]
                + datos["gastos_serv"]
                + datos["gastos_rep"]
                + datos["otros_egr"]
                + total_seguro_global
            ),
            "valor_neto": datos["neto_pagar"] - total_seguro_global,
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
            "notas": [
                f"Estado de cuenta consolidado - {datos['cantidad_propiedades']} propiedades",
                datos.get("observaciones", ""),
            ],
        }

    def generar_liquidacion_asesor_pdf(self, id_liquidacion_asesor: int):
        """
        Genera PDF de liquidación de asesor (Cuenta de Cobro).

        Args:
            id_liquidacion_asesor: ID de la liquidación del asesor
        """
        logger.info("=" * 80)
        logger.info("💼 INICIANDO GENERACIÓN DE PDF LIQUIDACIÓN ASESOR")
        logger.info(f"ID Liquidación Asesor: {id_liquidacion_asesor}")
        logger.info(f"Timestamp: {datetime.now()}")

        self.generating = True

        try:
            logger.debug("📊 Paso 1: Inicializando servicio de liquidaciones asesores...")

            # Import correct repositories (matching liquidacion_asesores_state.py pattern)
            from src.aplicacion.servicios.servicio_liquidacion_asesores import (
                ServicioLiquidacionAsesores,
            )
            from src.infraestructura.persistencia.database import db_manager
            from src.infraestructura.persistencia.repositorio_asesor_sqlite import (
                RepositorioAsesorSQLite,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
                RepositorioContratoArrendamientoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_persona_sqlite import (
                RepositorioPersonaSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                RepositorioPropiedadSQLite,
            )
            from src.infraestructura.repositorios.repositorio_bonificacion_asesor_sqlite import (
                RepositorioBonificacionAsesorSQLite,
            )
            from src.infraestructura.repositorios.repositorio_descuento_asesor_sqlite import (
                RepositorioDescuentoAsesorSQLite,
            )
            from src.infraestructura.repositorios.repositorio_liquidacion_asesor_sqlite import (
                RepositorioLiquidacionAsesorSQLite,
            )
            from src.infraestructura.repositorios.repositorio_pago_asesor_sqlite import (
                RepositorioPagoAsesorSQLite,
            )
            from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF

            # Create only required repositories (matching pattern from liquidacion_asesores_state.py)
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            repo_bonificacion = RepositorioBonificacionAsesorSQLite(db_manager)
            repo_contrato = RepositorioContratoArrendamientoSQLite(db_manager)
            repo_propiedad = RepositorioPropiedadSQLite(db_manager)
            repo_asesor = RepositorioAsesorSQLite(db_manager)
            repo_persona = RepositorioPersonaSQLite(db_manager)
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
            logger.debug("✅ Servicio inicializado correctamente")

            logger.debug("📄 Paso 2: Generando PDF de cuenta de cobro...")
            pdf_path = servicio.generar_pdf_comprobante(id_liquidacion_asesor)
            logger.debug(f"✅ PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path

            logger.info("✅ PDF LIQUIDACIÓN ASESOR GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success("PDF de liquidación de asesor generado")

            # ESTRATEGIA ÉLITE: Fetch + Blob URL (same as Propietarios)
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            js_download = f"""
            fetch('{download_url}')
              .then(res => res.blob())
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            yield rx.call_script(js_download)

        except Exception as e:
            logger.error("❌ ERROR EN GENERACIÓN DE PDF LIQUIDACIÓN ASESOR")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error: {str(e)}")
        finally:
            self.generating = False
            logger.info("=" * 80)

    def generar_recibo_pago_pdf(self, id_recaudo: int):
        """
        Genera PDF de recibo de pago para un recaudo.

        Args:
            id_recaudo: ID del recaudo
        """
        logger.info("=" * 80)
        logger.info("🧾 INICIANDO GENERACIÓN DE PDF RECIBO DE PAGO")
        logger.info(f"ID Recaudo: {id_recaudo}")
        logger.info(f"Timestamp: {datetime.now()}")

        self.generating = True

        try:
            logger.debug("📊 Paso 1: Obteniendo datos del recaudo...")

            from src.infraestructura.persistencia.database import db_manager
            from src.infraestructura.persistencia.repositorio_recaudo_sqlite import (
                RepositorioRecaudoSQLite,
            )

            RepositorioRecaudoSQLite(db_manager)

            # Fetch recaudo with all related data
            placeholder = db_manager.get_placeholder()  # Get correct placeholder for DB type

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
                f"✅ Datos obtenidos: Recaudo {row['ID_RECAUDO']}, Valor ${row['VALOR_TOTAL']:,}"
            )

            # Debug: Log what keys are in conceptos_rows
            if conceptos_rows:
                logger.debug(f"📋 Conceptos keys: {list(conceptos_rows[0].keys())}")
                logger.debug(f"📋 First concepto: {conceptos_rows[0]}")

            # Get PERIODO from first concepto (defensive with .get())
            periodo = datetime.now().strftime("%Y-%m")  # Default
            if conceptos_rows:
                # Try different possible key names
                periodo = (
                    conceptos_rows[0].get("periodo") or conceptos_rows[0].get("PERIODO") or periodo
                )
            logger.debug(f"📅 Periodo usado: {periodo}")

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
                "matricula": row["MATRICULA_INMOBILIARIA"] or "Sin matrícula",
                "municipio": row.get("MUNICIPIO", "Armenia").upper(),
                "departamento": row.get("DEPARTAMENTO", "Quindío").upper(),
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
                "cuenta_bancaria": "No aplica", # Usually for payments made TO the entity
                "tipo_cuenta": row["METODO_PAGO"],
                "banco": "Caja General", # Default for cash
                # Notes with arrendatario info
                "observaciones": f"Arrendatario: {row['NOMBRE_ARRENDATARIO']} ({row['DOCUMENTO_ARRENDATARIO']}). {row['OBSERVACIONES'] or ''}".strip(),
                # Audit
                "created_at": datetime.now().isoformat(),
                "created_by": "Sistema",
            }
            
            # --- INYECTAR DATOS EMPRESA (LOGO) ---
            try:
                from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
                servicio_config = ServicioConfiguracion(db_manager)
                config_empresa = servicio_config.obtener_configuracion_empresa()
                
                if config_empresa:
                    datos_pdf["empresa"] = {
                        "nombre": config_empresa.nombre_empresa,
                        "nit": config_empresa.nit,
                        "direccion": config_empresa.direccion,
                        "telefono": config_empresa.telefono,
                        "email": config_empresa.email,
                        "logo_base64": config_empresa.logo_base64, # <--- CLAVE PARA EL LOGO
                        "website": config_empresa.website
                    }
                    # Copia directa para compatibilidad extra
                    datos_pdf["logo_base64"] = config_empresa.logo_base64
            except Exception as e:
                logger.error(f"⚠️ No se pudo cargar config empresa: {e}")

            logger.debug("📄 Paso 2: Generando PDF...")
            pdf_path = self.pdf_service.generar_recibo_recaudo_elite(datos_pdf)
            logger.debug(f"✅ PDF generado en: {pdf_path}")

            self.last_pdf_path = pdf_path

            logger.info("✅ PDF RECIBO DE PAGO GENERADO EXITOSAMENTE")
            logger.info(f"Path: {pdf_path}")

            yield rx.toast.success("Recibo de pago generado")

            # ESTRATEGIA ÉLITE: Fetch + Blob URL
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            js_download = f"""
            fetch('{download_url}')
              .then(res => res.blob())
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            yield rx.call_script(js_download)

        except Exception as e:
            logger.error("❌ ERROR EN GENERACIÓN DE PDF RECIBO DE PAGO")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")

            yield rx.toast.error(f"Error: {str(e)}")
        finally:
            self.generating = False
            logger.info("=" * 80)

    def _get_datos_liquidacion(self, id_liquidacion: int) -> Dict[str, Any]:
        """
        Obtiene datos de una liquidación desde la base de datos real.
        Se conecta directamente a ServicioFinanciero para obtener datos reales.

        Args:
            id_liquidacion: ID de la liquidación

        Returns:
            Diccionario con datos formateados para PDF

        Raises:
            ValueError: Si la liquidación no existe
        """
        from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
        from src.infraestructura.persistencia.database import db_manager
        
        # Importar repositorios requeridos para ServicioFinanciero
        from src.infraestructura.persistencia.repositorio_recaudo_sqlite import RepositorioRecaudoSQLite
        from src.infraestructura.persistencia.repositorio_liquidacion_sqlite import RepositorioLiquidacionSQLite
        from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite
        from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite
        from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
        
        # Instanciar dependencias
        repo_recaudo = RepositorioRecaudoSQLite(db_manager)
        repo_liquidacion = RepositorioLiquidacionSQLite(db_manager)
        repo_propiedad = RepositorioPropiedadSQLite(db_manager)
        repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
        repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
        servicio_pdf = ServicioDocumentosPDF()

        # Instanciar servicio financiero con todas sus dependencias
        servicio = ServicioFinanciero(
            repo_recaudo=repo_recaudo,
            repo_liquidacion=repo_liquidacion,
            repo_propiedad=repo_propiedad,
            repo_arriendo=repo_arriendo,
            repo_mandato=repo_mandato,
            pdf_service=servicio_pdf
        )

        # Get real liquidation data from database
        datos = servicio.obtener_datos_liquidacion_para_pdf(id_liquidacion)

        if not datos:
            raise ValueError(f"Liquidación {id_liquidacion} no encontrada")

        # --- OBTENER CONFIGURACIÓN DE EMPRESA ---
        from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
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
                "website": config_empresa.website
            }

        return datos

    def _get_datos_certificado(self, contrato_id: int, tipo: str = "paz_y_salvo") -> Dict[str, Any]:
        """
        Obtiene datos para certificado desde el repository

        PRODUCCIÓN: El MockPDFRepository ya tiene TODOs de cómo conectar a DB real
        """
        from src.infraestructura.servicios.pdf_elite.utils.mock_data_repository import (
            MockPDFRepository,
        )

        datos = MockPDFRepository.get_certificado_data(contrato_id, tipo)

        if not datos:
            raise ValueError(f"No se pudo generar certificado para contrato {contrato_id}")

        return datos


__all__ = ["PDFState"]
