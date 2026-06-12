import reflex as rx
from typing import Optional

def badge_grupo_pago(grupo_operativo: rx.Var[int], fecha_pago: Optional[rx.Var[str]] = None) -> rx.Component:
    """
    Componente Badge dinámico que visualiza la fecha de pago con el color y 
    tooltip correspondiente al grupo operativo, soportando variables reactivas.
    """
    color = rx.match(
        grupo_operativo,
        (1, "orange"),
        (2, "tomato"),
        (3, "cyan"),
        "gray"
    )
    
    label = rx.match(
        grupo_operativo,
        (1, "Grupo 1: Contratos iniciados entre día 28 y 7. Pago programado: 10 de cada mes."),
        (2, "Grupo 2: Contratos iniciados entre día 8 y 17. Pago programado: 20 de cada mes."),
        (3, "Grupo 3: Contratos iniciados entre día 18 y 27. Pago programado: 30 de cada mes (truncado a fin de mes si aplica)."),
        "Sin grupo asignado"
    )

    if fecha_pago is None:
        badge_text = rx.match(
            grupo_operativo,
            (1, "Grupo 1"),
            (2, "Grupo 2"),
            (3, "Grupo 3"),
            "N/A"
        )
        return rx.tooltip(
            rx.badge(
                badge_text,
                color_scheme=color,
                variant="soft",
                cursor="help",
            ),
            content=label,
        )
    else:
        badge_text = rx.cond(
            fecha_pago != "", f"Día {fecha_pago}", "N/R"
        )
        return rx.cond(
            fecha_pago != "",
            rx.tooltip(
                rx.badge(
                    badge_text,
                    color_scheme=color,
                    variant="soft",
                    cursor="help",
                ),
                content=label,
            ),
            rx.text("N/R", size="1", color="var(--gray-9)", font_style="italic")
        )
