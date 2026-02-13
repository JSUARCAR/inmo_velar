"""
Vista: Detalle de Liquidación de Asesor (Modal)
Muestra información completa de una liquidación incluyendo descuentos y pagos.
"""

import os
from typing import Callable

import reflex as rx

from src.presentacion.components.document_manager import DocumentManager


def crear_modal_detalle_liquidacion(
    page: ft.Page,
    servicio_liquidacion_asesores,
    servicio_notificaciones,
    id_liquidacion: int,
    on_cerrar: Callable,
) -> ft.AlertDialog:
    """
    Crea un modal con el detalle completo de una liquidación.

    Args:
        page: Página de Flet
        servicio_liquidacion_asesores: Servicio de liquidaciones
        servicio_notificaciones: Servicio de notificaciones (Email)
        id_liquidacion: ID de la liquidación
        on_cerrar: Callback al cerrar

    Returns:
        AlertDialog configurado
    """

    try:
        # Obtener detalle completo
        detalle = servicio_liquidacion_asesores.obtener_detalle_completo(id_liquidacion)
        liquidacion = detalle["liquidacion"]
        descuentos = detalle["descuentos"]
        pagos = detalle["pagos"]

        # Color según estado
        color_estado = {
            "Pendiente": "#ff9800",
            "Aprobada": "#2196f3",
            "Pagada": "#4caf50",
            "Anulada": "#9e9e9e",
        }.get(liquidacion["estado_liquidacion"], "#666")

        # Sección de información general
        info_general = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Información General", size=16, weight=ft.FontWeight.BOLD, color="#1976d2"
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        [
                            ft.Text("Período:", weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(liquidacion["periodo_liquidacion"], size=13),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Text("Asesor ID:", weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(f"#{liquidacion['id_asesor']}", size=13),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Text("Contrato ID:", weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(f"#{liquidacion['id_contrato_a']}", size=13),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Text("Estado:", weight=ft.FontWeight.BOLD, size=13),
                            ft.Container(
                                content=ft.Text(
                                    liquidacion["estado_liquidacion"],
                                    color="white",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=color_estado,
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                border_radius=4,
                            ),
                        ]
                    ),
                ],
                spacing=10,
            ),
            bgcolor="#f5f5f5",
            padding=15,
            border_radius=8,
        )

        # Sección de información del predio (NUEVA)
        if detalle.get("propiedad"):
            prop = detalle["propiedad"]
            info_predio = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Información del Predio",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="#1976d2",
                        ),
                        ft.Divider(height=1),
                        ft.Row(
                            [
                                ft.Text("Contrato ID:", weight=ft.FontWeight.BOLD, size=13),
                                ft.Text(f"#{detalle['liquidacion']['id_contrato_a']}", size=13),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Text("Dirección:", weight=ft.FontWeight.BOLD, size=13),
                                ft.Text(prop["direccion_propiedad"] or "N/A", size=13),
                            ]
                        ),
                    ],
                    spacing=10,
                ),
                bgcolor="#e3f2fd",  # Azul claro para diferenciar
                padding=15,
                border_radius=8,
            )
        else:
            info_predio = ft.Container()

        # Sección de cálculos
        calculos = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Cálculo de Comisión", size=16, weight=ft.FontWeight.BOLD, color="#1976d2"
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        [
                            ft.Text("Canon Liquidado:", size=13),
                            ft.Text(
                                f"${liquidacion['canon_arrendamiento_liquidado']:,}",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text("Porcentaje Comisión:", size=13),
                            ft.Text(f"{liquidacion['porcentaje_real']:.2f}%", size=13),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text("Comisión Bruta:", size=13),
                            ft.Text(
                                f"${liquidacion['comision_bruta']:,}", size=13, color="#1976d2"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text("Total Descuentos:", size=13),
                            ft.Text(
                                f"${liquidacion['total_descuentos']:,}", size=13, color="#f44336"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        [
                            ft.Text("VALOR NETO:", size=15, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"${liquidacion['valor_neto_asesor']:,}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#4caf50",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=8,
            ),
            bgcolor="white",
            padding=15,
            border_radius=8,
            border=ft.border.all(1, "#e0e0e0"),
        )

        # Sección de contratos incluidos (NUEVA)
        contratos_asociados = detalle.get("contratos", [])
        if contratos_asociados:
            filas_contratos = []
            for contrato in contratos_asociados:
                # Calcular comisión individual para este contrato
                comision_individual = int(
                    contrato["canon_incluido"] * liquidacion["porcentaje_real"] / 100
                )

                filas_contratos.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Text(
                                    f"#{contrato['id_contrato']}",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                )
                            ),
                            ft.DataCell(ft.Text(contrato["direccion"], size=11)),
                            ft.DataCell(ft.Text(f"${contrato['canon_incluido']:,}", size=12)),
                            ft.DataCell(
                                ft.Text(f"${comision_individual:,}", size=12, color="#1976d2")
                            ),
                        ]
                    )
                )

            tabla_contratos = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(
                        ft.Text("Dirección Propiedad", size=12, weight=ft.FontWeight.BOLD)
                    ),
                    ft.DataColumn(ft.Text("Canon", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Comisión", size=12, weight=ft.FontWeight.BOLD)),
                ],
                rows=filas_contratos,
                border=ft.border.all(1, "#e0e0e0"),
                heading_row_color="#e3f2fd",
                heading_row_height=35,
                data_row_min_height=40,
            )

            seccion_contratos = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            f"Contratos Incluidos ({len(contratos_asociados)})",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="#1976d2",
                        ),
                        ft.Container(
                            content=tabla_contratos,
                            bgcolor="white",
                            border_radius=8,
                        ),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.only(top=15),
            )
        else:
            seccion_contratos = ft.Container()

        # Sección de descuentos
        if descuentos:
            filas_desc = []
            for desc in descuentos:
                filas_desc.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(desc["tipo_descuento"], size=12)),
                            ft.DataCell(ft.Text(desc["descripcion_descuento"], size=11)),
                            ft.DataCell(ft.Text(f"${desc['valor_descuento']:,}", size=12)),
                        ]
                    )
                )

            tabla_descuentos = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Tipo", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Descripción", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Valor", size=12, weight=ft.FontWeight.BOLD)),
                ],
                rows=filas_desc,
                border=ft.border.all(1, "#e0e0e0"),
                heading_row_color="#f5f5f5",
                heading_row_height=35,
                data_row_min_height=40,
            )

            seccion_descuentos = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.RECEIPT_LONG, color="#f44336", size=20),
                                ft.Text(
                                    "Egresos y Deducciones Aplicados",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#f44336",
                                ),
                            ]
                        ),
                        tabla_descuentos,
                        (
                            ft.Container(
                                content=ft.Text(
                                    "💡 Puede agregar más descuentos editando esta liquidación (si está pendiente)",
                                    size=11,
                                    color="#666",
                                    italic=True,
                                ),
                                padding=ft.padding.only(top=8),
                            )
                            if liquidacion["estado_liquidacion"] == "Pendiente"
                            else ft.Container()
                        ),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.only(top=15),
                bgcolor="#fff3f3",  # Fondo rosa muy suave para destacar
                border_radius=8,
                border=ft.border.all(1, "#ffcdd2"),
            )
        else:
            seccion_descuentos = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.RECEIPT_LONG, color="#999", size=20),
                                ft.Text(
                                    "Egresos y Deducciones",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#666",
                                ),
                            ]
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.CHECK_CIRCLE_OUTLINE, color="#4caf50", size=16
                                    ),
                                    ft.Text(
                                        "Sin descuentos aplicados - Valor neto = Comisión bruta",
                                        size=12,
                                        color="#666",
                                        italic=True,
                                    ),
                                ]
                            ),
                            padding=ft.padding.only(top=5),
                        ),
                    ]
                ),
                bgcolor="#f5f5f5",
                border_radius=8,
                padding=15,
            )

        # Sección de pagos
        if pagos:
            filas_pagos = []
            for pago in pagos:
                filas_pagos.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(f"${pago['valor_pago']:,}", size=12)),
                            ft.DataCell(ft.Text(pago["fecha_programada"] or "N/A", size=11)),
                            ft.DataCell(ft.Text(pago["estado_pago"], size=11)),
                        ]
                    )
                )

            tabla_pagos = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Valor", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Fecha Prog.", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Estado", size=12, weight=ft.FontWeight.BOLD)),
                ],
                rows=filas_pagos,
                border=ft.border.all(1, "#e0e0e0"),
                heading_row_color="#f5f5f5",
                heading_row_height=35,
                data_row_min_height=40,
            )

            seccion_pagos = ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Pagos", size=14, weight=ft.FontWeight.BOLD),
                        tabla_pagos,
                    ],
                    spacing=10,
                ),
                padding=ft.padding.only(top=15),
            )
        else:
            seccion_pagos = ft.Container(
                content=ft.Text("Sin pagos programados", size=12, color="#999", italic=True),
                padding=ft.padding.only(top=15),
            )

        # Observaciones
        if liquidacion["observaciones_liquidacion"]:
            seccion_observaciones = ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Observaciones:", size=13, weight=ft.FontWeight.BOLD),
                        ft.Text(liquidacion["observaciones_liquidacion"], size=12, color="#666"),
                    ],
                    spacing=5,
                ),
                padding=ft.padding.only(top=10),
            )
        else:
            seccion_observaciones = ft.Container()

        # Contenido del modal
        contenido = ft.Container(
            content=ft.Column(
                [
                    info_general,
                    info_predio,  # LEGACY
                    calculos,
                    seccion_contratos,  # NUEVA: Tabla de contratos incluidos
                    seccion_descuentos,
                    seccion_pagos,
                    seccion_observaciones,
                    ft.Divider(),
                    ft.Text("Documentos", size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
                    DocumentManager(
                        entidad_tipo="LIQUIDACION",
                        entidad_id=str(id_liquidacion),
                        page=page,
                        height=250,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
            ),
            width=900,  # Aumentado para acomodar tabla de documentos y botones
            height=550,  # Aumentado de 500 a 550
            padding=10,
        )

    except Exception as e:
        pass  # print(f"Error cargando detalle de liquidación: {e}") [OpSec Removed]
        import traceback

        traceback.print_exc()

        contenido = ft.Container(
            content=ft.Text(f"Error al cargar detalles: {str(e)}", color="red"), padding=20
        )

    def handle_enviar_email(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("⏳ Enviando correo... Esto puede tardar unos segundos.")
        )
        page.snack_bar.open = True
        page.update()

    def handle_enviar_whatsapp(e):
        """Envía la liquidación por WhatsApp al asesor (automático)"""
        pass  # print("[DEBUG WHATSAPP] ========== INICIO handle_enviar_whatsapp ==========") [OpSec Removed]
        pass  # print(f"[DEBUG WHATSAPP] Event: {e}") [OpSec Removed]
        pass  # print(f"[DEBUG WHATSAPP] ID Liquidación: {id_liquidacion}") [OpSec Removed]
        try:
            pass  # print("[DEBUG WHATSAPP] Step 1: Mostrando SnackBar inicial...") [OpSec Removed]
            page.snack_bar = ft.SnackBar(ft.Text("⏳ Obteniendo datos del asesor..."))
            page.snack_bar.open = True
            page.update()
            pass  # print("[DEBUG WHATSAPP] Step 1: SnackBar mostrado OK") [OpSec Removed]

            # 1. Obtener datos del asesor desde la base de datos
            try:
                pass  # print("[DEBUG WHATSAPP] Step 2: Obteniendo asesor...") [OpSec Removed]
                asesor = servicio_liquidacion_asesores.repo_asesor.obtener_por_id(
                    liquidacion["id_asesor"]
                )
                pass  # print(f"[DEBUG WHATSAPP] Asesor obtenido: {asesor}") [OpSec Removed]
                if not asesor:
                    raise Exception("Asesor no encontrado")

                pass  # print("[DEBUG WHATSAPP] Step 3: Obteniendo persona...") [OpSec Removed]
                persona = servicio_liquidacion_asesores.repo_persona.obtener_por_id(
                    asesor.id_persona
                )
                pass  # print(f"[DEBUG WHATSAPP] Persona obtenida: {persona}") [OpSec Removed]
                if not persona:
                    raise Exception("Datos de persona no encontrados")

                telefono = persona.telefono_principal
                nombre_asesor = persona.nombre_completo
                pass  # print(f"[DEBUG WHATSAPP] Teléfono: {telefono}, Nombre: {nombre_asesor}") [OpSec Removed]

            except Exception as ex:
                pass  # print(f"[DEBUG WHATSAPP] ERROR en obtención de datos: {ex}") [OpSec Removed]
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"❌ No se pudo obtener datos del asesor: {str(ex)}"),
                    bgcolor="red",
                    duration=5000,
                )
                page.snack_bar.open = True
                page.update()
                return

            # Función para continuar con el envío (definida ANTES para que esté disponible en el scope)
            def continuar_envio_whatsapp():
                nonlocal nombre_asesor, telefono

                try:
                    # 2. Generar PDF
                    pass  # print("[DEBUG WHATSAPP] Step 4: Generando PDF...") [OpSec Removed]
                    page.snack_bar = ft.SnackBar(ft.Text("⏳ Generando PDF..."))
                    page.snack_bar.open = True
                    page.update()

                    try:
                        ruta_pdf = servicio_liquidacion_asesores.generar_pdf_comprobante(
                            id_liquidacion
                        )
                        pass  # print(f"[DEBUG WHATSAPP] PDF generado: {ruta_pdf}") [OpSec Removed]

                        if not ruta_pdf or not os.path.exists(ruta_pdf):
                            raise Exception("No se pudo generar el comprobante PDF.")
                    except Exception as ex:
                        pass  # print(f"[DEBUG WHATSAPP] ERROR generando PDF: {ex}") [OpSec Removed]
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"❌ Error generando PDF: {str(ex)}"), bgcolor="red"
                        )
                        page.snack_bar.open = True
                        page.update()
                        return

                    # 3. Preparar objeto para servicio de notificaciones
                    pass  # print("[DEBUG WHATSAPP] Step 5: Preparando objeto liquidación...") [OpSec Removed]

                    class LiquidacionObj:
                        def __init__(self, data):
                            self.periodo_liquidacion = data["periodo_liquidacion"]
                            self.valor_neto_asesor = data["valor_neto_asesor"]

                    liquidacion_obj = LiquidacionObj(liquidacion)
                    pass  # print("[DEBUG WHATSAPP] Objeto preparado OK") [OpSec Removed]

                    # 4. Enviar mensaje por WhatsApp automáticamente
                    pass  # print("[DEBUG WHATSAPP] Step 6: Enviando WhatsApp...") [OpSec Removed]
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"⏳ Abriendo WhatsApp para {nombre_asesor}...")
                    )
                    page.snack_bar.open = True
                    page.update()

                    pass  # print(f"[DEBUG WHATSAPP] Enviando WhatsApp automático a: {telefono} ({nombre_asesor})") [OpSec Removed]
                    exito = servicio_notificaciones.notificar_liquidacion_asesor_whatsapp(
                        liquidacion=liquidacion_obj,
                        telefono_asesor=telefono,
                        nombre_asesor=nombre_asesor,
                    )
                    pass  # print(f"[DEBUG WHATSAPP] Resultado envío: {'EXITOSO' if exito else 'FALLIDO'}") [OpSec Removed]

                    if exito:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(
                                f"✅ WhatsApp abierto para {nombre_asesor}. El mensaje se enviará automáticamente."
                            ),
                            bgcolor="green",
                            duration=5000,
                        )
                    else:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(
                                "⚠️ No se pudo abrir WhatsApp. Verifique que WhatsApp Desktop esté instalado."
                            ),
                            bgcolor="orange",
                            duration=5000,
                        )

                    page.snack_bar.open = True
                    page.update()

                except Exception as ex:
                    pass  # print(f"[DEBUG WHATSAPP] ERROR en continuar_envio_whatsapp: {ex}") [OpSec Removed]
                    import traceback

                    traceback.print_exc()
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"❌ Error: {str(ex)}"), bgcolor="red", duration=5000
                    )
                    page.snack_bar.open = True
                    page.update()

            # Si no hay teléfono en BD, pedir manualmente
            if not telefono:
                pass  # print("[DEBUG WHATSAPP] Teléfono no encontrado en BD, solicitando manualmente...") [OpSec Removed]

                def confirmar_envio_whatsapp_manual(ev):
                    nonlocal telefono
                    telefono_input = txt_telefono_manual.value.strip()
                    if not telefono_input or len(telefono_input) < 10:
                        txt_telefono_manual.error_text = (
                            "Ingrese un número válido (mínimo 10 dígitos)"
                        )
                        page.update()
                        return

                    telefono = telefono_input
                    page.close(dlg_telefono_manual)

                    # Continuar con el flujo normal (generar PDF y enviar)
                    continuar_envio_whatsapp()

                txt_telefono_manual = ft.TextField(
                    label="Teléfono del Asesor (con código país)",
                    value="57",
                    autofocus=True,
                    hint_text="573001234567",
                    width=300,
                )

                dlg_telefono_manual = ft.AlertDialog(
                    title=ft.Text(f"Teléfono de {nombre_asesor}"),
                    content=ft.Column(
                        [
                            ft.Text("El asesor no tiene teléfono registrado en la base de datos."),
                            ft.Text("Por favor ingrese el número de WhatsApp:", size=13),
                            txt_telefono_manual,
                            ft.Text(
                                "Nota: Debería actualizar este campo en 'Personas > Editar'",
                                size=11,
                                color="orange",
                            ),
                        ],
                        tight=True,
                        spacing=10,
                    ),
                    actions=[
                        ft.TextButton(
                            "Cancelar", on_click=lambda e: page.close(dlg_telefono_manual)
                        ),
                        ft.TextButton("Continuar", on_click=confirmar_envio_whatsapp_manual),
                    ],
                )
                page.open(dlg_telefono_manual)
                return  # Salir aquí, el flujo continúa en confirmar_envio_whatsapp_manual

            # Si hay teléfono, continuar automáticamente
            else:
                continuar_envio_whatsapp()

        except Exception as ex:
            pass  # print(f"[DEBUG WHATSAPP] ERROR GENERAL: {ex}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error: {str(ex)}"), bgcolor="red", duration=5000
            )
            page.snack_bar.open = True
            page.update()

        pass  # print("[DEBUG WHATSAPP] ========== FIN handle_enviar_whatsapp ==========") [OpSec Removed]

    def handle_descargar_pdf(e):
        try:
            page.snack_bar = ft.SnackBar(ft.Text("⏳ Generando PDF..."))
            page.snack_bar.open = True
            page.update()

            ruta_pdf = servicio_liquidacion_asesores.generar_pdf_comprobante(id_liquidacion)
            page.launch_url(f"file:///{ruta_pdf.replace('\\', '/')}")

            page.snack_bar = ft.SnackBar(ft.Text("✅ PDF generado correctamente"), bgcolor="green")
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            pass  # print(f"Error generando PDF: {ex}") [OpSec Removed]
            page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error generando PDF: {str(ex)}"), bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()

    # Crear dialog
    dialog = ft.AlertDialog(
        title=ft.Text(f"Detalle de Liquidación #{id_liquidacion}"),
        content=contenido,
        actions=[
            ft.TextButton(
                "Descargar PDF",
                icon=ft.Icons.PICTURE_AS_PDF,
                on_click=lambda e: handle_descargar_pdf(e),
            ),
            ft.TextButton("Enviar WhatsApp", icon=ft.Icons.CHAT, on_click=handle_enviar_whatsapp),
            ft.TextButton("Cerrar", on_click=lambda e: on_cerrar()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog
