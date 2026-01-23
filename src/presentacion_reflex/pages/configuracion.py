
import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.configuracion_state import ConfiguracionState
from src.dominio.entidades.parametro_sistema import ParametroSistema

# --- ESTILOS & CONSTANTES ---
CARD_STYLE = {
    "background": "white",
    "border_radius": "16px",
    "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "padding": "2rem",
    "border": "1px solid rgba(226, 232, 240, 0.8)"
}

SECTION_TITLE_STYLE = {
    "font_size": "1.1rem",
    "font_weight": "bold",
    "color": "#1e293b", # Slate 800
    "letter_spacing": "-0.01em",
    "display": "flex",
    "align_items": "center",
    "gap": "0.5rem"
}

def elite_input_field(label: str, placeholder: str, field_name: str, icon_tag: str, type_: str = "text") -> rx.Component:
    """Campo de entrada con diseño elite y validación visual."""
    return rx.vstack(
        rx.text(label, font_size="0.875rem", weight="medium", color="#64748b"),
        rx.box(
            rx.icon(icon_tag, size=18, color="#94a3b8", position="absolute", left="12px", top="50%", transform="translateY(-50%)", z_index="1"),
            rx.input(
                placeholder=placeholder,
                value=ConfiguracionState.empresa[field_name],
                type=type_,
                on_change=lambda val: ConfiguracionState.set_empresa_field(field_name, val),
                variant="soft",
                color_scheme="gray",
                radius="full",
                padding_left="40px",
                width="100%",
                style={"_focus": {"box_shadow": "0 0 0 2px #3b82f6", "background": "white"}}
            ),
            position="relative",
            width="100%"
        ),
        spacing="2",
        width="100%"
    )

def company_identity_card() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.icon("building", size=24, color="#3b82f6"),
            rx.text("Identidad Corporativa", style=SECTION_TITLE_STYLE),
            display="flex", align_items="center", gap="3", margin_bottom="4"
        ),
        rx.grid(
            rx.vstack(
                rx.text("Nombre Legal", font_size="0.875rem", weight="medium", color="#64748b"),
                rx.input(
                    value=ConfiguracionState.empresa["nombre_empresa"],
                    on_change=lambda val: ConfiguracionState.set_empresa_field("nombre_empresa", val),
                    placeholder="Ej. Inmobiliaria Velar S.A.S.",
                    variant="soft", radius="large", width="100%"
                ),
                width="100%"
            ),
            rx.vstack(
                rx.text("NIT / RUC", font_size="0.875rem", weight="medium", color="#64748b"),
                rx.input(
                    value=ConfiguracionState.empresa["nit"],
                    on_change=lambda val: ConfiguracionState.set_empresa_field("nit", val),
                    placeholder="Ej. 900.000.000-1",
                    variant="soft", radius="large", width="100%"
                ),
                width="100%"
            ),
            columns="2", spacing="4", width="100%"
         ),
         rx.grid(
            rx.vstack(
                rx.text("Representante Legal", font_size="0.875rem", weight="medium", color="#64748b"),
                rx.input(
                    value=ConfiguracionState.empresa["representante_legal"],
                    on_change=lambda val: ConfiguracionState.set_empresa_field("representante_legal", val),
                    placeholder="Nombre del Representante",
                    variant="soft", radius="large", width="100%"
                ),
                width="100%"
            ),
            rx.vstack(
                rx.text("Cédula Representante", font_size="0.875rem", weight="medium", color="#64748b"),
                rx.input(
                    value=ConfiguracionState.empresa["cedula_representante"],
                    on_change=lambda val: ConfiguracionState.set_empresa_field("cedula_representante", val),
                    placeholder="Número de Documento",
                    variant="soft", radius="large", width="100%"
                ),
                width="100%"
            ),
            columns="2", spacing="4", width="100%", margin_top="4"
        ),
        rx.divider(margin_y="4", opacity="0.4"),
        rx.vstack(
            rx.text("Logo de la Empresa", font_size="0.875rem", weight="medium", color="#64748b", margin_bottom="3"),
            # Mostrar logo cargado O área de upload
            rx.cond(
                ConfiguracionState.logo_preview != "",
                # Si HAY logo: diseño limpio y organizado
                rx.vstack(
                    # Área de preview del logo
                    rx.center(
                        rx.image(
                            src=ConfiguracionState.logo_preview,
                            width="140px",
                            height="140px",
                            border_radius="12px",
                            object_fit="contain",
                            border="2px solid #e2e8f0",
                            background="white",
                            padding="3"
                        ),
                        width="100%",
                        padding="4",
                        background="#fafafa",
                        border_radius="12px"
                    ),
                    # Información del archivo
                    rx.hstack(
                        rx.icon("file-image", size=14, color="#64748b"),
                        rx.text(
                            ConfiguracionState.logo_filename,
                            font_size="0.75rem",
                            color="#475569",
                            weight="medium"
                        ),
                        spacing="2",
                        align_items="center",
                        justify="center",
                        width="100%"
                     ),
                    # Botones de acción
                    rx.hstack(
                        rx.upload(
                            rx.button(
                                rx.icon("refresh-cw", size=14),
                                "Cambiar Logo",
                                size="2",
                                variant="soft",
                                color_scheme="blue",
                                width="100%"
                            ),
                            id="logo_upload",
                            multiple=False,
                            accept={
                                "image/png": [".png"],
                                "image/jpeg": [".jpg", ".jpeg"]
                            },
                            max_files=1,
                            on_drop=ConfiguracionState.handle_upload_logo(rx.upload_files(upload_id="logo_upload")),
                            border="none",
                            padding="0",
                            width="calc(50% - 0.25rem)",
                            display="block"
                        ),
                        rx.button(
                            rx.icon("trash-2", size=14),
                            "Eliminar",
                            size="2",
                            variant="outline",
                            color_scheme="red",
                            on_click=ConfiguracionState.clear_logo,
                            width="calc(50% - 0.25rem)"
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    spacing="3",
                    width="100%"
                ),
                # Si NO hay logo: mostrar área de upload
                rx.upload(
                    rx.vstack(
                        rx.center(
                            rx.icon("image", size=40, color="#cbd5e1"),
                            width="100px", 
                            height="100px", 
                            background="#f1f5f9", 
                            border_radius="12px",
                            border="2px dashed #cbd5e1"
                        ),
                        rx.text(
                            "Arrastra tu logo aquí o haz clic",
                            font_size="0.875rem",
                            weight="medium",
                            color="#334155"
                        ),
                        rx.text(
                            "PNG, JPG • Máximo 1MB • Recomendado: 500x500px",
                            font_size="0.75rem",
                            color="#94a3b8"
                        ),
                        rx.button(
                            rx.icon("upload", size=14),
                            "Seleccionar archivo",
                            size="2",
                            variant="soft",
                            color_scheme="blue"
                        ),
                        spacing="3",
                        align_items="center",
                        padding="6",
                        border="2px dashed #cbd5e1",
                        border_radius="12px",
                        _hover={"border_color": "#3b82f6", "background": "#f8fafc"},
                        transition="all 0.2s",
                        cursor="pointer",
                        width="100%"
                    ),
                    id="logo_upload",
                    multiple=False,
                    accept={
                        "image/png": [".png"],
                        "image/jpeg": [".jpg", ".jpeg"]
                    },
                    max_files=1,
                    on_drop=ConfiguracionState.handle_upload_logo(rx.upload_files(upload_id="logo_upload")),
                )
            ),
            spacing="2",
            width="100%"
        ),
        style=CARD_STYLE,
        width="100%"
    )

def contact_location_card() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.icon("map-pin", size=24, color="#10b981"), # Emerald 500
            rx.text("Ubicación y Contacto", style=SECTION_TITLE_STYLE),
            display="flex", align_items="center", gap="3", margin_bottom="4"
        ),
        rx.grid(
            elite_input_field("Correo Electrónico", "contacto@empresa.com", "email", "mail"),
            elite_input_field("Teléfono / Móvil", "+57 300 000 0000", "telefono", "phone"),
            elite_input_field("Dirección Física", "Calle 123 # 45 - 67", "direccion", "map-pin"),
            elite_input_field("Ciudad / Ubicación", "Bogotá D.C.", "ubicacion", "globe"),
            columns="2", spacing="5", width="100%"
        ),
        rx.box(
            elite_input_field("Sitio Web", "https://www.miempresa.com", "website", "link"),
            margin_top="4", width="100%"
        ),
        rx.divider(margin_y="4", opacity="0.4"),
        rx.vstack(
            rx.hstack(
                rx.icon("share-2", size=20, color="#8b5cf6"),  # Purple for social
                rx.text("Redes Sociales", font_size="0.95rem", weight="medium", color="#1e293b"),
                spacing="2"
            ),
            rx.grid(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            width="20px", height="20px", 
                            background="#1877f2", 
                            border_radius="4px",
                            display="flex",
                            align_items="center",
                            justify_content="center"
                        ),
                        rx.text("Facebook", font_size="0.875rem", weight="medium", color="#64748b"),
                        spacing="2"
                    ),
                    rx.input(
                        placeholder="@tuempresa",
                        value=ConfiguracionState.empresa["facebook"],
                        on_change=lambda val: ConfiguracionState.set_empresa_field("facebook", val),
                        variant="soft",
                        color_scheme="gray",
                        width="100%"
                    ),
                    width="100%"
                ),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            width="20px", height="20px",
                            background="linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%)",
                            border_radius="4px",
                            display="flex",
                            align_items="center",
                            justify_content="center"
                        ),
                        rx.text("Instagram", font_size="0.875rem", weight="medium", color="#64748b"),
                        spacing="2"
                    ),
                    rx.input(
                        placeholder="@tuempresa",
                        value=ConfiguracionState.empresa["instagram"],
                        on_change=lambda val: ConfiguracionState.set_empresa_field("instagram", val),
                        variant="soft",
                        color_scheme="gray",
                        width="100%"
                    ),
                    width="100%"
                ),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            width="20px", height="20px",
                            background="#000000",
                            border_radius="4px",
                            display="flex",
                            align_items="center",
                            justify_content="center"
                        ),
                        rx.text("TikTok", font_size="0.875rem", weight="medium", color="#64748b"),
                        spacing="2"
                    ),
                    rx.input(
                        placeholder="@tuempresa",
                        value=ConfiguracionState.empresa["tiktok"],
                        on_change=lambda val: ConfiguracionState.set_empresa_field("tiktok", val),
                        variant="soft",
                        color_scheme="gray",
                        width="100%"
                    ),
                    width="100%"
                ),
                columns="3",
                spacing="4",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        style=CARD_STYLE,
        width="100%"
    )

def company_tab_content() -> rx.Component:
    return rx.vstack(
        rx.grid(
            company_identity_card(),
            contact_location_card(),
            columns=rx.breakpoints(initial="1", lg="2"),
            spacing="6",
            width="100%"
        ),
        rx.box(
            rx.button(
                rx.hstack(rx.icon("save", size=18), rx.text("Guardar Cambios")),
                on_click=ConfiguracionState.guardar_empresa_click,
                size="3",
                variant="solid",
                color_scheme="blue",
                padding_x="2rem",
                box_shadow="0 4px 14px 0 rgba(0,118,255,0.39)",
                _hover={"transform": "translateY(-2px)", "box_shadow": "0 6px 20px rgba(0,118,255,0.23)"},
                transition="all 0.2s ease"
            ),
            position="sticky",
            bottom="20px",
            display="flex",
            justify_content="flex-end",
            width="100%",
            padding_top="4",
            z_index="10"
        ),
        spacing="6",
        width="100%",
        max_width="1200px",
        margin="0 auto"
    )

# --- SISTEMA ---

def parameter_badge(categoria: str) -> rx.Component:
    colors = {
        "FINANCIERO": "green",
        "LEGAL": "blue",
        "SISTEMA": "gray",
        "NOTIFICACIONES": "orange"
    }
    color = colors.get(categoria, "violet")
    return rx.badge(
        categoria, 
        color_scheme=color, 
        variant="soft", 
        radius="full",
        padding_x="2"
    )

def system_tab_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("settings-2", size=24, color="#6366f1"),
                rx.text("Parámetros Globales", style=SECTION_TITLE_STYLE),
                margin_bottom="4"
            ),
            rx.text(
                "Estos valores afectan el comportamiento de cálculos y lógica del sistema. Modificar con precaución.",
                color="gray", margin_bottom="4"
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Parámetro", padding_left="4"),
                        rx.table.column_header_cell("Categoría"),
                        rx.table.column_header_cell("Valor Actual"),
                        rx.table.column_header_cell("Estado"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        ConfiguracionState.parametros,
                        lambda param: rx.table.row(
                            rx.table.cell(
                                rx.vstack(
                                    rx.text(param.nombre_parametro, weight="bold", color="#334155"),
                                    rx.text(param.descripcion, font_size="0.75rem", color="#94a3b8"),
                                    spacing="1"
                                ),
                                padding_y="3",
                                padding_left="4"
                            ),
                            rx.table.cell(parameter_badge(param.categoria)),
                            rx.table.cell(
                                rx.cond(
                                    param.modificable == 1,
                                    rx.hstack(
                                        rx.input(
                                            default_value=param.valor_parametro,
                                            on_blur=lambda val: ConfiguracionState.actualizar_parametro(param.id_parametro, val),
                                            width="120px",
                                            size="2",
                                            variant="soft"
                                        ),
                                        rx.icon("edit-2", size=14, color="#cbd5e1")
                                    ),
                                    rx.text(param.valor_parametro, weight="bold", font_family="monospace")
                                )
                            ),
                            rx.table.cell(
                                rx.cond(
                                    param.modificable == 1,
                                    rx.icon("unlock", size=16, color="#10b981", tooltip="Editable"),
                                    rx.icon("lock", size=16, color="#ef4444", tooltip="Solo Lectura de Sistema")
                                )
                            ),
                            _hover={"background": "#f8fafc"}
                        )
                    )
                ),
                variant="surface",
                size="2",
                width="100%",
                style={"border_radius": "12px", "overflow": "hidden"}
            ),
            style=CARD_STYLE,
            width="100%"
        ),
        width="100%",
        max_width="1200px",
        margin="0 auto"
    )

def configuracion_content() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.heading("Configuración & Administración", size="8", weight="bold", letter_spacing="-0.03em", color="#1e293b"),
            rx.text("Gestión centralizada de la identidad corporativa y parámetros del sistema.", color="#64748b", size="4", margin_top="2"),
            padding_bottom="6",
            border_bottom="1px solid #e2e8f0",
            width="100%",
            max_width="1200px",
            margin_x="auto"
        ),
        
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Empresa", value="empresa", style={"font_size": "1rem", "padding_y": "12px"}),
                rx.tabs.trigger("Sistema", value="sistema", style={"font_size": "1rem", "padding_y": "12px"}),
                size="2",
            ),
            rx.tabs.content(company_tab_content(), value="empresa", padding_top="6"),
            rx.tabs.content(system_tab_content(), value="sistema", padding_top="6"),
            default_value="empresa",
            width="100%",
            max_width="1200px",
            margin_x="auto"
        ),
        
        width="100%",
        spacing="6",
        padding="8",
        background="#f8fafc", # Slate 50 background global
        min_height="100vh",
        on_mount=ConfiguracionState.on_load
    )

@rx.page(route="/configuracion", title="Configuración | Inmobiliaria Velar")
def configuracion_page() -> rx.Component:
    return dashboard_layout(configuracion_content())
