import reflex as rx

from src.presentacion_reflex.state.alertas_state import AlertasState


def notification_item(item: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon(
                rx.cond(item["nivel"] == "danger", "circle_alert", "info"),
                color=rx.cond(item["nivel"] == "danger", "var(--red-9)", "var(--blue-9)"),
                size=20,
            ),
            rx.vstack(
                rx.text(item["mensaje"], size="2", weight="medium", color="#1f2937"),
                rx.text(f"Fecha: {item['fecha']}", size="1", color="#6b7280"),
                spacing="1",
                align="start",
            ),
            align="start",
            spacing="3",
        ),
        padding="3",
        border_bottom="1px solid #f3f4f6",
        _hover={"bg": "#f9fafb"},
        cursor="pointer",
        transition="all 0.2s ease",
    )


def bell_icon() -> rx.Component:
    return rx.box(
        rx.html(
            """
            <style>
                @keyframes bell-ring {
                    0% { transform: rotate(0); }
                    10% { transform: rotate(30deg); }
                    20% { transform: rotate(0); }
                    30% { transform: rotate(-30deg); }
                    40% { transform: rotate(0); }
                    100% { transform: rotate(0); }
                }
                .bell-ringing {
                    animation: bell-ring 2.5s infinite ease-in-out;
                    transform-origin: top center;
                }
                @keyframes pulse-ring {
                    0% { transform: scale(0.8); opacity: 0.8; }
                    100% { transform: scale(2.5); opacity: 0; }
                }
                .pulse-circle {
                    position: absolute;
                    top: -2px;
                    right: -2px;
                    width: 12px;
                    height: 12px;
                    background: rgba(239, 68, 68, 0.6);
                    border-radius: 50%;
                    animation: pulse-ring 1.5s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
                    z-index: 0;
                }
                .notification-badge-shine {
                    position: absolute;
                    top: 0;
                    right: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 60%);
                    border-radius: 50%;
                    opacity: 0.6;
                }
            </style>
        """
        ),
        rx.popover.root(
            rx.popover.trigger(
                rx.box(
                    rx.button(
                        rx.box(
                            # Contenedor del Icono con animación condicional
                            rx.box(
                                rx.icon(
                                    "bell",
                                    size=24,
                                    color="#fbbf24",
                                ),
                                class_name=rx.cond(
                                    AlertasState.unread_count > 0, "bell-ringing", ""
                                ),
                                style={"transition": "color 0.3s ease"},
                            ),
                            # Badge de Notificaciones
                            rx.cond(
                                AlertasState.unread_count > 0,
                                rx.box(
                                    # Círculo pulsante (efecto radar)
                                    rx.box(class_name="pulse-circle"),
                                    # Badge principal
                                    rx.center(
                                        rx.text(
                                            AlertasState.unread_count,
                                            color="white",
                                            size="1",
                                            weight="bold",
                                            style={"font-size": "10px", "line-height": "1"},
                                        ),
                                        bg="linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)",  # Red gradient
                                        border_radius="full",
                                        width="16px",
                                        height="16px",
                                        box_shadow="0 2px 4px rgba(220, 38, 38, 0.4)",
                                        z_index="1",
                                        position="relative",
                                        # Brillo sutil
                                        _before={
                                            "content": "''",
                                            "position": "absolute",
                                            "top": "1px",
                                            "left": "3px",
                                            "width": "4px",
                                            "height": "4px",
                                            "background": "rgba(255,255,255,0.4)",
                                            "border_radius": "50%",
                                        },
                                    ),
                                    position="absolute",
                                    top="-4px",
                                    right="-4px",
                                    width="16px",
                                    height="16px",
                                ),
                            ),
                            position="relative",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),
                        variant="ghost",
                        size="3",
                        padding="2",
                        on_click=AlertasState.check_alerts,
                        _hover={
                            "bg": "rgba(255, 255, 255, 0.1)",
                            "transform": "scale(1.05)",
                        },
                        style={"transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"},
                    ),
                    cursor="pointer",
                )
            ),
            rx.popover.content(
                rx.vstack(
                    rx.hstack(
                        rx.icon("bell-ring", size=18, color="#ef4444"),
                        rx.text("Notificaciones", weight="bold", size="3", color="#111827"),
                        rx.spacer(),
                        rx.badge(
                            f"{AlertasState.unread_count} nuevas",
                            color_scheme="red",
                            variant="surface",
                            radius="full",
                        ),
                        width="100%",
                        padding="4",
                        border_bottom="1px solid #e5e7eb",
                        align="center",
                        bg="#f9fafb",
                    ),
                    rx.scroll_area(
                        rx.vstack(
                            rx.cond(
                                AlertasState.notifications,
                                rx.foreach(AlertasState.notifications, notification_item),
                                rx.center(
                                    rx.vstack(
                                        rx.icon("circle_check", size=48, color="#e5e7eb"),
                                        rx.text("¡Todo al día!", color="#9ca3af", weight="medium"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    padding="8",
                                    width="100%",
                                ),
                            ),
                            width="100%",
                            gap="0",
                        ),
                        type="auto",
                        scrollbars="vertical",
                        style={"height": "320px", "max-height": "400px"},
                    ),
                    gap="0",
                    width="340px",
                    bg="white",
                    border_radius="16px",
                    box_shadow="0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                    border="1px solid #e5e7eb",
                    overflow="hidden",
                ),
                side_offset=15,
                z_index="9999", # Ensure it's above Mobile Drawer (z-100) and everything else
            ),
        ),
    )
