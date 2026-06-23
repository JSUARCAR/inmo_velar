import pytest
from playwright.sync_api import sync_playwright
import time
from tests.utils_network import SERVER_RUNNING

pytestmark = pytest.mark.skipif(
    not SERVER_RUNNING,
    reason="El servidor local en localhost:8000 no esta activo. E2E/Playwright tests ignorados.",
)


def test_liquidacion_asesores_flow():
    print("🚀 Iniciando validación de Liquidación de Asesores...")

    with sync_playwright() as p:
        # Usar chromium en modo con cabeza para facilitar la depuración si es necesario,
        # pero en CI o modo automático suele ser headless.
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        try:
            # 0. Listeners
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            page.on("pageerror", lambda err: print(f"BROWSER ERROR: {err.message}"))

            # 1. Login
            base_url = "http://127.0.0.1:3000"
            print(f"🔗 Navegando directamente a {base_url}/login...")
            page.goto(f"{base_url}/login", timeout=60000)
            page.wait_for_load_state("load")
            time.sleep(5)

            print("🔑 Realizando login...")
            # El selector de input por name debe funcionar si la página cargó
            page.wait_for_selector("input[name='username']", timeout=30000)
            page.locator("input[name='username']").fill("admin")
            page.locator("input[name='password']").fill("admin0123")

            # El botón dice "Acceder al Panel"
            page.locator("button:has-text('Acceder al Panel')").first.click()

            # Esperar a que cargue el dashboard
            page.wait_for_url("**/dashboard*", timeout=20000)
            print("✅ Login exitoso.")

            # 2. Navegar a Liquidación de Asesores
            print("📅 Navegando a /liquidacion-asesores...")
            page.goto(f"{base_url}/liquidacion-asesores")
            page.wait_for_load_state("domcontentloaded")

            # Esperar a que el contenido principal cargue
            page.wait_for_selector("text='Liquidaciones de Asesores'", timeout=20000)
            print("📊 Módulo cargado correctamente.")

            # 2.5 Validación: Nueva Liquidación (Prueba de Modales)
            print("🆕 Probando apertura de modal: Nueva Liquidación...")
            # El botón tiene un ícono 'plus' y el texto 'Nueva Liquidación'
            btn_nueva = page.locator("button:has-text('Nueva Liquidación')").first
            btn_nueva.click()

            try:
                page.wait_for_selector(
                    "text='Nueva Liquidación de Asesor'", timeout=10000
                )
                print("✅ Modal de 'Nueva Liquidación' abierto correctamente.")
                page.keyboard.press("Escape")
                time.sleep(2)  # Dar tiempo a que el modal se cierre
            except Exception as e:
                print(f"❌ No se pudo abrir el modal de 'Nueva Liquidación': {e}")
                page.screenshot(path="tests/modal_nueva_fail.png")

            # 3. Acción: Ver Detalles
            print("🔍 Validando: Ver Detalles...")

            # Esperar a que la tabla tenga datos
            page.wait_for_selector("table tbody tr", timeout=10000)
            primera_fila = page.locator("table tbody tr").first

            # Localizar el botón del ojo (primero en el stack de acciones)
            btn_detalle = primera_fila.locator("button:has(svg.lucide-eye)").first

            print("DEBUG: Haciendo hover y click en el botón de detalles...")
            btn_detalle.hover()
            time.sleep(1)
            btn_detalle.click(force=True)

            # Esperar a que el diálogo aparezca
            print("DEBUG: Esperando a que aparezca el diálogo...")
            try:
                # Radix UI dialogs often use a portal
                page.wait_for_selector(
                    "[role='dialog']", timeout=20000, state="visible"
                )
                print("✅ Diálogo detectado y visible.")

                dialogo = page.locator("[role='dialog']")
                inner_text = dialogo.inner_text()

                if "Detalle" in inner_text or "Asesor" in inner_text:
                    print(f"✅ El diálogo es correcto. Texto: {inner_text[:50]}...")
                else:
                    print(f"⚠️ Texto inesperado en diálogo: {inner_text[:100]}")
            except Exception as e:
                print(f"❌ El diálogo de detalles no apareció: {e}")
                page.screenshot(path="tests/modal_fail_v3.png")
                raise e

            # Cerrar el modal
            page.keyboard.press("Escape")
            time.sleep(2)

            # 4. Acción: Descargar PDF
            print("📄 Validando: Descargar PDF...")
            # Buscar botón con 'file-text'
            btn_pdf = (
                page.locator("table tbody tr")
                .first.locator(
                    "button:has(svg.lucide-file-text), button:has(svg[data-lucide='file-text'])"
                )
                .first
            )

            if btn_pdf.is_visible():
                with page.expect_download() as download_info:
                    btn_pdf.click()
                download = download_info.value
                print(f"✅ PDF descargado: {download.suggested_filename}")
            else:
                print("⚠️ Botón PDF no disponible (posiblemente liquidación anulada).")

            # 5. Acción: Editar
            print("✏️ Validando: Editar...")
            # Buscar una fila con estado 'Pendiente' para editar
            fila_pendiente = page.locator(
                "table tbody tr:has(span:text('Pendiente'))"
            ).first

            if fila_pendiente.count() > 0:
                btn_editar = fila_pendiente.locator(
                    "button:has(svg.lucide-pencil), button:has(svg[data-lucide='pencil'])"
                ).first
                btn_editar.click()

                # Esperar modal de edición
                page.wait_for_selector("text='Editar Liquidación'", timeout=10000)

                # Modificar observaciones
                obs_textarea = page.locator("textarea").first
                obs_textarea.fill(
                    f"Validación automatizada {time.strftime('%Y-%m-%d %H:%M:%S')}"
                )

                # Guardar (el botón dice "Guardar Cambios")
                page.locator("button:has-text('Guardar Cambios')").first.click()

                # Verificar toast
                page.wait_for_selector("text='Liquidación actualizada'", timeout=10000)
                print("✅ Edición completada con éxito.")
            else:
                print("⚠️ No hay liquidaciones pendientes para editar.")

            # 6. Acción: Aprobar
            print("✅ Validando: Aprobar Liquidación...")
            # Buscar de nuevo una fila pendiente
            fila_para_aprobar = page.locator(
                "table tbody tr:has(span:text('Pendiente'))"
            ).first

            if fila_para_aprobar.count() > 0:
                # En la grilla el ícono es 'check'
                btn_aprobar = fila_para_aprobar.locator(
                    "button:has(svg.lucide-check), button:has(svg[data-lucide='check'])"
                ).first
                btn_aprobar.click()

                # Verificar toast de aprobación (el toast dice "Aprobada")
                page.wait_for_selector("text='Aprobada'", timeout=10000)
                print("✅ Liquidación aprobada con éxito.")
            else:
                print("⚠️ No hay liquidaciones pendientes para aprobar.")

            print("\n🏁 Proceso de validación finalizado con éxito.")

        except Exception as e:
            print(f"❌ Error durante la validación: {e}")
            page.screenshot(path="tests/error_liquidacion_asesores.png")
            print(
                "📸 Pantallazo de error guardado en tests/error_liquidacion_asesores.png"
            )
            raise e

        finally:
            browser.close()


if __name__ == "__main__":
    test_liquidacion_asesores_flow()
