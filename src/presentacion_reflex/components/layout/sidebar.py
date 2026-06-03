import reflex as rx

from src.presentacion_reflex import styles
from src.presentacion_reflex.components.layout.bell_icon import bell_icon
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.configuracion_state import ConfiguracionState


def sidebar_item(
    text: str,
    icon: str,
    url: str,
    description: str = "",
    module_name: str = "",
) -> rx.Component:
    """Item individual del sidebar con HoverCard experto y protección por permisos."""
    is_active = rx.State.router.page.path == url

    resolved_icon_color = rx.cond(
        is_active, styles.BRAND_PRIMARY, styles.TEXT_SECONDARY
    )

    # Envoltura interna para mantener los iconos perfectamente alineados pero el bloque centrado
    inner_content = rx.hstack(
        rx.icon(
            icon,
            size=20,
            color=resolved_icon_color,
        ),
        rx.text(
            text,
            size="3",
            weight=rx.cond(is_active, "bold", "medium"),
            color=rx.cond(
                rx.color_mode == "light",
                rx.cond(is_active, "#0f172a", "#334155"),
                "white",
            ),
        ),
        spacing="3",
        align="center",
        width="200px",  # Anchura fija para alinear el contenido internamente
        justify="start",
    )

    # Base item content (Trigger)
    item_content = rx.hstack(
        inner_content,
        padding_y="3",
        border_radius="10px",
        border="none",
        background=styles.BG_PANEL,
        box_shadow=rx.cond(is_active, styles.NEU_INSET, "none"),
        _hover={
            "box_shadow": rx.cond(
                is_active,
                styles.NEU_INSET,
                styles.NEU_SHADOW,  # Elevado al hover
            ),
        },
        width="100%",
        justify="center",  # Esto centra el inner_content de 200px perfectamente en la píldora
        align="center",
        transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
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
                rx.cond(
                    description != "",
                    description,
                    f"Acceder al módulo de {text}",
                ),
                size="2",
                color="#4b5563",
                line_height="1.5",
            ),
            spacing="2",
            align="start",
        ),
        side="right",
        side_offset=15,
        align="center",
        avoid_collisions=True,
        background_color=styles.BG_PANEL,
        padding="16px",
        border_radius="16px",
        border="none",
        box_shadow=styles.NEU_SHADOW,
        width="260px",
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

    return item_component


def sidebar_section(title: str, *items) -> rx.Component:
    """Sección del sidebar con título y items."""
    return rx.vstack(
        # Contenedor para alinear el título con exactitud sobre los iconos (200px de ancho central)
        rx.box(
            rx.text(
                title,
                size="1",
                color=rx.cond(rx.color_mode == "light", "#64748b", "white"),
                weight="bold",
                letter_spacing="0.5px",
            ),
            width="200px",
            margin_x="auto",  # Centra la caja al igual que los links
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
            ),
            sidebar_item(
                "Alertas Tempranas",
                "bell_ring",
                "/alertas",
                "Gestión proactiva de vencimientos de contratos, recibos y eventos críticos.",
                module_name="Dashboard", # Reutilizamos Dashboard por ahora para visibilidad compartida
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
            ),
            sidebar_item(
                "Propiedades",
                "home",
                "/propiedades",
                "Administración del inventario de inmuebles, características y estados.",
                module_name="Propiedades",
            ),
            sidebar_item(
                "Contratos",
                "file_text",
                "/contratos",
                "Control de contratos de mandato y arrendamiento vigentes e históricos.",
                module_name="Contratos",
            ),
            sidebar_item(
                "Prop. Horizontal",
                "building",
                "/propiedad-horizontal",
                "Gestión de asambleas y pagos de administración de PH.",
                module_name="Propiedad Horizontal",
            ),
            sidebar_item(
                "Proveedores",
                "wrench",
                "/proveedores",
                "Directorio y gestión de proveedores de servicios y mantenimiento.",
                module_name="Proveedores",
            ),
        ),
        # Sección Operaciones
        sidebar_section(
            "OPERACIONES",
            sidebar_item(
                "Liquidaciones",
                "dollar_sign",
                "/liquidaciones",
                "Gestión de liquidaciones de arriendo, cálculo de intereses y mora.",
                module_name="Liquidaciones",
            ),
            sidebar_item(
                "Liquidación Asesores",
                "user_check",
                "/liquidacion-asesores",
                "Cálculo y pago de comisiones, bonificaciones y estructura comercial.",
                module_name="Liquidación Asesores",
            ),
            sidebar_item(
                "Recaudos",
                "coins",
                "/recaudos",
                "Registro y seguimiento de pagos recibidos de arrendatarios.",
                module_name="Recaudos",
            ),
            sidebar_item(
                "Desocupaciones",
                "log_out",
                "/desocupaciones",
                "Gestión de procesos de desocupación, inspecciones y restitución.",
                module_name="Desocupaciones",
            ),
            sidebar_item(
                "Incidentes",
                "triangle-alert",
                "/incidentes",
                "Seguimiento y resolución de incidencias, reparaciones y mantenimiento.",
                module_name="Incidentes",
            ),
            sidebar_item(
                "Seguros",
                "shield",
                "/seguros",
                "Control de pólizas de seguro de arrendamiento y hogar.",
                module_name="Seguros",
            ),
            sidebar_item(
                "Recibos Públicos",
                "zap",
                "/recibos-publicos",
                "Gestión de pagos y control de servicios públicos de los inmuebles.",
                module_name="Recibos Públicos",
            ),
            sidebar_item(
                "Saldos a Favor",
                "piggy-bank",
                "/saldos-favor",
                "Administración de saldos a favor de terceros y devoluciones.",
                module_name="Saldos a Favor",
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
            ),
            sidebar_item(
                "Configuración",
                "settings",
                "/configuracion",
                "Ajustes generales del sistema y parámetros globales.",
                module_name="Configuración",
            ),
            sidebar_item(
                "IPC / Incrementos",
                "trending_up",
                "/incrementos",
                "Aplicación de incrementos anuales e indexación masiva por IPC.",
                module_name="IPC / Incrementos",
            ),
            sidebar_item(
                "Auditoría",
                "clipboard_list",
                "/auditoria",
                "Registro detallado (logs) de cambios y actividades en el sistema.",
                module_name="Auditoría",
            ),
            sidebar_item(
                "Reportes",
                "file-bar-chart",
                "/reportes",
                "Generación y exportación de reportes detallados en CSV.",
                module_name="Reportes",
            ),
        ),
        spacing="0",
        width="100%",
    )


def sidebar_footer() -> rx.Component:
    """Pie del sidebar con perfil de usuario."""
    from src.presentacion_reflex.components.layout.theme_toggle import theme_toggle_icon

    return rx.hstack(
        rx.icon("user-check", size=30, color="var(--text-secondary)"),
        rx.vstack(
            rx.text(
                AuthState.user_nombre,
                size="2",
                weight="bold",
                color=rx.cond(rx.color_mode == "light", "#1e293b", "white"),
                max_width="100px",  # Reducido para evitar overlap con botones
                overflow="hidden",
                white_space="nowrap",
                text_overflow="ellipsis",
            ),
            rx.text(
                AuthState.user_rol,
                size="1",
                color=rx.cond(rx.color_mode == "light", "#64748b", "white"),
                max_width="100px",
                overflow="hidden",
                white_space="nowrap",
                text_overflow="ellipsis",
            ),
            spacing="0",
            align_items="start",
        ),
        rx.spacer(),
        rx.hstack(
            theme_toggle_icon(),
            bell_icon(),
            rx.tooltip(
                rx.icon_button(
                    rx.icon("log-out", size=18, color="var(--red-9)"),
                    size="2",
                    variant="soft",
                    color_scheme="gray",
                    radius="full",
                    background=styles.BG_PANEL,
                    border="none",
                    box_shadow=styles.NEU_SHADOW,
                    _active={
                        "box_shadow": styles.NEU_INSET,
                        "transform": "scale(0.95)",
                    },
                    _hover={
                        "transform": "translateY(-1px)",
                        "box_shadow": styles.NEU_SHADOW,
                    },
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    on_click=AuthState.logout,
                    width="32px",
                    height="32px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                content="Cerrar Sesión",
            ),
            spacing="3",  # Ajuste a 3 para respiración eq. a 12px
            align_items="center",
        ),
        spacing="2",  # Reducido padding del flex base
        width="100%",
        align_items="center",
        padding_top="2",
        padding_x="4",
        padding_bottom="4",
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
                                color="var(--brand-primary)",
                                margin_bottom="2",
                                cursor="pointer",
                            ),
                        ),
                        _hover={
                            "transform": "scale(1.05)",
                            "transition": "transform 0.2s",
                        },
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
                                    "NIT: ",
                                    ConfiguracionState.empresa["nit"],
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
                                rx.icon(
                                    "user-check", size=14, color="var(--text-tertiary)"
                                ),
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
                                "Contacto",
                                size="1",
                                weight="bold",
                                color="#64748b",
                                margin_top="1",
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
                                        ConfiguracionState.empresa["direccion"],
                                        " - ",
                                        ConfiguracionState.empresa["ubicacion"],
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
                    background_color=styles.BG_PANEL,
                    padding="16px",
                    border_radius="16px",
                    border="none",
                    box_shadow=styles.NEU_SHADOW,
                    width="280px",
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
                color=rx.cond(rx.color_mode == "light", "#1e293b", "white"),
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
            padding_x="4",
            overflow_y="auto",
            flex="1",
            width="100%",
        ),
        # Footer User Profile
        sidebar_footer(),
        height="100vh",
        width="280px",
        background=styles.BG_PANEL,
        position="sticky",
        top="0",
        left="0",
        flex_direction="column",
        box_shadow=rx.cond(
            rx.color_mode == "light",
            "5px 0 15px rgba(163, 177, 198, 0.2)",
            "5px 0 15px rgba(0, 0, 0, 0.4)",
        ),
        on_mount=ConfiguracionState.cargar_datos_empresa,
        class_name="hide-on-mobile",
    )
