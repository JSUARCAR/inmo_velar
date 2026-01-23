"""
Template para Estados de Cuenta Élite
=====================================
Generador mejorado de estados de cuenta con gráficos y análisis.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .base_template import BaseDocumentTemplate
from ..components.tables import AdvancedTable
from ..core.config import Colors


class EstadoCuentaElite(BaseDocumentTemplate):
    """
    Generador élite de estados de cuenta
    
    Mejora sobre el estado de cuenta básico con:
    - Tabla de movimientos profesional
    - Resumen de totales destacado
    - Gráficos opcionales de evolución
    - QR de verificación
    - Formato profesional
    
    Example:
        >>> gen = EstadoCuentaElite()
        >>> data = {
        ...     'estado_id': 789,
        ...     'propietario': {...},
        ...     'inmueble': {...},
        ...     'periodo': '2026-01',
        ...     'movimientos': [...],
        ...     'resumen': {...}
        ... }
        >>> pdf_path = gen.generate(data)
    """
    
    def __init__(self, output_dir: Path = None):
        """Inicializa el generador de estados de cuenta"""
        super().__init__(output_dir)
        self.document_title = "ESTADO DE CUENTA - PROPIETARIO"
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida datos del estado de cuenta"""
        self._require_fields(
            data,
            'estado_id', 'propietario', 'inmueble',
            'periodo', 'movimientos', 'resumen'
        )
        return True
    
    def generate(self, data: Dict[str, Any]) -> Path:
        """
        Genera el estado de cuenta en PDF
        
        Args:
            data: Diccionario con datos del estado
            
        Returns:
            Path del PDF generado
        """
        # Habilitar QR de verificación
        self.enable_verification_qr('estado', data['estado_id'])
        
        # Crear documento
        filename = self._generate_filename('estado_cuenta', data['estado_id'])
        self.create_document(filename, self.document_title)
        
        # Construir contenido
        self._add_header_estado(data)
        self._add_info_propietario(data)
        self._add_info_inmueble(data)
        self._add_movimientos(data)
        self._add_resumen_financiero(data)
        self._add_notas(data)
        
        # Construir PDF
        return self.build()
    
    def _add_header_estado(self, data: Dict[str, Any]) -> None:
        """Agrega header del estado de cuenta"""
        self.add_title_main(self.document_title)
        
        # Período y número
        self.add_document_info_header(
            doc_number=f"No. {data['estado_id']:06d}",
            doc_date=f"Período: {data['periodo']}"
        )
    
    def _add_info_propietario(self, data: Dict[str, Any]) -> None:
        """Agrega información del propietario"""
        self.add_heading("INFORMACIÓN DEL PROPIETARIO", level=2)
        
        prop = data['propietario']
        
        prop_info = {
            "Nombre": prop['nombre'],
            "Documento": prop['documento'],
            "Teléfono": prop.get('telefono', 'N/A'),
            "Email": prop.get('email', 'N/A')
        }
        
        table = AdvancedTable.create_key_value_table(prop_info)
        self.story.append(table)
        self.add_spacer(0.2)
    
    def _add_info_inmueble(self, data: Dict[str, Any]) -> None:
        """Agrega información del inmueble"""
        self.add_heading("INMUEBLE", level=2)
        
        inmueble = data['inmueble']
        
        inmueble_info = {
            "Dirección": inmueble['direccion'],
            "Tipo": inmueble.get('tipo', 'Apartamento'),
            "Canon Actual": f"${inmueble.get('canon', 0):,.2f}"
        }
        
        # Agregar arrendatario si está arrendado
        if 'arrendatario' in inmueble:
            inmueble_info["Arrendatario"] = inmueble['arrendatario']
        
        table = AdvancedTable.create_key_value_table(inmueble_info)
        self.story.append(table)
        self.add_spacer(0.3)
    
    def _add_movimientos(self, data: Dict[str, Any]) -> None:
        """Agrega tabla de movimientos"""
        self.add_section_divider("DETALLE DE MOVIMIENTOS")
        
        movimientos = data['movimientos']
        
        # Headers de la tabla
        headers = ["Fecha", "Concepto", "Ingresos", "Egresos", "Saldo"]
        
        # Convertir movimientos a filas
        rows = []
        saldo_acumulado = 0
        
        for mov in movimientos:
            fecha = mov.get('fecha', '')
            concepto = mov.get('concepto', '')
            ingreso = mov.get('ingreso', 0)
            egreso = mov.get('egreso', 0)
            
            # Calcular saldo acumulado
            saldo_acumulado += (ingreso - egreso)
            
            # Formatear valores
            ingreso_str = f"${ingreso:,.2f}" if ingreso > 0 else "-"
            egreso_str = f"${egreso:,.2f}" if egreso > 0 else "-"
            saldo_str = f"${saldo_acumulado:,.2f}"
            
            rows.append([fecha, concepto, ingreso_str, egreso_str, saldo_str])
        
        # Crear tabla con zebra striping
        table = AdvancedTable.create_data_table(
            headers, rows,
            zebra_stripe=True
        )
        self.story.append(table)
        self.add_spacer(0.3)
    
    def _add_resumen_financiero(self, data: Dict[str, Any]) -> None:
        """Agrega resumen financiero"""
        self.add_section_divider("RESUMEN FINANCIERO")
        
        resumen = data['resumen']
        
        # Tabla de resumen
        headers = ["Concepto", "Valor"]
        rows = [
            ["Total Ingresos", f"${resumen.get('total_ingresos', 0):,.2f}"],
            ["Total Egresos", f"${resumen.get('total_egresos', 0):,.2f}"],
            ["Honorarios Administración", f"${resumen.get('honorarios', 0):,.2f}"],
            ["Otros Descuentos", f"${resumen.get('otros_descuentos', 0):,.2f}"]
        ]
        
        # Valor neto
        valor_neto = resumen.get('valor_neto', 0)
        totals = {1: f"${valor_neto:,.2f}"}
        
        table = AdvancedTable.create_data_table(
            headers, rows,
            totals=totals,
            highlight_totals=True
        )
        self.story.append(table)
        
        # Información de transferencia si hay valor positivo
        if 'cuenta_bancaria' in resumen and valor_neto > 0:
            self.add_spacer(0.2)
            self.add_paragraph(
                f"Valor a Transferir: ${valor_neto:,.2f}",
                style_name='Body'
            )
            self.add_paragraph(
                f"Cuenta Bancaria: {resumen['cuenta_bancaria']}",
                style_name='Body'
            )
            
            if 'fecha_pago' in resumen:
                self.add_paragraph(
                    f"Fecha de Pago: {resumen['fecha_pago']}",
                    style_name='Body'
                )
        
        self.add_spacer(0.3)
    
    def _add_notas(self, data: Dict[str, Any]) -> None:
        """Agrega notas y observaciones"""
        if 'notas' in data and data['notas']:
            self.add_heading("OBSERVACIONES", level=2)
            
            notas = data['notas']
            if isinstance(notas, list):
                for nota in notas:
                    self.add_paragraph(f"• {nota}", style_name='Small')
            else:
                self.add_paragraph(notas, style_name='Small')
        
        # Pie legal
        self.add_legal_footer_text(
            "Este estado de cuenta ha sido generado electrónicamente. "
            "Para consultas contacte a Inmobiliaria Velar SAS."
        )


__all__ = ['EstadoCuentaElite']
