class CacheKeys:
    """Claves centralizadas para invalidación de caché"""
    # Arrendamientos
    ARRIENDOS_LIST = "arriendos:list_paginated"
    
    # Mandatos
    MANDATOS_LIST = "mandatos:list_paginated"
    
    # Propiedades
    PROPIEDADES_LIST = "propiedades:list_paginated"
    PROPIEDADES_BASE_LIST = "propiedades:list"
    DASHBOARD_PROPIEDADES_TIPO = "dashboard:propiedades_tipo"
    
    @staticmethod
    def propiedad(id_propiedad: int) -> str:
        return f"propiedad:{id_propiedad}"
