"""
Validadores de rango para la renovación de contratos.

Gate en dos niveles (spec 073, FR-003):
  1. Máximos operativos (canon, comisión).
  2. Límite int4 como red de seguridad para todo valor derivado.
"""

from src.dominio.excepciones.excepciones_base import ValorFueraDeRangoError

CANON_MAXIMO = 10_000_000
COMISION_MAXIMA = 1500
INT4_MAXIMO = 2_147_483_647


def _validar(campo: str, valor: int, maximo: int) -> None:
    """
    Args:
        campo: Nombre del campo validado.
        valor: Valor a validar.
        maximo: Máximo permitido.

    Raises:
        ValorFueraDeRangoError: Si el valor excede el máximo.
    """
    if valor > maximo:
        raise ValorFueraDeRangoError(campo, valor, maximo)


def validar_canon(canon: int) -> None:
    """
    Valida el canon contra el máximo operativo.

    Args:
        canon: Canon de arrendamiento/mandato.

    Raises:
        ValorFueraDeRangoError: Si excede CANON_MAXIMO.
    """
    _validar("canon_arrendamiento", canon, CANON_MAXIMO)


def validar_comision(comision: int) -> None:
    """
    Valida la comisión contra el máximo operativo.

    Args:
        comision: Porcentaje de comisión en base 10000.

    Raises:
        ValorFueraDeRangoError: Si excede COMISION_MAXIMA.
    """
    _validar("comision_porcentaje", comision, COMISION_MAXIMA)


def validar_derivado(campo: str, valor: int) -> None:
    """
    Valida un valor derivado contra el límite int4 (red de seguridad).

    Args:
        campo: Nombre del campo derivado.
        valor: Valor derivado calculado.

    Raises:
        ValorFueraDeRangoError: Si excede INT4_MAXIMO.
    """
    _validar(campo, valor, INT4_MAXIMO)
