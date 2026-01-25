import reflex as rx

from src.presentacion_reflex.components.layout.bell_icon import bell_icon
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.configuracion_state import ConfiguracionState


def sidebar_item(
    text: str,
    icon: str,
    url: str,
    description: str = "",
    module_name: str = "",
    icon_color: str = "#3b82f6",
) -> rx.Component:
    """Item individual del sidebar con HoverCard experto y protección por permisos."""
    is_active = rx.State.router.page.path == url

    # Base item content (Trigger)
    item_content = rx.hstack(
        rx.icon(
            icon,
            size=20,
            color=icon_color,  # Use category color
        ),
        rx.text(
            text,
            size="3",
            weight=rx.cond(is_active, "bold", "medium"),
            color=rx.cond(is_active, "#0f172a", "#334155"),  # Dark colors for light bg
        ),
        spacing="3",
        padding_x="4",
        padding_y="3",
        margin_left="2",
        border_radius="10px",
        border_left=rx.cond(is_active, "3px solid #3b82f6", "3px solid transparent"),
        background=rx.cond(is_active, "rgba(59, 130, 246, 0.1)", "transparent"),
        _hover={
            "background": rx.cond(
                is_active,
                "rgba(59, 130, 246, 0.15)",
                "rgba(59, 130, 246, 0.05)",  # Light blue hover
            ),
            "transform": "translateX(4px)",
        },
        width="100%",
        align="center",
        transition="all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
        cursor="pointer",
    )

    # HoverCard Content (Elite Design - Informational Only)
    card_content = rx.hover_card.content(
        rx.vstack(
            rx.hstack(
                rx.icon_button(
                    rx.icon(icon, size=24),
                    size="3",
                    variant="surface",
                    color_scheme="blue",
                    radius="full",
                ),
                rx.vstack(
                    rx.text(text, size="3", weight="bold", color="#111827"),
                    rx.text("Módulo", size="1", color="#6b7280", weight="medium"),
                    spacing="0",
                ),
                align="center",
                spacing="3",
                width="100%",
                margin_bottom="2",
            ),
            rx.text(
                description if description else f"Acceder al módulo de {text}",
                size="2",
                color="#4b5563",
                line_height="1.5",
            ),
            # Removed "Click para navegar" footer specific request
            spacing="2",
            align="start",
        ),
        side="right",
        side_offset=15,
        align="center",
        avoid_collisions=True,
        background_color="white",
        padding="16px",
        border_radius="16px",
        border="1px solid #e5e7eb",
        box_shadow="0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        width="260px",
        data_state="open",
    )

    item_component = rx.hover_card.root(
        rx.hover_card.trigger(
            rx.link(
                item_content,
                href=url,
                width="100%",
                underline="none",
            ),
        ),
        card_content,
        open_delay=100,
        close_delay=200,
    )

    # Si se especifica un módulo, aplicar renderizado condicional según permisos
    if module_name:
        return rx.cond(
            AuthState.is_authenticated & AuthState.check_module_access(module_name),
            item_component,
            rx.fragment(),  # No renderizar nada si no tiene permiso
        )

    # Si no tiene módulo asignado (ej. Dashboard público), mostrar siempre
    # (Aunque Dashboard también debería ser un módulo, lo manejamos en la llamada)
    return item_component


def sidebar_section(title: str, *items) -> rx.Component:
    """Sección del sidebar con título y items."""
    return rx.vstack(
        rx.text(
            title,
            size="1",
            color="#64748b",  # Slate 500 - Darker than before
            weight="bold",
            letter_spacing="0.5px",
            padding_x="4",
            padding_left="6",
            margin_top="2",
        ),
        *items,
        spacing="1",
        width="100%",
        margin_bottom="4",
    )


def sidebar_items() -> rx.Component:
    """Items de navegación reutilizables."""
    return rx.vstack(
        # Sección Principal
        sidebar_section(
            "PRINCIPAL",
            sidebar_item(
                "Dashboard",
                "layout_dashboard",
                "/dashboard",
                "Panel de control general con métricas estratégicas y KPIs operativos.",
                module_name="Dashboard",
                icon_color="#3b82f6",  # Blue
            ),
        ),
        # Sección Gestión
        sidebar_section(
            "GESTIÓN",
            sidebar_item(
                "Personas",
                "users",
                "/personas",
                "Gestión integral de propietarios, arrendatarios, codeudores y asesores.",
                module_name="Personas",
                icon_color="#10b981",  # Green
            ),
            sidebar_item(
                "Propiedades",
                "home",
                "/propiedades",
                "Administración del inventario de inmuebles, características y estados.",
                module_name="Propiedades",
                icon_color="#10b981",  # Green
            ),
            sidebar_item(
                "Contratos",
                "file_text",
                "/contratos",
                "Control de contratos de mandato y arrendamiento vigentes e históricos.",
                module_name="Contratos",
                icon_color="#10b981",  # Green
            ),
            sidebar_item(
                "Proveedores",
                "wrench",
                "/proveedores",
                "Directorio y gestión de proveedores de servicios y mantenimiento.",
                module_name="Proveedores",
                icon_color="#10b981",  # Green
            ),
        ),
        # Sección Operaciones
        sidebar_section(
            "OPERACIONES",
            sidebar_item(
                "Liquidaciones",
                "dollar_sign",
                "/liquidaciones",
                "Procesamiento de liquidaciones a propietarios y gestión financiera.",
                module_name="Liquidaciones",
                icon_color="#f59e0b",  # Amber
            ),
            sidebar_item(
                "Liquidación Asesores",
                "user_check",
                "/liquidacion-asesores",
                "Cálculo y pago de comisiones, bonificaciones y estructura comercial.",
                module_name="Liquidación Asesores",
                icon_color="#f59e0b",  # Amber
            ),
            sidebar_item(
                "Recaudos",
                "coins",
                "/recaudos",
                "Registro y seguimiento de pagos recibidos de arrendatarios.",
                module_name="Recaudos",
                icon_color="#f59e0b",  # Amber
            ),
            sidebar_item(
                "Desocupaciones",
                "log_out",
                "/desocupaciones",
                "Gestión de procesos de desocupación, inspecciones y restitución.",
                module_name="Desocupaciones",
                icon_color="#f59e0b",  # Amber
            ),
            sidebar_item(
                "Incidentes",
                "triangle_alert",
                "/incidentes",
                "Seguimiento y resolución de incidencias, reparaciones y mantenimiento.",
                module_name="Incidentes",
                icon_color="#f59e0b",  # Amber
            ),
            sidebar_item(
                "Seguros",
                "shield",
                "/seguros",
                "Control de pólizas de seguro de arrendamiento y hogar.",
                module_name="Seguros",
                icon_color="#f59e0b",  # Amber
            ),
            sidebar_item(
                "Recibos Públicos",
                "zap",
                "/recibos-publicos",
                "Gestión de pagos y control de servicios públicos de los inmuebles.",
                module_name="Recibos Públicos",
                icon_color="#f59e0b",  # Amber
            ),
            sidebar_item(
                "Saldos a Favor",
                "piggy-bank",
                "/saldos-favor",
                "Administración de saldos a favor de terceros y devoluciones.",
                module_name="Saldos a Favor",
                icon_color="#f59e0b",  # Amber
            ),
        ),
        # Sección Administración
        sidebar_section(
            "ADMINISTRACIÓN",
            sidebar_item(
                "Usuarios",
                "users_round",
                "/usuarios",
                "Gestión de usuarios del sistema, roles y permisos de acceso.",
                module_name="Usuarios",
                icon_color="#8b5cf6",  # Purple
            ),
            sidebar_item(
                "Configuración",
                "settings",
                "/configuracion",
                "Ajustes generales del sistema y parámetros globales.",
                module_name="Configuración",
                icon_color="#8b5cf6",  # Purple
            ),
            sidebar_item(
                "IPC / Incrementos",
                "trending_up",
                "/incrementos",
                "Aplicación de incrementos anuales e indexación masiva por IPC.",
                module_name="IPC / Incrementos",
                icon_color="#8b5cf6",  # Purple
            ),
            sidebar_item(
                "Auditoría",
                "clipboard_list",
                "/auditoria",
                "Registro detallado (logs) de cambios y actividades en el sistema.",
                module_name="Auditoría",
                icon_color="#8b5cf6",  # Purple
            ),
            sidebar_item(
                "Reportes",
                "file-bar-chart",
                "/reportes",
                "Generación y exportación de reportes detallados en CSV.",
                module_name="Reportes",
                icon_color="#8b5cf6",  # Purple
            ),
        ),
        spacing="0",
        width="100%",
    )


def sidebar_footer() -> rx.Component:
    """Pie del sidebar con perfil de usuario."""
    return rx.hstack(
        rx.avatar(fallback="IV", size="3", radius="full", color_scheme="blue", variant="solid"),
        rx.vstack(
            rx.text(
                AuthState.user_info["nombre_usuario"],
                size="2",
                weight="bold",
                color="#1e293b",
                max_width="120px",
                overflow="hidden",
                text_overflow="ellipsis",
            ),
            rx.text(
                AuthState.user_info["rol"],
                size="1",
                color="#64748b",
                max_width="120px",
                overflow="hidden",
                text_overflow="ellipsis",
            ),
            spacing="0",
            align_items="start",
        ),
        rx.spacer(),
        bell_icon(),  # Restored bell icon
        rx.icon_button(
            "log-out",
            size="2",
            variant="ghost",
            color_scheme="red",
            on_click=AuthState.logout,
            tooltip="Cerrar Sesión",
        ),
        spacing="3",
        width="100%",
        align_items="center",
        padding_top="2",
    )


def sidebar() -> rx.Component:
    """Componente de navegación lateral mejorado."""
    return rx.vstack(
        # Header
        rx.vstack(
            rx.hover_card.root(
                rx.hover_card.trigger(
                    rx.box(
                        rx.cond(
                            ConfiguracionState.logo_preview != "",
                            rx.image(
                                src=ConfiguracionState.logo_preview,
                                height="60px",
                                width="auto",
                                max_width="140px",
                                object_fit="contain",
                                alt="Logo",
                                margin_bottom="2",
                                cursor="pointer",
                            ),
                            rx.icon(
                                "building",
                                size=40,
                                color="#3b82f6",
                                margin_bottom="2",
                                cursor="pointer",
                            ),
                        ),
                        _hover={"transform": "scale(1.05)", "transition": "transform 0.2s"},
                    )
                ),
                rx.hover_card.content(
                    rx.vstack(
                        # Encabezado con Logo y Nombre
                        rx.hstack(
                            rx.avatar(
                                src=ConfiguracionState.logo_preview,
                                fallback="IV",
                                size="4",
                                radius="full",
                                color_scheme="blue",
                                variant="soft",
                                border="2px solid #e2e8f0",
                            ),
                            rx.vstack(
                                rx.text(
                                    ConfiguracionState.empresa["nombre_empresa"],
                                    size="3",
                                    weight="bold",
                                    color="#1e293b",
                                ),
                                rx.badge(
                                    f"NIT: {ConfiguracionState.empresa['nit']}",
                                    color_scheme="gray",
                                    variant="surface",
                                    size="1",
                                ),
                                spacing="0",
                                align_items="start",
                            ),
                            spacing="3",
                            align_items="center",
                            width="100%",
                            padding_bottom="3",
                            border_bottom="1px solid #f1f5f9",
                        ),
                        # Detalles de la Empresa (Representante)
                        rx.vstack(
                            rx.text(
                                "Representante Legal",
                                size="1",
                                weight="bold",
                                color="#64748b",
                                margin_top="1",
                            ),
                            rx.hstack(
                                rx.icon("user-check", size=14, color="#3b82f6"),
                                rx.text(
                                    ConfiguracionState.empresa["representante_legal"],
                                    size="2",
                                    weight="medium",
                                    color="#334155",
                                ),
                                spacing="2",
                                align_items="center",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        # Contacto
                        rx.vstack(
                            rx.text(
                                "Contacto", size="1", weight="bold", color="#64748b", margin_top="1"
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("mail", size=14, color="#94a3b8"),
                                    rx.text(
                                        ConfiguracionState.empresa["email"],
                                        size="1",
                                        color="#475569",
                                    ),
                                    spacing="2",
                                    align_items="center",
                                ),
                                rx.hstack(
                                    rx.icon("phone", size=14, color="#94a3b8"),
                                    rx.text(
                                        ConfiguracionState.empresa["telefono"],
                                        size="1",
                                        color="#475569",
                                    ),
                                    spacing="2",
                                    align_items="center",
                                ),
                                rx.hstack(
                                    rx.icon("map-pin", size=14, color="#94a3b8"),
                                    rx.text(
                                        f"{ConfiguracionState.empresa['direccion']} - {ConfiguracionState.empresa['ubicacion']}",
                                        size="1",
                                        color="#475569",
                                    ),
                                    spacing="2",
                                    align_items="center",
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    side="right",
                    side_offset=20,
                    align="start",
                    background_color="white",
                    padding="16px",
                    border_radius="16px",
                    border="1px solid #e2e8f0",
                    box_shadow="0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                    width="280px",
                    data_state="open",
                    z_index="2000",
                ),
            ),
            rx.heading(
                rx.cond(
                    ConfiguracionState.empresa["nombre_empresa"] != "",
                    ConfiguracionState.empresa["nombre_empresa"],
                    "Inmobiliaria Velar",
                ),
                size="3",
                color="#1e293b",  # Dark text
                weight="bold",
                letter_spacing="-0.5px",
                text_align="center",
            ),
            spacing="1",
            padding_x="4",
            padding_y="6",
            align="center",
            width="100%",
        ),
        rx.divider(
            color_scheme="gray", opacity=0.5, margin_y="0"
        ),  # Changed opacity for visibility
        # Navigation Links
        rx.box(
            sidebar_items(),
            padding_y="4",
            overflow_y="auto",
            flex="1",
        ),
        # Footer User Profile
        sidebar_footer(),
        height="100vh",
        width="280px",
        background="rgba(0, 0, 51, 0.06)",  # Changed background
        position="sticky",
        top="0",
        left="0",
        display=["none", "none", "flex", "flex"],
        flex_direction="column",
        box_shadow="2px 0 8px rgba(0, 0, 0, 0.1)",
        on_mount=ConfiguracionState.cargar_datos_empresa,
    )
