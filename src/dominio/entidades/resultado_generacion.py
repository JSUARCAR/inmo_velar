from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class ResultadoGeneracionPropietario:
    """Resultado de la generación de liquidaciones para un propietario."""
    generadas: int = 0      # Liquidaciones creadas exitosamente
    omitidas: int = 0       # Contratos que ya tenían liquidación para el período
    errores: int = 0        # Fallos reales (datos inválidos, conexiones, etc.)
    no_elegibles: int = 0   # Contratos no elegibles (ej. sin arrendamiento activo)
    detalles_no_elegibles: List[str] = field(default_factory=list)
