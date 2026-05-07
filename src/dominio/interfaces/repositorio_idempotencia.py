from abc import ABC, abstractmethod
from typing import Optional, Any, Dict


class IRepositorioIdempotencia(ABC):
    """
    Contrato para persistencia de claves idempotentes.
    Implementación principal: PostgreSQL.
    """

    @abstractmethod
    def existe(self, key: str) -> bool:
        """Verifica si la clave ya existe en el sistema."""
        pass

    @abstractmethod
    def registrar(
        self,
        key: str,
        operacion: str,
        resultado: Any,
        parametros: Dict[str, Any],
        usuario_id: int,
        ttl_hours: int = 24,
    ) -> None:
        """
        Registra una nueva clave de idempotencia con su resultado.

        Args:
            key: Hash único de la operación (SHA256).
            operacion: Nombre descriptivo de la acción.
            resultado: Datos de respuesta para ser cacheados (JSON serializable).
            parametros: Argumentos originales de la llamada.
            usuario_id: ID del usuario que realiza la acción.
            ttl_hours: Tiempo de vida de la clave en horas.
        """
        pass

    @abstractmethod
    def bloquear(
        self,
        key: str,
        operacion: str,
        parametros: Dict[str, Any],
        usuario_id: int,
        ttl_hours: int = 1,
    ) -> bool:
        """
        Intenta adquirir el lock de idempotencia atómicamente.
        INSERT ... ON CONFLICT (KEY) DO NOTHING RETURNING ID_KEY.
        Returns True si se adquirió el lock (nuevo), False si ya existía.
        """
        pass

    @abstractmethod
    def obtener_resultado(self, key: str) -> Optional[Any]:
        """
        Recupera el resultado cacheado asociado a la clave.

        Returns:
            Optional[Any]: El resultado serializado o None si no existe.
        """
        pass

    @abstractmethod
    def registrar_evento(
        self,
        entidad_tipo: str,
        entidad_id: int,
        tipo_evento: str,
        idempotency_key: str,
        payload: Dict[str, Any],
        usuario_id: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Registra un evento de auditoría inmutable vinculado a una clave de idempotencia.
        """
        pass

    @abstractmethod
    def limpiar_expirados(self) -> int:
        """
        Elimina las claves que han superado su tiempo de vida (TTL).

        Returns:
            int: Cantidad de registros eliminados.
        """
        pass
