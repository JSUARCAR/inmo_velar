"""
Entry Point: Sistema de Gestión Inmobiliaria - Reflex
Versión web moderna con React bajo el capó.

FASE 0: Proof of Concept - Página de Bienvenida
"""

import reflex as rx


def index() -> rx.Component:
    """Página temporal de bienvenida durante la migración."""
    return rx.center(
        rx.vstack(
            rx.heading("🏢 Inmobiliaria Velar", size="9", weight="bold"),
            rx.text(
                "Sistema en Migración a Reflex", 
                size="5", 
                color="gray"
            ),
            rx.badge(
                "Fase 0: Preparación Completada ✓", 
                color_scheme="green",
                size="3"
            ),
            rx.divider(margin_y="4"),
            rx.text(
                "Framework: Reflex v0.8.24",
                size="2",
                color="gray"
            ),
            rx.text(
                "Puerto: 3000",
                size="2",
                color="gray"
            ),
            rx.text(
                "Base de Datos: SQLite (Compartida con Flet)",
                size="2",
                color="gray"
            ),
            rx.divider(margin_y="4"),
            rx.hstack(
                rx.button(
                    "📋 Ver Progreso",
                    on_click=rx.redirect("/progreso"),
                    variant="soft",
                ),
                rx.button(
                    "🚀 Próximo: Login (Fase 1)",
                    variant="outline",
                    disabled=True,
                ),
                spacing="3",
            ),
            spacing="4",
            align="center",
        ),
        height="100vh",
        background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    )


def progreso_page() -> rx.Component:
    """Página de progreso de la migración."""
    return rx.container(
        rx.vstack(
            rx.heading("📊 Progreso de Migración Flet → Reflex", size="8"),
            
            rx.card(
                rx.vstack(
                    rx.text("Fase 0: Preparación y Setup", weight="bold", size="4"),
                    rx.progress(value=100, color_scheme="green"),
                    rx.text("✅ Completado", color="green", size="2"),
                    spacing="2",
                ),
                width="100%",
            ),
            
            rx.card(
                rx.vstack(
                    rx.text("Fase 1: Core Architecture", weight="bold", size="4"),
                    rx.progress(value=0, color_scheme="blue"),
                    rx.text("⏳ Pendiente", color="gray", size="2"),
                    spacing="2",
                ),
                width="100%",
            ),
            
            rx.card(
                rx.vstack(
                    rx.heading("Componentes Inventariados", size="5"),
                    rx.hstack(
                        rx.stat(
                            rx.stat_label("Vistas"),
                            rx.stat_number("39"),
                            rx.stat_help_text("views/*.py"),
                        ),
                        rx.stat(
                            rx.stat_label("Componentes"),
                            rx.stat_number("16"),
                            rx.stat_help_text("components/"),
                        ),
                        rx.stat(
                            rx.stat_label("Servicios"),
                            rx.stat_number("19"),
                            rx.stat_help_text("sin cambios"),
                        ),
                        spacing="6",
                    ),
                    spacing="3",
                ),
                width="100%",
            ),
            
            rx.divider(),
            
            rx.link(
                rx.button("← Volver al Inicio", variant="soft"),
                href="/",
            ),
            
            spacing="6",
            max_width="800px",
            padding_y="8",
        ),
        max_width="900px",
    )


# Configurar aplicación
app = rx.App()

# Registrar páginas
app.add_page(index, route="/", title="Inmobiliaria Velar - Migración")
app.add_page(progreso_page, route="/progreso", title="Progreso de Migración")
