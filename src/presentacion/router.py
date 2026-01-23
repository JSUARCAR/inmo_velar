"""
Router: Sistema de Navegación
Gestiona el cambio de vistas en la aplicación.
"""

import flet as ft
from typing import Callable, Dict, Optional, Any
from src.dominio.entidades.usuario import Usuario


class Router:
    """
    Router simple para navegación entre vistas.
    Gestiona el estado de la aplicación y el cambio de vistas.
    """
    
    def __init__(self, page: ft.Page, usuario_actual: Usuario, shell=None):
        self.page = page
        self.usuario_actual = usuario_actual
        self.vista_actual = "dashboard"
        self.historial = ["dashboard"]
        self.shell = shell  # Referencia al Shell para navegación optimizada
        
        # Registro de callbacks de vistas
        self._view_builders: Dict[str, Callable] = {}
        
        # Caché de vistas pre-construidas
        self._view_cache: Dict[str, Any] = {}
    
    def registrar_vista(self, nombre: str, builder: Callable):
        """
        Registra un constructor de vista.
        
        Args:
            nombre: Nombre único de la vista
            builder: Función que retorna el contenido de la vista
        """
        # Normalizar a minúsculas para evitar problemas de case sensitivity
        self._view_builders[nombre.lower()] = builder
    
    def pre_construir_vista(self, nombre_vista: str, **kwargs):
        """
        Pre-construye una vista y la guarda en caché sin mostrarla.
        
        Args:
            nombre_vista: Nombre de la vista registrada
            **kwargs: Argumentos adicionales para pasar al constructor de vista
        """
        nombre_vista = nombre_vista.lower()
        
        if nombre_vista not in self._view_builders:
            print(f"⚠️ No se puede pre-construir '{nombre_vista}': vista no registrada")
            return
        
        try:
            # Solo pre-construir si no tiene kwargs (vistas sin parámetros)
            if not kwargs:
                print(f"🔨 Pre-construyendo vista: {nombre_vista}")
                vista = self._view_builders[nombre_vista](**kwargs)
                self._view_cache[nombre_vista] = vista
                print(f"✅ Vista '{nombre_vista}' pre-construida y cacheada")
            else:
                print(f"⏭️ Saltando '{nombre_vista}': requiere parámetros")
        except Exception as e:
            print(f"❌ Error pre-construyendo '{nombre_vista}': {e}")
    
    def refrescar_vista(self, nombre_vista: str):
        """
        Invalida el caché de una vista específica.
        La próxima vez que se navegue a ella, se reconstruirá.
        
        Args:
            nombre_vista: Nombre de la vista a refrescar
        """
        nombre_vista = nombre_vista.lower()
        
        if nombre_vista in self._view_cache:
            del self._view_cache[nombre_vista]
            print(f"🔄 Caché invalidado para: {nombre_vista}")
    
    def navegar_a(self, nombre_vista: str, **kwargs):
        """
        Navega a una vista específica.
        Usa caché si está disponible, sino construye la vista.
        
        Args:
            nombre_vista: Nombre de la vista registrada
            **kwargs: Argumentos adicionales para pasar al constructor de vista
        """
        print(f"\n=== ROUTER DEBUG: Navegando a '{nombre_vista}' ===")
        
        # Normalizar a minúsculas
        nombre_vista = nombre_vista.lower()
        print(f"ROUTER DEBUG: Nombre normalizado: '{nombre_vista}'")
        print(f"ROUTER DEBUG: Vistas registradas: {list(self._view_builders.keys())}")
        
        if nombre_vista not in self._view_builders:
            print(f"❌ ROUTER ERROR: Vista '{nombre_vista}' no registrada")
            print(f"Vistas disponibles: {list(self._view_builders.keys())}")
            return
        
        print(f"✅ ROUTER DEBUG: Vista encontrada, construyendo...")
        
        # Guardar en historial
        if self.vista_actual != nombre_vista:
            self.historial.append(nombre_vista)
            self.vista_actual = nombre_vista
        
        # Mostrar ProgressBar durante la navegación
        self.page.splash = ft.ProgressBar()
        self.page.update()

        # Construir nueva vista
        try:
            # Intentar usar caché si no hay kwargs
            # NOTA: Dashboard nunca debe ser cacheado para mostrar datos frescos
            use_cache = (
                nombre_vista in self._view_cache 
                and not kwargs 
                and nombre_vista != "dashboard"
            )
            
            if use_cache:
                print(f"⚡ ROUTER DEBUG: Usando vista cacheada para '{nombre_vista}'")
                nueva_vista = self._view_cache[nombre_vista]
            else:
                print(f"ROUTER DEBUG: Llamando view builder para '{nombre_vista}'...")
                nueva_vista = self._view_builders[nombre_vista](**kwargs)
            
            print(f"ROUTER DEBUG: Vista construida: {type(nueva_vista).__name__}")
            
            # Actualizar vista usando Shell (preserva Sidebar/Navbar) o método legacy
            if self.shell:
                print(f"ROUTER DEBUG: Actualizando solo content_area del Shell...")
                self.shell.update_content(nueva_vista)
                # Actualizar estado activo del Sidebar
                if hasattr(self.shell, 'sidebar') and hasattr(self.shell.sidebar, 'set_active_route'):
                    try:
                        self.shell.sidebar.set_active_route(nombre_vista)
                    except Exception as e:
                        print(f"Advertencia: No se pudo actualizar Sidebar active route: {e}")
            else:
                # Método legacy (destruye todo)
                print(f"ROUTER DEBUG: Limpiando página (método legacy)...")
                self.page.clean()
                print(f"ROUTER DEBUG: Agregando vista a página...")
                self.page.add(nueva_vista)
                print(f"ROUTER DEBUG: Actualizando página...")
                self.page.update()
            
            # Quitar ProgressBar
            self.page.splash = None
            print(f"✅ ROUTER DEBUG: Navegación completada exitosamente")
            print(f"=== FIN ROUTER DEBUG ===\n")
            
        except Exception as e:
            print(f"Error cargando vista '{nombre_vista}': {e}")
            import traceback
            traceback.print_exc()
            
            # Mostrar error en pantalla
            self.page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.ERROR, size=60, color=ft.Colors.RED),
                            ft.Text(
                                f"Error cargando vista: {nombre_vista}",
                                size=20,
                                color=ft.Colors.RED
                            ),
                            ft.Text(str(e), color=ft.Colors.RED),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
            self.page.update()
    
    def volver(self):
        """Navega a la vista anterior en el historial."""
        if len(self.historial) > 1:
            self.historial.pop()  # Remover vista actual
            vista_anterior = self.historial[-1]
            self.vista_actual = vista_anterior
            self.navegar_a(vista_anterior)
    
    def obtener_vista_actual(self) -> str:
        """Retorna el nombre de la vista actual."""
        return self.vista_actual
