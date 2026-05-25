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
        (1, "Grupo 1: Contratos iniciados entre día 1 y 10. Pago programado: 10 de cada mes."),
        (2, "Grupo 2: Contratos iniciados entre día 11 y 20. Pago programado: 20 de cada mes."),
        (3, "Grupo 3: Contratos iniciados entre día 21 y 31. Pago programado: Fin de mes (30/31)."),
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
        return rx.cond(
            fecha_pago != "",
            rx.tooltip(
                rx.badge(
                    f"Día {fecha_pago}",
                    color_scheme=color,
                    variant="soft",
                    cursor="help",
                ),
                content=label,
            ),
            rx.text("N/R", size="1", color="var(--gray-9)", font_style="italic")
        )
