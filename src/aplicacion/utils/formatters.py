"""
Utilidades de formateo para la capa de aplicación.
Funciones puras sin dependencias de frameworks de UI.
"""


def format_currency(amount: float) -> str:
    """
    Formatea un valor numérico como moneda (ej: 1000000 -> "$1.000.000").
    Maneja None retornando "$0".
    """
    if amount is None:
        return "$0"

    try:
        # Convertir a float por seguridad si viene como string
        val = float(amount)
        formatted = f"{val:,.0f}"
        return f"${formatted.replace(',', '.')}"
    except (ValueError, TypeError):
        return "$0"


def format_number(value: float, decimals: int = 1) -> str:
    """
    Formatea un número con punto para miles y coma para decimales.
    Ejemplo: 34.5 -> "34,5"
    """
    if value is None:
        return "0"

    try:
        val = float(value)
        # Usar un marcador temporal para no confundir puntos y comas durante el reemplazo
        formatted = f"{val:,.{decimals}f}"

        # 1,234.56 -> 1.234,56
        # Reemplazamos coma por marcador, punto por coma, marcador por punto.
        result = (
            formatted.replace(",", " TEMP ").replace(".", ",").replace(" TEMP ", ".")
        )

        return result
    except (ValueError, TypeError):
        return "0"
