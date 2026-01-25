"""
Constantes: Tipos de Propiedad

Define los tipos de inmuebles gestionados en el sistema.
"""

from enum import Enum


class TipoPropiedad(str, Enum):
    """
    Clasificación de inmuebles.

    - APARTAMENTO: Apartamento residencial
    - CASA: Casa residencial
    - LOCAL_COMERCIAL: Local para comercio
    - OFICINA: Oficina corporativa
    - BODEGA: Bodega industrial/almacenamiento
    - LOTE: Terreno sin construcción
    - FINCA: Propiedad rural
    """

    APARTAMENTO = "APARTAMENTO"
    CASA = "CASA"
    LOCAL_COMERCIAL = "LOCAL_COMERCIAL"
    OFICINA = "OFICINA"
    BODEGA = "BODEGA"
    LOTE = "LOTE"
    FINCA = "FINCA"


class TipoNegocio(str, Enum):
    """
    Tipo de negocio inmobiliario.

    - ARRIENDO: Arrendamiento/alquiler
    - VENTA: Venta del inmueble
    - ARRIENDO_VENTA: Disponible para ambos
    """

    ARRIENDO = "ARRIENDO"
    VENTA = "VENTA"
    ARRIENDO_VENTA = "ARRIENDO_VENTA"
