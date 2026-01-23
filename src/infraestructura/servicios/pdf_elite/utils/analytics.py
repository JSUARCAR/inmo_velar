"""
Sistema de Analytics para PDFs
===============================
Tracking y métricas de generación de documentos PDF.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import defaultdict


class PDFAnalytics:
    """
    Sistema de analytics para generación de PDFs
    
    Registra y analiza:
    - Documentos generados
    - Tiempos de generación
    - Errores y fallos
    - Documentos más generados
    - Performance por tipo
    
    Example:
        >>> analytics = PDFAnalytics()
        >>> analytics.track_generation('contrato', 1.5, success=True)
        >>> stats = analytics.get_statistics()
    """
    
    def __init__(self, storage_path: Path = None):
        """
        Inicializa el sistema de analytics
        
        Args:
            storage_path: Path para almacenar datos de analytics
        """
        self.storage_path = storage_path or Path("analytics/pdf_analytics.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar datos existentes
        self._load_data()
    
    def _load_data(self) -> None:
        """Carga datos de analytics desde disco"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'generations': [],
                'errors': [],
                'total_count': 0,
                'success_count': 0,
                'error_count': 0
            }
    
    def _save_data(self) -> None:
        """Guarda datos a disco"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def track_generation(
        self,
        doc_type: str,
        duration_seconds: float,
        success: bool = True,
        doc_id: int = None,
        user_id: int = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Registra una generación de PDF
        
        Args:
            doc_type: Tipo de documento
            duration_seconds: Tiempo que tomó generar
            success: Si fue exitosa
            doc_id: ID del documento generado
            user_id: ID del usuario que generó
            metadata: Metadata adicional
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'doc_type': doc_type,
            'duration': duration_seconds,
            'success': success,
            'doc_id': doc_id,
            'user_id': user_id,
            'metadata': metadata or {}
        }
        
        self.data['generations'].append(event)
        self.data['total_count'] += 1
        
        if success:
            self.data['success_count'] += 1
        else:
            self.data['error_count'] += 1
        
        # Guardar cada 10 eventos para no sobrecargar I/O
        if self.data['total_count'] % 10 == 0:
            self._save_data()
    
    def track_error(
        self,
        doc_type: str,
        error_message: str,
        doc_id: int = None,
        user_id: int = None
    ) -> None:
        """
        Registra un error en la generación
        
        Args:
            doc_type: Tipo de documento
            error_message: Mensaje de error
            doc_id: ID del documento
            user_id: ID del usuario
        """
        error_event = {
            'timestamp': datetime.now().isoformat(),
            'doc_type': doc_type,
            'error_message': error_message,
            'doc_id': doc_id,
            'user_id': user_id
        }
        
        self.data['errors'].append(error_event)
        self._save_data()
    
    def get_statistics(
        self,
        days: int = 30,
        doc_type: str = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de generación
        
        Args:
            days: Últimos N días a analizar
            doc_type: Filtrar por tipo de documento
            
        Returns:
            Diccionario con estadísticas
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filtrar eventos
        recent_gens = [
            g for g in self.data['generations']
            if datetime.fromisoformat(g['timestamp']) > cutoff_date
            and (doc_type is None or g['doc_type'] == doc_type)
        ]
        
        if not recent_gens:
            return {
                'period_days': days,
                'total_generations': 0,
                'success_rate': 0,
                'avg_duration': 0
            }
        
        # Calcular métricas
       successful = [g for g in recent_gens if g['success']]
        durations = [g['duration'] for g in successful]
        
        # Por tipo de documento
        by_type = defaultdict(lambda: {'count': 0, 'avg_duration': 0, 'durations': []})
        for gen in successful:
            dtype = gen['doc_type']
            by_type[dtype]['count'] += 1
            by_type[dtype]['durations'].append(gen['duration'])
        
        # Calcular promedios
        for dtype in by_type:
            durations_list = by_type[dtype]['durations']
            by_type[dtype]['avg_duration'] = sum(durations_list) / len(durations_list)
            del by_type[dtype]['durations']  # No necesitamos la lista completa
        
        # Documentos más generados
        type_counts = defaultdict(int)
        for gen in recent_gens:
            type_counts[gen['doc_type']] += 1
        
        top_documents = sorted(
            type_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'period_days': days,
            'total_generations': len(recent_gens),
            'successful_generations': len(successful),
            'failed_generations': len(recent_gens) - len(successful),
            'success_rate': (len(successful) / len(recent_gens)) * 100,
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'by_type': dict(by_type),
            'top_documents': top_documents,
            'total_errors': len([e for e in self.data['errors'] 
                               if datetime.fromisoformat(e['timestamp']) > cutoff_date])
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene errores recientes
        
        Args:
            limit: Número de errores a retornar
            
        Returns:
            Lista de errores recientes
        """
        return sorted(
            self.data['errors'],
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
    
    def export_report(self, days: int = 30) -> str:
        """
        Exporta reporte de analytics en formato texto
        
        Args:
            days: Período a reportar
            
        Returns:
            String con el reporte
        """
        stats = self.get_statistics(days)
        
        report = f"""
=== REPORTE DE ANALYTICS PDF ({days} días) ===

📊 Resumen General:
- Total generaciones: {stats['total_generations']}
- Exitosas: {stats['successful_generations']}
- Fallidas: {stats['failed_generations']}
- Tasa de éxito: {stats['success_rate']:.1f}%

⏱️ Performance:
- Tiempo promedio: {stats['avg_duration']:.2f}s
- Tiempo mínimo: {stats['min_duration']:.2f}s
- Tiempo máximo: {stats['max_duration']:.2f}s

📄 Documentos Más Generados:
"""
        for doc_type, count in stats['top_documents']:
            report += f"  - {doc_type}: {count} documentos\n"
        
        report += f"\n💥 Total errores: {stats['total_errors']}\n"
        
        return report


# Instancia global singleton
_analytics_instance: Optional[PDFAnalytics] = None


def get_pdf_analytics() -> PDFAnalytics:
    """Obtiene instancia singleton de analytics"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = PDFAnalytics()
    return _analytics_instance


__all__ = ['PDFAnalytics', 'get_pdf_analytics']
