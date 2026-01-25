"""
Entidad: ConfiguracionEmpresa

Representa la configuración global de la empresa/inmobiliaria.
Mapeo a la tabla: configuracion_sistema
"""

import json
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ConfiguracionEmpresa:
    """
    Entidad que representa la configuración y datos de la empresa.
    Tabla: configuracion_sistema
    """

    id: Optional[int] = None
    nombre_empresa: str = ""
    nit: str = ""
    email: str = ""
    telefono: str = ""
    direccion: str = ""
    ubicacion: str = ""
    website: str = ""
    redes_sociales: str = "{}"  # Almacenado como JSON string en BD

    # Representante Legal
    representante_legal: str = ""
    cedula_representante: str = ""

    # Logo
    logo_base64: str = ""  # Logo codificado en Base64
    logo_filename: str = ""  # Nombre original del archivo

    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def redes_sociales_dict(self) -> Dict:
        """Retorna redes sociales como diccionario."""
        try:
            return json.loads(self.redes_sociales) if self.redes_sociales else {}
        except json.JSONDecodeError:
            return {}

    def set_redes_sociales_from_dict(self, redes: Dict) -> None:
        """Establece redes sociales desde un diccionario."""
        self.redes_sociales = json.dumps(redes)
