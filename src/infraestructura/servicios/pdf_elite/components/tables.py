"""
Componente Avanzado de Tablas
==============================
Constructores de tablas profesionales con estilos predefinidos y personalizables.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Any, Dict, List, Optional, Tuple

from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle

from ..core.config import Colors, Fonts


class AdvancedTable:
    """
    Constructor de tablas avanzadas para PDFs

    Proporciona métodos estáticos para crear tablas con estilos profesionales
    siguiendo las mejores prácticas de diseño de documentos.
    """

    @staticmethod
    def create_data_table(
        headers: List[str],
        rows: List[List[Any]],
        totals: Optional[Dict[int, Any]] = None,
        col_widths: Optional[List[float]] = None,
        highlight_totals: bool = True,
        zebra_stripe: bool = False,
    ) -> Table:
        """
        Crea tabla de datos con headers y opcionalmente totales

        Args:
            headers: Lista de nombres de columnas
            rows: Lista de filas de datos
            totals: Dict {col_index: total_value} para fila de totales
            col_widths: Anchos personalizados de columnas en puntos
            highlight_totals: Resaltar fila de totales
            zebra_stripe: Alternar colores de filas (efecto zebra)

        Returns:
            Tabla configurada

        Example:
            >>> table = AdvancedTable.create_data_table(
            ...     headers=["Producto", "Cantidad", "Precio"],
            ...     rows=[["Item 1", "10", "$100"], ["Item 2", "5", "$50"]],
            ...     totals={1: "15", 2: "$150"}
            ... )
        """
        # Construir datos completos
        data = [headers] + rows

        # Agregar fila de totales si existe
        if totals:
            total_row = [""] * len(headers)
            for col_idx, value in totals.items():
                total_row[col_idx] = value
            data.append(total_row)

        # Crear tabla
        table = Table(data, colWidths=col_widths, repeatRows=1)

        # Comandos de estilo base
        style_commands = [
            # === HEADER ===
            ("BACKGROUND", (0, 0), (-1, 0), Colors.to_reportlab(Colors.PRIMARY)),
            ("TEXTCOLOR", (0, 0), (-1, 0), Colors.to_reportlab(Colors.WHITE)),
            ("FONTNAME", (0, 0), (-1, 0), Fonts.MAIN_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), Fonts.SIZE_BODY),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            # === BODY ===
            ("BACKGROUND", (0, 1), (-1, -1), Colors.to_reportlab(Colors.WHITE)),
            ("FONTNAME", (0, 1), (-1, -1), Fonts.MAIN),
            ("FONTSIZE", (0, 1), (-1, -1), Fonts.SIZE_SMALL),
            ("GRID", (0, 0), (-1, -1), 0.5, Colors.to_reportlab(Colors.GRAY_LIGHT)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ]

        # Efecto zebra (rayas alternadas)
        if zebra_stripe and len(rows) > 0:
            for row_idx in range(1, len(data) - (1 if totals else 0)):
                if row_idx % 2 == 0:
                    style_commands.append(
                        (
                            "BACKGROUND",
                            (0, row_idx),
                            (-1, row_idx),
                            Colors.to_reportlab(Colors.GRAY_LIGHTEST),
                        )
                    )

        # Estilo para fila de totales
        if totals and highlight_totals:
            last_row = len(data) - 1
            style_commands.extend(
                [
                    (
                        "BACKGROUND",
                        (0, last_row),
                        (-1, last_row),
                        Colors.to_reportlab(Colors.GRAY_LIGHT),
                    ),
                    ("FONTNAME", (0, last_row), (-1, last_row), Fonts.MAIN_BOLD),
                    ("FONTSIZE", (0, last_row), (-1, last_row), Fonts.SIZE_BODY),
                    (
                        "LINEABOVE",
                        (0, last_row),
                        (-1, last_row),
                        2,
                        Colors.to_reportlab(Colors.PRIMARY),
                    ),
                    ("TOPPADDING", (0, last_row), (-1, last_row), 8),
                    ("BOTTOMPADDING", (0, last_row), (-1, last_row), 8),
                ]
            )

        table.setStyle(TableStyle(style_commands))
        return table

    @staticmethod
    def create_key_value_table(
        data: Dict[str, Any],
        title: Optional[str] = None,
        key_width: float = 3 * inch,
        value_width: float = 4 * inch,
    ) -> Table:
        """
        Crea tabla de clave-valor para mostrar información

        Args:
            data: Diccionario con pares clave-valor
            title: Título opcional de la tabla
            key_width: Ancho de columna de claves
            value_width: Ancho de columna de valores

        Returns:
            Tabla configurada

        Example:
            >>> info = {"Nombre": "Juan", "Email": "juan@example.com"}
            >>> table = AdvancedTable.create_key_value_table(
            ...     info, title="Información del Usuario"
            ... )
        """
        rows = []

        # Agregar título si existe
        if title:
            rows.append([title, ""])

        # Agregar filas de datos
        for key, value in data.items():
            rows.append([str(key), str(value)])

        # Crear tabla
        table = Table(rows, colWidths=[key_width, value_width])

        # Comandos de estilo
        style_commands = [
            # Columna de claves (labels)
            ("FONTNAME", (0, 0), (0, -1), Fonts.MAIN_BOLD),
            ("FONTSIZE", (0, 0), (-1, -1), Fonts.SIZE_SMALL),
            ("BACKGROUND", (0, 0), (0, -1), Colors.to_reportlab(Colors.GRAY_LIGHTEST)),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            # Columna de valores
            ("FONTNAME", (1, 0), (1, -1), Fonts.MAIN),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            # General
            ("GRID", (0, 0), (-1, -1), 0.5, Colors.to_reportlab(Colors.GRAY_LIGHT)),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]

        # Estilo especial para título
        if title:
            style_commands.extend(
                [
                    ("SPAN", (0, 0), (1, 0)),
                    ("BACKGROUND", (0, 0), (1, 0), Colors.to_reportlab(Colors.PRIMARY)),
                    ("TEXTCOLOR", (0, 0), (1, 0), Colors.to_reportlab(Colors.WHITE)),
                    ("FONTNAME", (0, 0), (1, 0), Fonts.MAIN_BOLD),
                    ("FONTSIZE", (0, 0), (1, 0), Fonts.SIZE_HEADING_2),
                    ("ALIGN", (0, 0), (1, 0), "CENTER"),
                    ("TOPPADDING", (0, 0), (1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (1, 0), 10),
                ]
            )

        table.setStyle(TableStyle(style_commands))
        return table

    @staticmethod
    def create_minimal_table(
        data: List[List[Any]], col_widths: Optional[List[float]] = None
    ) -> Table:
        """
        Crea tabla con estilo minimalista (sin bordes)

        Args:
            data: Datos de la tabla
            col_widths: Anchos de columnas

        Returns:
            Tabla configurada
        """
        table = Table(data, colWidths=col_widths)

        style_commands = [
            # Primera fila como header
            ("FONTNAME", (0, 0), (-1, 0), Fonts.MAIN_BOLD),
            ("FONTSIZE", (0, 0), (-1, 0), Fonts.SIZE_BODY),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("LINEBELOW", (0, 0), (-1, 0), 1, Colors.to_reportlab(Colors.GRAY_DARK)),
            # Resto de filas
            ("FONTNAME", (0, 1), (-1, -1), Fonts.MAIN),
            ("FONTSIZE", (0, 1), (-1, -1), Fonts.SIZE_SMALL),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            # General
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]

        table.setStyle(TableStyle(style_commands))
        return table

    @staticmethod
    def create_signature_table(
        signatures: List[Tuple[str, str]], spacing: float = 2 * inch
    ) -> Table:
        """
        Crea tabla para bloques de firma

        Args:
            signatures: Lista de tuplas (label, nombre/documento)
            spacing: Espaciado entre firmas

        Returns:
            Tabla de firmas

        Example:
            >>> sigs = [
            ...     ("ARRENDADOR", "Juan Pérez\\nCC 123456"),
            ...     ("ARRENDATARIO", "María López\\nCC 789012")
            ... ]
            >>> table = AdvancedTable.create_signature_table(sigs)
        """
        num_sigs = len(signatures)

        # Líneas de firma
        lines_row = ["_" * 40] * num_sigs

        # Labels (en negrita)
        labels_row = [sig[0] for sig in signatures]

        # Nombres/Documentos
        names_row = [sig[1] for sig in signatures]

        # Crear tabla
        data = [lines_row, labels_row, names_row]
        table = Table(data, colWidths=[spacing] * num_sigs)

        style_commands = [
            # Líneas de firma
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, 0), 20),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
            # Labels
            ("FONTNAME", (0, 1), (-1, 1), Fonts.MAIN_BOLD),
            ("FONTSIZE", (0, 1), (-1, 1), Fonts.SIZE_SMALL),
            ("ALIGN", (0, 1), (-1, 1), "CENTER"),
            ("TOPPADDING", (0, 1), (-1, 1), 3),
            # Nombres/Documentos
            ("FONTNAME", (0, 2), (-1, 2), Fonts.MAIN),
            ("FONTSIZE", (0, 2), (-1, 2), Fonts.SIZE_SMALL),
            ("ALIGN", (0, 2), (-1, 2), "CENTER"),
            ("TOPPADDING", (0, 2), (-1, 2), 2),
        ]

        table.setStyle(TableStyle(style_commands))
        return table


__all__ = ["AdvancedTable"]
