"""
Ejemplo de integración de paginación en ServicioPersonas.

Este archivo demuestra cómo integrar el sistema de paginación
en servicios existentes.

Autor: InmoVelar Dev Team
Fecha: 2025-12-29
"""

from typing import Optional
from src.dominio.modelos.pagination import PaginatedResult, PaginationParams, create_empty_result
from src.infraestructura.cache.cache_manager import cache_manager


# ====================================================================
# EJEMPLO: Método paginado en ServicioPersonas
# ====================================================================

class ServicioPersonasConPaginacion:
    """
    Ejemplo de ServicioPersonas con soporte para paginación.
    
    NOTA: Este es un ejemplo de referencia. La integración real debe
    hacerse en src/aplicacion/servicios/servicio_personas.py
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
        self.repo = RepositorioPersonaSQLite(db_manager)
    
    # Método existente (mantener por compatibilidad)
    def listar_personas(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None
    ):
        """
        Método original sin paginación.
        Se mantiene por compatibilidad hacia atrás.
        """
        # Implementación existente...
        pass
    
    # Nuevo método con paginación
    @cache_manager.cached('personas:paginated', level=1)
    def listar_personas_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = False
    ) -> PaginatedResult:
        """
        Lista personas con paginación.
        
        Args:
            page: Número de página (1-indexed)
            page_size: Items por página
            filtro_rol: Filtrar por rol específico
            solo_activos: Solo personas activas
            busqueda: Búsqueda por nombre/documento
            sort_by: Campo para ordenar
            sort_desc: Ordenar descendente
            
        Returns:
            PaginatedResult con personas y metadata
        """
        try:
            # Crear parámetros de paginación
            params = PaginationParams(
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_desc=sort_desc
            )
            
            # Preparar filtros
            filtros = {
                'solo_activos': solo_activos
            }
            
            if filtro_rol:
                filtros['rol'] = filtro_rol
            
            if busqueda:
                filtros['busqueda'] = busqueda
            
            # OPCIÓN 1: Si el repositorio NO tiene método paginado
            # (implementación manual)
            """
            # Contar total
            total = self.repo.contar_con_filtros(filtros)
            
            if total == 0:
                return create_empty_result(page, page_size)
            
            # Obtener items de la página
            items = self.repo.obtener_todos(
                solo_activos=solo_activos,
                limite=params.limit,
                offset=params.offset
            )
            
            return PaginatedResult(
                items=items,
                total=total,
                page=page,
                page_size=page_size
            )
            """
            
            # OPCIÓN 2: Si el repositorio tiene método paginado
            # (recomendado - más eficiente)
            result = self.repo.obtener_paginado(params, filtros)
            return result
            
        except Exception as e:
            print(f"Error en listar_personas_paginado: {e}")
            return create_empty_result(page, page_size)
    
    # Métodos de escritura invalidan cache
    def crear_persona(self, ...):
        """Crea persona e invalida cache."""
        result = self.repo.crear(...)
        cache_manager.invalidate('personas')
        return result
    
    def actualizar_persona(self, ...):
        """Actualiza persona e invalida cache."""
        result = self.repo.actualizar(...)
        cache_manager.invalidate('personas')
        return result


# ====================================================================
# EJEMPLO: Vista PersonasListView con paginación
# ====================================================================

"""
Ejemplo de cómo integrar PaginationManager en PersonasListView.

Cambios principales en la vista:

1. Agregar componente de paginación
2. Mantener estado de página actual
3. Usar método paginado del servicio
4. Resetear a página 1 cuando cambian filtros

class PersonasListView(ft.Container):
    def __init__(self, ...):
        super().__init__(...)
        
        # Estado de paginación
        self.current_page = 1
        self.page_size = 25
        self.total_items = 0
        
        # Componente de paginación
        self.pagination = PaginationManager(
            total_items=0,
            items_per_page=25,
            current_page=1,
            on_page_change=self._on_page_change,
            on_page_size_change=self._on_page_size_change
        )
        
        # Layout incluye paginación
        self.content = ft.Column([
            # ... breadcrumb, filtros, etc
            self.tabla_container,
            self.pagination,  # Agregar aquí
        ])
    
    def _on_page_change(self, new_page: int):
        '''Callback cuando cambia la página.'''
        self.current_page = new_page
        self.cargar_datos()
    
    def _on_page_size_change(self, new_size: int):
        '''Callback cuando cambia el tamaño.'''
        self.page_size = new_size
        self.current_page = 1  # Reset a página 1
        self.cargar_datos()
    
    def _on_filtro_change(self, e):
        '''Cuando cambia filtro, resetear a página 1.'''
        self.filtro_rol = e.control.value
        self.current_page = 1
        self.cargar_datos()
    
    def _fetch_data_thread(self):
        '''Obtener datos con paginación.'''
        try:
            # Usar método paginado
            result = self.servicio.listar_personas_paginado(
                page=self.current_page,
                page_size=self.page_size,
                filtro_rol=self.filtro_rol,
                solo_activos=self.solo_activos,
                busqueda=self.busqueda
            )
            
            # Actualizar estado
            self.personas = result.items
            self.total_items = result.total
            
            # Actualizar componente de paginación
            self.pagination.set_total_items(result.total)
            self.pagination.set_current_page(result.page)
            
            # Renderizar
            self._schedule_ui_update(0, None)
            
        except Exception as e:
            print(f"Error: {e}")
            self._schedule_ui_update(0, str(e))
"""


# ====================================================================
# EJEMPLO: Query SQL con paginación eficiente
# ====================================================================

EJEMPLO_QUERY_PAGINACION = """
-- Query ejemplo usando window functions para total en una sola consulta

SELECT 
    p.ID_PERSONA,
    p.NOMBRE,
    p.APELLIDO,
    p.TIPO_DOCUMENTO,
    p.NUMERO_DOCUMENTO,
    p.ACTIVO,
    COUNT(*) OVER() as total_count  -- Window function para total
FROM PERSONA p
WHERE 
    p.ACTIVO = :solo_activos
    AND (:busqueda IS NULL OR 
         p.NOMBRE LIKE :busqueda_pattern OR 
         p.APELLIDO LIKE :busqueda_pattern OR
         p.NUMERO_DOCUMENTO LIKE :busqueda_pattern)
ORDER BY 
    CASE WHEN :sort_by = 'nombre' AND :sort_desc = 0 THEN p.NOMBRE END ASC,
    CASE WHEN :sort_by = 'nombre' AND :sort_desc = 1 THEN p.NOMBRE END DESC,
    p.ID_PERSONA DESC  -- Default order
LIMIT :limit OFFSET :offset
"""

# Ejemplo de uso en repositorio:
"""
def obtener_paginado(self, params: PaginationParams, filtros: Dict) -> PaginatedResult:
    query = EJEMPLO_QUERY_PAGINACION
    
    # Preparar parámetros
    query_params = {
        'solo_activos': 1 if filtros.get('solo_activos', True) else 0,
        'busqueda': filtros.get('busqueda'),
        'busqueda_pattern': f"%{filtros.get('busqueda', '')}%",
        'sort_by': params.sort_by or 'nombre',
        'sort_desc': 1 if params.sort_desc else 0,
        'limit': params.limit,
        'offset': params.offset
    }
    
    # Ejecutar
    cursor = self.db.execute(query, query_params)
    rows = cursor.fetchall()
    
    # Extraer total (disponible en primera fila)
    total = rows[0]['total_count'] if rows else 0
    
    # Mapear a entidades
    items = [self._map_row_to_entity(row) for row in rows]
    
    return PaginatedResult(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size
    )
"""


# ====================================================================
# NOTAS DE MIGRACIÓN
# ====================================================================

NOTAS_MIGRACION = """
PASOS PARA INTEGRAR PAGINACIÓN EN VISTAS EXISTENTES:

1. Importar componentes:
   from src.presentacion.components.pagination_manager import PaginationManager
   from src.dominio.modelos.pagination import PaginatedResult

2. Agregar estado de paginación a la vista:
   self.current_page = 1
   self.page_size = 25
   self.total_items = 0

3. Crear componente de paginación:
   self.pagination = PaginationManager(
       total_items=0,
       items_per_page=25,
       on_page_change=self._on_page_change,
       on_page_size_change=self._on_page_size_change
   )

4. Actualizar método de carga de datos:
   - Usar método *_paginado del servicio
   - Actualizar self.total_items con result.total
   - Actualizar componente: self.pagination.set_total_items(total)

5. Resetear a página 1 cuando cambien filtros:
   def _on_filtro_change(self, e):
       self.current_page = 1
       self.cargar_datos()

6. Agregar componente al layout:
   ft.Column([
       # ... contenido existente
       self.pagination  # Al final
   ])

VISTAS A MIGRAR (prioridad):
- [x] Ejemplo de referencia creado
- [ ] PersonasListView
- [ ] PropiedadesListView  
- [ ] ContratosListView
- [ ] RecaudosListView
- [ ] LiquidacionesListView
- [ ] RecibosPublicosListView
- [ ] SaldosFavorListView
""".strip()
