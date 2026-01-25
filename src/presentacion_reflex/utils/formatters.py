
import reflex as rx

def format_currency(amount: float) -> str:
    """
    Formatea un valor flotante como moneda con punto para miles y coma para decimales.
    Ejemplo: 10176000.0 -> "$10.176.000"
    """
    if amount is None:
        return "$0"
    
    # Formatear con comas para miles y puntos para decimales primero (estándar python/en)
    # Luego intercambiar para cumplir con la solicitud del usuario (estándar es/co)
    formatted = f"{amount:,.0f}"
    return f"${formatted.replace(',', '.')}"

def format_number(value: float, decimals: int = 1) -> str:
    """
    Formatea un número con punto para miles y coma para decimales.
    Ejemplo: 34.5 -> "34,5"
    """
    if value is None:
        return "0"
        
    # Usar un marcador temporal para no confundir puntos y comas durante el reemplazo
    formatted = f"{value:,.{decimals}f}"
    
    # 1,234.56 -> 1.234,56
    # Reemplazamos coma por marcador, punto por coma, marcador por punto.
    result = formatted.replace(',', ' TEMP ').replace('.', ',').replace(' TEMP ', '.')
    
    # Si termina en ,0 y no se pidieron decimales explícitamente mayores a 0, remover
    if decimals == 0 and result.endswith(',0'):
        result = result[:-2]
        
    return result
