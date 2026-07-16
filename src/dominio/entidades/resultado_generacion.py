from dataclasses import dataclass

@dataclass(frozen=True)
class ResultadoGeneracionPropietario:
    """Resultado de la generación de liquidaciones para un propietario."""
    generadas: int = 0      # Liquidaciones creadas exitosamente
    omitidas: int = 0       # Contratos que ya tenían liquidación para el período
    errores: int = 0        # Fallos reales (datos inválidos, conexiones, etc.)
