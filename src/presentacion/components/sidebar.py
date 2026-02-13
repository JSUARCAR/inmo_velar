"""
Barra de Navegación Lateral (Sidebar) - Inmobiliaria Velar
"""

import reflex as rx

from src.presentacion.theme import colors, styles


class Sidebar(ft.Container):
    """Menu lateral de navegacion."""

    def __init__(
        self,
        usuario,
        on_navigate,
        on_logout,
        collapsed=False,
        on_toggle=None,
        responsive=False,
        page_width=None,
    ):
        super().__init__()
        self.usuario = usuario
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.collapsed = collapsed
        self.on_toggle = on_toggle
        self.responsive = responsive
        self.page_width = page_width
        # Adjust initial collapsed state based on responsiveness
        if self.responsive and self.page_width is not None:
            self.collapsed = self.page_width < 600
        self.width = 80 if self.collapsed else 250

        # Width already set above based on responsive state
        self.bgcolor = colors.BACKGROUND
        self.border_radius = 0
        self.padding = 0
        self.border = ft.border.only(right=ft.border.BorderSide(1, colors.BORDER_DEFAULT))

        # Map to store menu items controls for updating state
        self._menu_items_map = {}

        self.content = self._build_content()
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)

    def toggle(self, e):
        """Alterna el estado de expansión de la sidebar."""
        self.collapsed = not self.collapsed
        self.width = 80 if self.collapsed else 250

        # Reconstruir contenido
        self.content = self._build_content()

        # Notify parent of toggle state if applicable
        if self.on_toggle:
            self.on_toggle(self.collapsed)
        self.update()

        # Notificar cambio de estado al padre (persistencia)
        if self.on_toggle:
            self.on_toggle(self.collapsed)

    def _build_content(self):
        # Header Content
        if self.collapsed:
            header_content = ft.Column(
                [
                    ft.Icon(ft.Icons.APARTMENT, color=colors.PRIMARY, size=24),
                    ft.IconButton(
                        icon=ft.Icons.MENU_OPEN,
                        icon_color=colors.TEXT_SECONDARY,
                        on_click=self.toggle,
                        tooltip="Expandir",
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        else:
            header_content = ft.Row(
                [
                    ft.Icon(ft.Icons.APARTMENT, color=colors.PRIMARY, size=28),
                    ft.Column(
                        [
                            ft.Text(
                                "VELAR",
                                weight=ft.FontWeight.BOLD,
                                size=18,
                                color=colors.TEXT_PRIMARY,
                            ),
                            ft.Text("INMOBILIARIA", size=10, color=colors.TEXT_SECONDARY),
                        ],
                        spacing=0,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=colors.TEXT_SECONDARY,
                        on_click=self.toggle,
                        tooltip="Colapsar",
                        icon_size=20,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            )

        # Profile Content
        if self.collapsed:
            profile_content = ft.CircleAvatar(
                content=ft.Text(self.usuario.nombre_usuario[:2].upper(), size=12),
                bgcolor=colors.PRIMARY,
                radius=18,
            )
        else:
            profile_content = ft.Column(
                [
                    ft.CircleAvatar(
                        content=ft.Text(self.usuario.nombre_usuario[:2].upper()),
                        bgcolor=colors.PRIMARY,
                        radius=24,
                    ),
                    ft.Text(
                        self.usuario.nombre_usuario,
                        weight=ft.FontWeight.BOLD,
                        color=colors.TEXT_PRIMARY,
                    ),
                    (
                        styles.badge_admin()
                        if self.usuario.rol == "Administrador"
                        else styles.badge_asesor()
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        return ft.Column(
            [
                # 1. Header: Logo y Marca + Toggle
                ft.Container(
                    content=header_content,
                    padding=ft.padding.symmetric(
                        vertical=20, horizontal=10 if self.collapsed else 20
                    ),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, colors.BORDER_DEFAULT)),
                    alignment=ft.alignment.center if self.collapsed else None,
                ),
                # 2. Perfil Usuario Resumido
                ft.Container(content=profile_content, padding=20, alignment=ft.alignment.center),
                ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                # 3. Menu Items (Scrollable)
                ft.Column(
                    [
                        # Operaciones
                        ft.Container(
                            content=(
                                ft.Text(
                                    "OPS",
                                    size=10,
                                    color=colors.TEXT_SECONDARY,
                                    weight=ft.FontWeight.BOLD,
                                )
                                if self.collapsed
                                else ft.Text(
                                    "OPERACIONES",
                                    size=10,
                                    color=colors.TEXT_SECONDARY,
                                    weight=ft.FontWeight.BOLD,
                                )
                            ),
                            padding=ft.padding.only(left=5 if self.collapsed else 0),
                            alignment=(
                                ft.alignment.center if self.collapsed else ft.alignment.center_left
                            ),
                        ),
                        self._menu_item(
                            "Dashboard", ft.Icons.DASHBOARD_OUTLINED, route="dashboard"
                        ),
                        self._menu_item("Personas", ft.Icons.PEOPLE_OUTLINE, route="personas"),
                        self._menu_item(
                            "Proveedores", ft.Icons.ENGINEERING_OUTLINED, route="proveedores"
                        ),
                        self._menu_item("Seguros", ft.Icons.SHIELD_OUTLINED, route="seguros"),
                        self._menu_item(
                            "Propiedades", ft.Icons.HOME_WORK_OUTLINED, route="propiedades"
                        ),
                        self._menu_item(
                            "Desocupaciones",
                            ft.Icons.NO_MEETING_ROOM_OUTLINED,
                            route="desocupaciones",
                        ),
                        self._menu_item(
                            "Contratos", ft.Icons.DESCRIPTION_OUTLINED, route="contratos"
                        ),
                        self._menu_item("Recaudos", ft.Icons.ATTACH_MONEY, route="recaudos"),
                        self._menu_item(
                            "Liquidaciones", ft.Icons.ACCOUNT_BALANCE_WALLET, route="liquidaciones"
                        ),
                        self._menu_item(
                            "Liquidación Asesores",
                            ft.Icons.HANDSHAKE_OUTLINED,
                            route="liquidaciones_asesores",
                        ),
                        self._menu_item(
                            "Pagos Asesores", ft.Icons.PAYMENTS, route="pagos_asesores"
                        ),
                        self._menu_item(
                            "Saldos a Favor",
                            ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                            route="saldos_favor",
                        ),
                        self._menu_item(
                            "Recibos Públicos", ft.Icons.RECEIPT_LONG, route="recibos_publicos"
                        ),
                        self._menu_item(
                            "Incrementos IPC", ft.Icons.TRENDING_UP, route="incrementos"
                        ),
                        self._menu_item("Incidentes", ft.Icons.BUILD_OUTLINED, route="incidentes"),
                        # Sección de Administración (solo para Administrador)
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                                    ft.Container(
                                        content=(
                                            ft.Icon(
                                                ft.Icons.SETTINGS,
                                                size=16,
                                                color=colors.TEXT_SECONDARY,
                                            )
                                            if self.collapsed
                                            else ft.Text(
                                                "ADMINISTRACIÓN",
                                                size=10,
                                                color=colors.TEXT_SECONDARY,
                                                weight=ft.FontWeight.BOLD,
                                            )
                                        ),
                                        alignment=(
                                            ft.alignment.center
                                            if self.collapsed
                                            else ft.alignment.center_left
                                        ),
                                    ),
                                    self._menu_item(
                                        "Configuración", ft.Icons.SETTINGS, route="configuracion"
                                    ),
                                ]
                            ),
                            visible=self.usuario.rol == "Administrador",
                        ),
                    ],
                    spacing=5,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                        if self.collapsed
                        else ft.CrossAxisAlignment.START
                    ),
                ),
                # 4. Footer: Logout
                ft.Container(
                    content=(
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            icon_color=colors.ERROR,
                            tooltip="Cerrar Sesión",
                            on_click=lambda _: self.on_logout(),
                        )
                        if self.collapsed
                        else ft.TextButton(
                            "Cerrar Sesión",
                            icon=ft.Icons.LOGOUT,
                            icon_color=colors.ERROR,
                            style=ft.ButtonStyle(color=colors.ERROR),
                            on_click=lambda _: self.on_logout(),
                        )
                    ),
                    padding=20,
                    border=ft.border.only(top=ft.border.BorderSide(1, colors.BORDER_DEFAULT)),
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )

    def _menu_item(self, titulo, icono, activado=False, route=None, on_click=None):
        # Determine route key (fallback to title lower if None, though explicit route is better)
        route_key = route if route else titulo.lower()

        color = colors.PRIMARY if activado else colors.TEXT_SECONDARY
        bg = colors.SURFACE if activado else colors.BACKGROUND
        weight = ft.FontWeight.W_500 if activado else ft.FontWeight.NORMAL

        if on_click:
            handler = on_click
        else:
            def handler(_):
                return self.on_navigate(route_key)

        # Create controls with ref
        icon_control = ft.Icon(icono, size=24 if self.collapsed else 20, color=color)

        if self.collapsed:
            content = icon_control
            tooltip = titulo
            padding = ft.padding.all(10)
        else:
            text_control = ft.Text(titulo, size=14, color=color, weight=weight)
            content = ft.Row([icon_control, text_control], spacing=12)
            tooltip = None
            padding = ft.padding.symmetric(horizontal=16, vertical=12)

        container = ft.Container(
            content=content,
            padding=padding,
            bgcolor=bg,
            border_radius=8,
            on_click=handler,
            ink=True,
            tooltip=tooltip,
            data={"route": route_key},  # Store route in data for easy access
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

        # Store refs for future updates (need to be careful as text might not exist now)
        # For simplicity in this specialized update, we'll store specific references safely
        self._menu_items_map[route_key] = {
            "container": container,
            "icon": icon_control,
            # Text is optional now
            "text": (
                content.controls[1] if not self.collapsed and isinstance(content, ft.Row) else None
            ),
        }

        return container

    def set_active_route(self, route_name: str):
        """
        Actualiza el estado visual de los items del menú basado en la ruta activa.

        Args:
            route_name: Nombre de la ruta activa (ej: 'dashboard', 'personas')
        """
        route_name = route_name.lower()
        # If responsive, ensure sidebar is expanded for larger screens
        if self.responsive and self.page_width is not None:
            self.collapsed = self.page_width < 600
            self.width = 80 if self.collapsed else 250
            self.content = self._build_content()
            self.update()

        # Normalize route name if needed (e.g. handle sub-routes or strip params if format differs)
        # For now direct matching or prefix matching might be enough.

        for key, controls in self._menu_items_map.items():
            is_active = key == route_name

            # Special case for sub-views handling (e.g. 'persona_detalle' should light up 'personas')
            # Assuming simple prefix convention or explicit mapping might be needed later.
            # Simple heuristic: if route_name starts with key (and key is not too short/generic)
            # E.g. route="personas_form" -> key="personas"
            if not is_active and len(key) > 3 and key in route_name:
                is_active = True

            # Update styles
            color = colors.PRIMARY if is_active else colors.TEXT_SECONDARY
            bg = colors.SURFACE if is_active else colors.BACKGROUND
            weight = ft.FontWeight.W_500 if is_active else ft.FontWeight.NORMAL

            controls["container"].bgcolor = bg
            controls["icon"].color = color

            if controls.get("text"):
                controls["text"].color = color
                controls["text"].weight = weight

            controls["container"].update()

    def update_responsive(self, page_width: int):
        """Update sidebar layout based on given page width.
        Args:
            page_width: Current width of the application window.
        """
        self.page_width = page_width
        if self.responsive:
            new_collapsed = page_width < 600
            if new_collapsed != self.collapsed:
                self.collapsed = new_collapsed
                self.width = 80 if self.collapsed else 250
                self.content = self._build_content()
                self.update()
