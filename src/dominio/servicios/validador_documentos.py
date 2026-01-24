from typing import Dict, Any, List, Optional
from src.dominio.constantes.tipos_documento import TIPOS_DOCUMENTO_MODULO

class ValidadorDocumentos:
    """
    Servicio de dominio para validar reglas de negocio sobre documentos.
    """

    @staticmethod
    def obtener_reglas_modulo(entidad_tipo: str) -> Optional[Dict[str, Any]]:
        """Obtiene la configuración de tipos para un módulo."""
        return TIPOS_DOCUMENTO_MODULO.get(entidad_tipo)

    @staticmethod
    def validar_archivo_generico(entidad_tipo: str, nombre_archivo: str, tamano_bytes: int) -> Dict[str, Any]:
        """
        Valida un archivo contra TODAS las reglas posibles del módulo.
        Si cumple al menos una configuración (ej. es un PDF válido para 'contrato' O para 'cedula'), se acepta.
        
        Retorna: {'valido': bool, 'mensaje': str}
        """
        reglas_modulo = ValidadorDocumentos.obtener_reglas_modulo(entidad_tipo)
        
        if not reglas_modulo:
            # Si el módulo no tiene reglas definidas, ¿Permitimos o denegamos?
            # Por seguridad, si no hay reglas, denegamos. O definimos un default.
            # Asumiremos que si está en la constante, se valida. Si no, ERROR CONFIG.
            return {'valido': False, 'mensaje': f"Configuración no encontrada para módulo {entidad_tipo}"}

        extension = "." + nombre_archivo.split(".")[-1].lower() if "." in nombre_archivo else ""
        if not extension:
             return {'valido': False, 'mensaje': "El archivo no tiene extensión"}

        # Estrategia Agregada:
        # 1. Buscar si la extensión está permitida en ALGUN tipo
        # 2. Si está permitida, verificar si el tamaño cumple el MÁXIMO de esos tipos compatibles
        
        tipos_compatibles = []
        max_size_permitido = 0
        
        for tipo_key, reglas in reglas_modulo.items():
            if extension in reglas.get('tipos', []):
                tipos_compatibles.append(tipo_key)
                max_size_permitido = max(max_size_permitido, reglas.get('max_size', 0))
        
        if not tipos_compatibles:
            # Recopilar extensiones permitidas para mensaje amigable
            exts = set()
            for r in reglas_modulo.values():
                for e in r.get('tipos', []):
                    exts.add(e)
            return {
                'valido': False, 
                'mensaje': f"Tipo de archivo {extension} no permitido en {entidad_tipo}. Permitidos: {', '.join(sorted(exts))}"
            }

        if tamano_bytes > max_size_permitido:
            limit_mb = max_size_permitido / (1024 * 1024)
            return {
                'valido': False, 
                'mensaje': f"El archivo excede el tamaño máximo permitido de {limit_mb:.1f}MB"
            }

        return {'valido': True, 'mensaje': "OK", 'posibles_tipos': tipos_compatibles}
