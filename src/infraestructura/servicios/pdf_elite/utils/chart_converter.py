"""
Conversor de Gráficos para PDFs
================================
Utilidad para convertir gráficos Plotly a imágenes para insertar en PDFs.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Optional, Literal
from pathlib import Path
from io import BytesIO
import tempfile

try:
    import plotly.graph_objects as go
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class ChartConverter:
    """
    Conversor de gráficos Plotly a imágenes
    
    Convierte gráficos Plotly a formato PNG para insertar en PDFs de ReportLab.
    """
    
    @staticmethod
    def plotly_to_image(
        fig: 'go.Figure',
        width: int = 600,
        height: int = 400,
        format: Literal['png', 'jpeg'] = 'png',
        scale: float = 2.0
    ) -> BytesIO:
        """
        Convierte gráfico Plotly a imagen
        
        Args:
            fig: Figura de Plotly
            width: Ancho en píxeles
            height: Alto en píxeles
            format: Formato de salida ('png' o 'jpeg')
            scale: Escala de resolución (2.0 = alta calidad)
            
        Returns:
            BytesIO con la imagen
            
        Raises:
            ImportError: Si Plotly no está disponible
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError(
                "Plotly no está instalado. "
                "Instale con: pip install plotly kaleido"
            )
        
        # Convertir a bytes
        img_bytes = pio.to_image(
            fig,
            format=format,
            width=width,
            height=height,
            scale=scale
        )
        
        # Retornar como BytesIO
        buffer = BytesIO(img_bytes)
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def save_plotly_chart(
        fig: 'go.Figure',
        output_path: Path,
        width: int = 800,
        height: int = 600
    ) -> None:
        """
        Guarda gráfico Plotly a archivo
        
        Args:
            fig: Figura de Plotly
            output_path: Path donde guardar
            width: Ancho en píxeles
            height: Alto en píxeles
        """
        img_buffer = ChartConverter.plotly_to_image(fig, width, height)
        
        with open(output_path, 'wb') as f:
            f.write(img_buffer.getvalue())
    
    @staticmethod
    def create_sample_chart() -> Optional['go.Figure']:
        """
        Crea gráfico de muestra para testing
        
        Returns:
            Figura de Plotly o None si no está disponible
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        # Gráfico de barras simple
        fig = go.Figure(data=[
            go.Bar(
                x=['Enero', 'Febrero', 'Marzo', 'Abril'],
                y=[100, 150, 120, 180],
                marker_color='rgb(51, 77, 153)'
            )
        ])
        
        fig.update_layout(
            title="Ingresos Mensuales",
            xaxis_title="Mes",
            yaxis_title="Valor ($)",
            template="plotly_white",
            height=400,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        return fig


__all__ = ['ChartConverter']
