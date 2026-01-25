"""
Sistema de Cache Avanzado para PDFs
====================================
Cachea templates y PDFs generados para mejorar performance.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class PDFCacheManager:
    """
    Gestor de cache para sistema PDF

    Características:
    - Cache de templates compilados (en memoria)
    - Cache de PDFs generados (en disco)
    - TTL configurable
    - Invalidación automática
    - LRU eviction

    Example:
        >>> cache = PDFCacheManager()
        >>> pdf_path = cache.get_cached_pdf('contrato', data_hash)
        >>> if not pdf_path:
        ...     pdf_path = generate_pdf()
        ...     cache.store_pdf('contrato', data_hash, pdf_path)
    """

    def __init__(
        self, cache_dir: Path = None, ttl_seconds: int = 3600, max_cache_size_mb: int = 100
    ):
        """
        Inicializa el cache manager

        Args:
            cache_dir: Directorio para cache en disco
            ttl_seconds: Tiempo de vida del cache (default: 1 hora)
            max_cache_size_mb: Tamaño máximo del cache en MB
        """
        self.cache_dir = cache_dir or Path("cache/pdfs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.ttl_seconds = ttl_seconds
        self.max_size_bytes = max_cache_size_mb * 1024 * 1024

        # Cache en memoria de metadata
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}

        # Limpiar cache expirado al inicializar
        self._cleanup_expired()

    def _generate_cache_key(self, doc_type: str, data: Dict[str, Any]) -> str:
        """
        Genera clave única para el cache basada en los datos

        Args:
            doc_type: Tipo de documento
            data: Datos del documento

        Returns:
            Hash MD5 como clave
        """
        # Serializar datos de forma determinística
        data_str = json.dumps(data, sort_keys=True, default=str)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()

        return f"{doc_type}_{data_hash}"

    def get_cached_pdf(self, doc_type: str, data: Dict[str, Any]) -> Optional[Path]:
        """
        Obtiene PDF desde cache si existe y no ha expirado

        Args:
            doc_type: Tipo de documento
            data: Datos del documento

        Returns:
            Path del PDF cacheado o None si no existe/expiró
        """
        cache_key = self._generate_cache_key(doc_type, data)
        cached_path = self.cache_dir / f"{cache_key}.pdf"

        # Verificar si existe
        if not cached_path.exists():
            return None

        # Verificar TTL
        metadata = self._metadata_cache.get(cache_key)
        if metadata:
            age = time.time() - metadata["timestamp"]
            if age > self.ttl_seconds:
                # Expirado - eliminar
                cached_path.unlink(missing_ok=True)
                del self._metadata_cache[cache_key]
                return None

        return cached_path

    def store_pdf(self, doc_type: str, data: Dict[str, Any], pdf_path: Path) -> None:
        """
        Almacena PDF en cache

        Args:
            doc_type: Tipo de documento
            data: Datos del documento
            pdf_path: Path del PDF a cachear
        """
        cache_key = self._generate_cache_key(doc_type, data)
        cached_path = self.cache_dir / f"{cache_key}.pdf"

        # Verificar tamaño del cache antes de agregar
        self._ensure_cache_size()

        # Copiar PDF al cache
        import shutil

        shutil.copy2(pdf_path, cached_path)

        # Guardar metadata
        self._metadata_cache[cache_key] = {
            "timestamp": time.time(),
            "doc_type": doc_type,
            "size": cached_path.stat().st_size,
        }

    def _ensure_cache_size(self) -> None:
        """Asegura que el cache no exceda el tamaño máximo"""
        total_size = sum(
            (self.cache_dir / f).stat().st_size for f in self.cache_dir.glob("*.pdf") if f.is_file()
        )

        if total_size > self.max_size_bytes:
            # Eliminar archivos más antiguos hasta estar bajo el límite
            files_with_time = [(f, f.stat().st_mtime) for f in self.cache_dir.glob("*.pdf")]
            files_with_time.sort(key=lambda x: x[1])  # Más antiguos primero

            for file_path, _ in files_with_time:
                if total_size <= self.max_size_bytes * 0.8:  # 80% del máximo
                    break

                size = file_path.stat().st_size
                file_path.unlink()
                total_size -= size

                # Remover metadata
                cache_key = file_path.stem
                self._metadata_cache.pop(cache_key, None)

    def _cleanup_expired(self) -> None:
        """Limpia archivos expirados del cache"""
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.pdf"):
            age = current_time - cache_file.stat().st_mtime
            if age > self.ttl_seconds:
                cache_file.unlink(missing_ok=True)

    def invalidate_cache(self, doc_type: Optional[str] = None) -> None:
        """
        Invalida cache completo o de un tipo específico

        Args:
            doc_type: Tipo de documento a invalidar (None = todos)
        """
        if doc_type is None:
            # Invalidar todo
            for cache_file in self.cache_dir.glob("*.pdf"):
                cache_file.unlink()
            self._metadata_cache.clear()
        else:
            # Invalidar solo un tipo
            pattern = f"{doc_type}_*.pdf"
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
                cache_key = cache_file.stem
                self._metadata_cache.pop(cache_key, None)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache

        Returns:
            Diccionario con estadísticas
        """
        pdf_files = list(self.cache_dir.glob("*.pdf"))
        total_size = sum(f.stat().st_size for f in pdf_files)

        by_type = {}
        for key, meta in self._metadata_cache.items():
            doc_type = meta["doc_type"]
            by_type[doc_type] = by_type.get(doc_type, 0) + 1

        return {
            "total_files": len(pdf_files),
            "total_size_mb": total_size / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "usage_percent": (total_size / self.max_size_bytes) * 100,
            "by_type": by_type,
            "ttl_seconds": self.ttl_seconds,
        }


# Instancia global singleton
_cache_instance: Optional[PDFCacheManager] = None


def get_pdf_cache() -> PDFCacheManager:
    """Obtiene instancia singleton del cache manager"""
    global _cache_instance
    if _cache_instance is None:
        from src.infraestructura.servicios.pdf_elite.core.config import config

        _cache_instance = PDFCacheManager(
            ttl_seconds=3600, max_cache_size_mb=config.max_cache_size_mb  # 1 hora
        )
    return _cache_instance


__all__ = ["PDFCacheManager", "get_pdf_cache"]
