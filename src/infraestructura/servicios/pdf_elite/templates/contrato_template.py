"""
Template para Contratos de Arrendamiento
=========================================
Generador élite de contratos con cláusulas, firmas y verificación QR.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from pathlib import Path
from typing import Any, Dict

from ..components.tables import AdvancedTable
from ..utils.validators import DataValidator
from .base_template import BaseDocumentTemplate


class ContratoArrendamientoElite(BaseDocumentTemplate):
    """
    Generador élite de contratos de arrendamiento

    Crea contratos profesionales con:
    - Header con información del contrato
    - Cláusulas numeradas y formateadas
    - Tabla de condiciones económicas
    - Bloques de firma para las partes
    - QR de verificación
    - Marca de agua opcional para borradores

    Example:
        >>> gen = ContratoArrendamientoElite()
        >>> data = {
        ...     'contrato_id': 123,
        ...     'fecha': '2026-01-18',
        ...     'arrendador': {...},
        ...     'arrendatario': {...},
        ...     'inmueble': {...},
        ...     'condiciones': {...},
        ...     'clausulas': [...]
        ... }
        >>> pdf_path = gen.generate(data)
    """

    # Cláusulas estándar por defecto
    CLAUSULAS_ESTANDAR = [
        {
            "numero": 1,
            "titulo": "OBJETO DEL CONTRATO",
            "texto": "El ARRENDADOR da en arrendamiento al ARRENDATARIO el inmueble descrito, "
            "quien lo recibe a satisfacción para destinarlo exclusivamente a vivienda familiar.",
        },
        {
            "numero": 2,
            "titulo": "DURACIÓN Y PRÓRROGA",
            "texto": "El término de duración del presente contrato es de {duracion} meses, "
            "contados a partir de la fecha de entrega del inmueble. Este contrato se "
            "prorrogará automáticamente por períodos iguales, salvo manifestación en contrario "
            "de cualquiera de las partes con {preaviso} días de anticipación.",
        },
        {
            "numero": 3,
            "titulo": "CANON DE ARRENDAMIENTO",
            "texto": "El canon de arrendamiento mensual es de {canon}, pagadero dentro de los "
            "primeros {dia_pago} días de cada mes. El pago se realizará en la cuenta "
            "bancaria indicada por el ARRENDADOR.",
        },
        {
            "numero": 4,
            "titulo": "SERVICIOS PÚBLICOS",
            "texto": "El ARRENDATARIO se obliga a pagar oportunamente los servicios públicos del "
            "inmueble arrendado. Cualquier falta de pago será causal de terminación del contrato.",
        },
        {
            "numero": 5,
            "titulo": "REPARACIONES Y MANTENIMIENTO",
            "texto": "Las reparaciones locativas estarán a cargo del ARRENDATARIO. Las reparaciones "
            "estructurales o de instalaciones esenciales serán responsabilidad del ARRENDADOR.",
        },
        {
            "numero": 6,
            "titulo": "PROHIBICIONES",
            "texto": "El ARRENDATARIO no podrá subarrendar, ceder o traspasar el inmueble, ni "
            "destinarlo a usos diferentes al pactado, sin autorización previa y escrita del ARRENDADOR.",
        },
        {
            "numero": 7,
            "titulo": "TERMINACIÓN",
            "texto": "Son causales de terminación del contrato: mora superior a 2 meses, destinación "
            "diferente, subarriendo sin autorización, deterioro del inmueble por negligencia, "
            "o cualquier otra causal establecida en la ley.",
        },
    ]

    def __init__(self, output_dir: Path = None):
        """Inicializa el generador de contratos"""
        super().__init__(output_dir)
        self.document_title = "CONTRATO DE ARRENDAMIENTO DE VIVIENDA URBANA"

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida datos del contrato (soporta Arrendamiento y Mandato)

        Args:
            data: Datos del contrato

        Returns:
            True si son válidos

        Raises:
            ValueError: Si hay errores de validación
        """
        # Detectar tipo de contrato
        es_mandato = data.get("tipo_contrato") == "MANDATO"

        # Campos requeridos base
        required_base = ["contrato_id", "fecha", "inmueble", "condiciones"]

        # Campos específicos según tipo
        if es_mandato:
            required = required_base + ["mandante", "inmobiliaria"]
        else:
            required = required_base + ["arrendador", "arrendatario"]

        is_valid, missing = DataValidator.validate_required_fields(data, required)
        if not is_valid:
            raise ValueError(f"Campos requeridos faltantes: {', '.join(missing)}")

        # Validar subestructuras según tipo
        if es_mandato:
            self._require_fields(data["mandante"], "nombre", "documento", "telefono")
            self._require_fields(data["inmobiliaria"], "nombre")
        else:
            self._require_fields(data["arrendador"], "nombre", "documento", "telefono")
            self._require_fields(data["arrendatario"], "nombre", "documento", "telefono")

        self._require_fields(data["inmueble"], "direccion", "tipo")
        self._require_fields(data["condiciones"], "duracion_meses")

        # Validar valor monetario (canon en arrendamiento, comisión en mandato)
        if es_mandato:
            if "comision" in data["condiciones"]:
                if not DataValidator.validate_money_amount(data["condiciones"]["comision"]):
                    raise ValueError("Comisión inválida")
        else:
            if not DataValidator.validate_money_amount(data["condiciones"]["canon"]):
                raise ValueError("Canon de arrendamiento inválido")

        return True

    def generate(self, data: Dict[str, Any]) -> Path:
        """
        Genera el contrato en PDF

        Args:
            data: Diccionario con datos del contrato

        Returns:
            Path del PDF generado
        """
        # Habilitar QR de verificación
        self.enable_verification_qr("contrato", data["contrato_id"])

        # Marca de agua si es borrador
        if data.get("estado") == "borrador":
            self.set_watermark("BORRADOR", opacity=0.12)

        # Crear documento
        filename = self._generate_filename("contrato", data["contrato_id"])
        self.create_document(filename, self.document_title)

        # Construir contenido
        self._add_header_section(data)
        self._add_partes_section(data)
        self._add_inmueble_section(data)
        self._add_condiciones_economicas(data)
        self._add_clausulas(data)
        self._add_firmas(data)

        # Construir PDF
        return self.build()

    def _add_header_section(self, data: Dict[str, Any]) -> None:
        """Agrega header del contrato"""
        # Título principal
        self.add_title_main(self.document_title)

        # Información del contrato
        self.add_document_info_header(
            doc_number=f"No. {data['contrato_id']:06d}",
            doc_date=data["fecha"],
            doc_status=data.get("estado", "Vigente").upper(),
        )

    def _add_partes_section(self, data: Dict[str, Any]) -> None:
        """Agrega información de las partes (adaptable a Arrendamiento/Mandato)"""
        self.add_section_divider("PARTES CONTRATANTES")

        es_mandato = data.get("tipo_contrato") == "MANDATO"

        if es_mandato:
            # MANDATO: Mandante e Inmobiliaria
            mandante = data["mandante"]
            inmobiliaria = data["inmobiliaria"]

            # Información del mandante (propietario)
            self.add_heading("MANDANTE (PROPIETARIO)", level=2)
            mandante_info = {
                "Nombre": mandante["nombre"],
                "Documento": mandante["documento"],
                "Teléfono": mandante["telefono"],
                "Email": mandante.get("email", "N/A"),
                "Dirección": mandante.get("direccion", "N/A"),
            }
            table = AdvancedTable.create_key_value_table(mandante_info)
            self.story.append(table)
            self.add_spacer(0.2)

            # Información de la inmobiliaria
            self.add_heading("MANDATARIO (INMOBILIARIA)", level=2)
            inmobiliaria_info = {
                "Nombre": inmobiliaria["nombre"],
                "NIT": inmobiliaria.get("nit", "N/A"),
                "Teléfono": inmobiliaria.get("telefono", "N/A"),
                "Email": inmobiliaria.get("email", "N/A"),
                "Dirección": inmobiliaria.get("direccion", "N/A"),
            }
            table = AdvancedTable.create_key_value_table(inmobiliaria_info)
            self.story.append(table)
            self.add_spacer(0.3)
        else:
            # ARRENDAMIENTO: Arrendador y Arrendatario
            arrendador = data["arrendador"]
            arrendatario = data["arrendatario"]

            # Información del arrendador
            self.add_heading("ARRENDADOR", level=2)
            arrendador_info = {
                "Nombre": arrendador["nombre"],
                "Documento": arrendador["documento"],
                "Teléfono": arrendador["telefono"],
                "Email": arrendador.get("email", "N/A"),
                "Dirección": arrendador.get("direccion", "N/A"),
            }
            table = AdvancedTable.create_key_value_table(arrendador_info)
            self.story.append(table)
            self.add_spacer(0.2)

            # Información del arrendatario
            self.add_heading("ARRENDATARIO", level=2)
            arrendatario_info = {
                "Nombre": arrendatario["nombre"],
                "Documento": arrendatario["documento"],
                "Teléfono": arrendatario["telefono"],
                "Email": arrendatario.get("email", "N/A"),
                "Dirección": arrendatario.get("direccion", "N/A"),
            }
            table = AdvancedTable.create_key_value_table(arrendatario_info)
            self.story.append(table)
            self.add_spacer(0.3)

    def _add_inmueble_section(self, data: Dict[str, Any]) -> None:
        """Agrega información del inmueble"""
        self.add_section_divider("INMUEBLE ARRENDADO")

        inmueble = data["inmueble"]

        inmueble_info = {
            "Dirección": inmueble["direccion"],
            "Tipo": inmueble["tipo"],
            "Área (m²)": inmueble.get("area", "N/A"),
            "Habitaciones": inmueble.get("habitaciones", "N/A"),
            "Baños": inmueble.get("banos", "N/A"),
            "Estrato": inmueble.get("estrato", "N/A"),
        }

        table = AdvancedTable.create_key_value_table(inmueble_info)
        self.story.append(table)
        self.add_spacer(0.3)

    def _add_condiciones_economicas(self, data: Dict[str, Any]) -> None:
        """Agrega condiciones económicas (adaptable a Arrendamiento/Mandato)"""
        self.add_section_divider("CONDICIONES ECONÓMICAS")

        cond = data["condiciones"]
        es_mandato = data.get("tipo_contrato") == "MANDATO"

        if es_mandato:
            # MANDATO: Comisión y valor sugerido
            comision = f"${cond.get('comision', 0):,.2f}"
            valor_sugerido = f"${cond.get('valor_canon_sugerido', 0):,.2f}"

            headers = ["Concepto", "Valor", "Periodicidad"]
            rows = [
                ["Comisión de Administración", comision, "Mensual"],
                ["Valor Canon Sugerido", valor_sugerido, "Referencia"],
            ]

            table = AdvancedTable.create_data_table(headers, rows, zebra_stripe=True)
            self.story.append(table)
        else:
            # ARRENDAMIENTO: Canon, administración, depósito
            canon = f"${cond.get('canon', 0):,.2f}"
            deposito = f"${cond.get('deposito', 0):,.2f}"
            admin = f"${cond.get('administracion', 0):,.2f}"

            headers = ["Concepto", "Valor", "Periodicidad"]
            rows = [
                ["Canon de Arrendamiento", canon, "Mensual"],
                ["Administración", admin, "Mensual"],
                ["Depósito en Garantía", deposito, "Única vez"],
            ]

            # Calcular total mensual
            total_mensual = cond.get("canon", 0) + cond.get("administracion", 0)
            totals = {1: f"${total_mensual:,.2f}"}

            table = AdvancedTable.create_data_table(headers, rows, totals=totals, zebra_stripe=True)
            self.story.append(table)

        # Detalles adicionales
        self.add_spacer(0.2)
        self.add_paragraph(f"<b>Duración:</b> {cond['duracion_meses']} meses", style_name="Body")
        if not es_mandato:
            self.add_paragraph(
                f"<b>Día de Pago:</b> Primeros {cond.get('dia_pago', 5)} días del mes",
                style_name="Body",
            )
            self.add_paragraph(
                "<b>Incremento Anual:</b> IPC certificado por el DANE", style_name="Body"
            )
        self.add_spacer(0.3)

    def _add_clausulas(self, data: Dict[str, Any]) -> None:
        """Agrega cláusulas del contrato"""
        self.add_section_divider("CLÁUSULAS")

        # Usar cláusulas personalizadas o estándar
        clausulas = data.get("clausulas", self.CLAUSULAS_ESTANDAR)

        # Detectar tipo de contrato para variables
        es_mandato = data.get("tipo_contrato") == "MANDATO"

        # Variables para reemplazo en cláusulas
        if es_mandato:
            # Variables para contratos de mandato
            variables = {
                "duracion": str(data["condiciones"]["duracion_meses"]),
                "canon": f"${data['condiciones'].get('comision', 0):,.2f}",  # Usar comisión
                "preaviso": "30",
                "dia_pago": str(data["condiciones"].get("dia_pago", 5)),
            }
        else:
            # Variables para contratos de arrendamiento
            variables = {
                "duracion": str(data["condiciones"]["duracion_meses"]),
                "canon": f"${data['condiciones']['canon']:,.2f}",
                "preaviso": "30",
                "dia_pago": str(data["condiciones"].get("dia_pago", 5)),
            }

        for clausula in clausulas:
            # Título de la cláusula
            titulo = f"CLÁUSULA {clausula['numero']}: {clausula['titulo']}"
            self.add_heading(titulo, level=2)

            # Texto de la cláusula (con reemplazo de variables)
            texto = clausula["texto"]
            for var, valor in variables.items():
                texto = texto.replace(f"{{{var}}}", valor)

            self.add_paragraph(texto, style_name="Body")
            self.add_spacer(0.15)

        self.add_spacer(0.2)

    def _add_firmas(self, data: Dict[str, Any]) -> None:
        """Agrega bloques de firma (adaptable a Arrendamiento/Mandato)"""
        self.add_section_divider()

        es_mandato = data.get("tipo_contrato") == "MANDATO"

        # Texto de aceptación
        self.add_paragraph(
            "En constancia de lo anterior, las partes firman el presente contrato "
            "en la ciudad de Bogotá D.C., a los {fecha}.".format(fecha=data["fecha"]),
            style_name="Body",
        )

        self.add_spacer(0.4)

        # Tabla de firmas según tipo
        if es_mandato:
            signatures = [
                ("MANDANTE", f"{data['mandante']['nombre']}\n{data['mandante']['documento']}"),
                (
                    "MANDATARIO",
                    f"{data['inmobiliaria']['nombre']}\n{data['inmobiliaria'].get('nit', 'N/A')}",
                ),
            ]
        else:
            signatures = [
                (
                    "ARRENDADOR",
                    f"{data['arrendador']['nombre']}\n{data['arrendador']['documento']}",
                ),
                (
                    "ARRENDATARIO",
                    f"{data['arrendatario']['nombre']}\n{data['arrendatario']['documento']}",
                ),
            ]

        # Agregar testigo si existe
        if "testigo" in data:
            signatures.append(
                ("TESTIGO", f"{data['testigo']['nombre']}\n{data['testigo']['documento']}")
            )

        table = AdvancedTable.create_signature_table(signatures)
        self.story.append(table)

        # Pie legal
        self.add_legal_footer_text(
            "Este documento ha sido generado electrónicamente por Inmobiliaria Velar SAS. "
            "Verifique su autenticidad escaneando el código QR."
        )


__all__ = ["ContratoArrendamientoElite"]
