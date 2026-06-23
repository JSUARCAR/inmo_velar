"""
Test E2E para validar Row 4 del Dashboard - Composición Portafolio, Incidentes y Top Asesores.
Según el blueprint layout_blueprint.svg, estos 3 componentes deben estar presentes.
"""

import pytest
from playwright.sync_api import sync_playwright
import time
from tests.utils_network import SERVER_RUNNING

pytestmark = pytest.mark.skipif(
    not SERVER_RUNNING,
    reason="El servidor local en localhost:8000 no esta activo. E2E/Playwright tests ignorados.",
)


def test_dashboard_row4_components():
    """
    Valida que los 3 componentes del Row 4 (Composición, Incidentes, Top Asesores)
    están presentes y visibles en el dashboard después de la implementación.
    """
    print("Iniciando test E2E para Row 4 del Dashboard...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. Navegar al login directamente
            print("Navegando a http://localhost:3000/login...")
            page.goto("http://localhost:3000/login", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            time.sleep(3)

            # Verificar que la página carga - capturar HTML si falla
            print("Verificando contenido de la pagina...")
            title = page.title()
            url = page.url
            print(f"  URL actual: {url}")
            print(f"  Titulo: {title}")

            # 2. Login con credenciales - buscar input de diferentes formas
            print("Realizando login con admin/admin0123...")

            # Intentar varios localizadores
            username_input = page.locator("input[name='username']").first
            if not username_input.is_visible(timeout=5000):
                # Intentar otro localizador
                username_input = page.locator("input[type='text']").first
            if not username_input.is_visible(timeout=5000):
                # Ver el HTML para entender la estructura
                print("  Buscando estructura del formulario...")
                inputs = page.locator("input").all()
                print(f"  Encontrados {len(inputs)} inputs en la pagina")
                for i, inp in enumerate(inputs):
                    try:
                        print(
                            f"    Input {i}: name={inp.get_attribute('name')}, type={inp.get_attribute('type')}, placeholder={inp.get_attribute('placeholder')}"
                        )
                    except Exception:
                        pass

            username_input.wait_for(state="visible", timeout=20000)
            username_input.fill("admin")

            password_input = page.locator("input[type='password']").first
            password_input.wait_for(state="visible", timeout=10000)
            password_input.fill("admin0123")

            login_button = page.locator(
                "button:has-text('Ingresar'), button[type='submit']"
            ).first
            login_button.click()

            # Esperar que cargue el dashboard
            page.wait_for_url("**/dashboard**", timeout=20000)
            time.sleep(3)  # Esperar a que los graficos carguen
            print("Login completado, dashboard cargado.")

            # 3. Validar Row 4 - Composición Portafolio
            print("\n--- Verificando Row 4: Composición Portafolio ---")
            composicion_heading = page.get_by_text("COMPOSICIÓN PORTAFOLIO")
            composicion_visible = composicion_heading.is_visible()
            print(f"  COMPOSICIÓN PORTAFOLIO visible: {composicion_visible}")

            # Buscar el gráfico de barras (puede tener nombre de clase relacionado con chart)
            composicion_chart = (
                page.locator("div")
                .filter(has_text="COMPOSICIÓN PORTAFOLIO")
                .locator("..")
                .locator("svg")
                .first
            )
            composicion_chart_visible = (
                composicion_chart.is_visible() if composicion_visible else False
            )
            print(f"  Gráfico de Composición visible: {composicion_chart_visible}")

            # 4. Validar Row 4 - Incidentes Distribución
            print("\n--- Verificando Row 4: Incidentes Distribución ---")
            incidentes_heading = page.get_by_text("INCIDENTES DISTRIBUCIÓN")
            incidentes_visible = incidentes_heading.is_visible()
            print(f"  INCIDENTES DISTRIBUCIÓN visible: {incidentes_visible}")

            incidentes_chart = (
                page.locator("div")
                .filter(has_text="INCIDENTES DISTRIBUCIÓN")
                .locator("..")
                .locator("svg")
                .first
            )
            incidentes_chart_visible = (
                incidentes_chart.is_visible() if incidentes_visible else False
            )
            print(f"  Gráfico de Incidentes visible: {incidentes_chart_visible}")

            # 5. Validar Row 4 - Top Asesores Revenue
            print("\n--- Verificando Row 4: Top Asesores Revenue ---")
            top_asesores_heading = page.get_by_text("TOP ASESORES REVENUE")
            top_asesores_visible = top_asesores_heading.is_visible()
            print(f"  TOP ASESORES REVENUE visible: {top_asesores_visible}")

            top_asesores_chart = (
                page.locator("div")
                .filter(has_text="TOP ASESORES REVENUE")
                .locator("..")
                .locator("svg")
                .first
            )
            top_asesores_chart_visible = (
                top_asesores_chart.is_visible() if top_asesores_visible else False
            )
            print(f"  Gráfico de Top Asesores visible: {top_asesores_chart_visible}")

            # 6. Validar que los otros rows también funcionan
            print("\n--- Verificando Rows existentes ---")

            # Row 1: KPIs
            kpis = ["Ocupación Financiera", "Eficiencia Recaudo", "Potencial Total"]
            for kpi in kpis:
                kpi_visible = page.get_by_text(kpi).first.is_visible()
                print(f"  KPI {kpi}: {kpi_visible}")

            # Row 2: Evolución + Túnel
            evolucion_visible = page.get_by_text(
                "EVOLUCIÓN DE RECAUDO"
            ).first.is_visible()
            tunel_visible = page.get_by_text("RIESGO DE VENCIMIENTO").first.is_visible()
            print(f"  Evolución de Recau  do visible: {evolucion_visible}")
            print(f"  Túnel de Vencimientos visible: {tunel_visible}")

            # Row 3: Pulso Operativo
            pulso_visible = page.get_by_text(
                "PULSO OPERATIVO Y ACCIONES"
            ).first.is_visible()
            print(f"  Pulso Operativo visible: {pulso_visible}")

            # Row 5: Vencimientos
            vencimiento_mandato_visible = page.get_by_text(
                "Vencimientos de Mandato"
            ).first.is_visible()
            vencimiento_arrenda_visible = page.get_by_text(
                "Vencimientos de Arrendamiento"
            ).first.is_visible()
            print(f"  Vencimientos Mandato visible: {vencimiento_mandato_visible}")
            print(
                f"  Vencimientos Arrendamiento visible: {vencimiento_arrenda_visible}"
            )

            # 7. Capturar screenshot para evidencia
            print("\n--- Capturando screenshot ---")
            page.screenshot(path="dashboard_row4_verified.png")
            print("Screenshot guardado en dashboard_row4_verified.png")

            # 8. Resultado final
            print("\n" + "=" * 60)
            print("RESULTADO DE LA VERIFICACIÓN")
            print("=" * 60)

            all_row4_present = (
                composicion_visible and incidentes_visible and top_asesores_visible
            )
            all_row4_with_charts = (
                composicion_chart_visible
                and incidentes_chart_visible
                and top_asesores_chart_visible
            )

            if all_row4_present and all_row4_with_charts:
                print("PASS: Row 4 completamente implementado")
                print("   - Composicion Portafolio: OK")
                print("   - Incidentes Distribucion: OK")
                print("   - Top Asesores Revenue: OK")
            elif all_row4_present:
                print("PARTIAL: Encabezados presentes pero graficos no detectados")
                print("   - Composicion Portafolio: OK (encabezado)")
                print("   - Incidentes Distribucion: OK (encabezado)")
                print("   - Top Asesores Revenue: OK (encabezado)")
            else:
                print("FAIL: Row 4 no implementado correctamente")
                print(
                    f"   - Composicion Portafolio: {'OK' if composicion_visible else 'FALTA'}"
                )
                print(
                    f"   - Incidentes Distribucion: {'OK' if incidentes_visible else 'FALTA'}"
                )
                print(
                    f"   - Top Asesores Revenue: {'OK' if top_asesores_visible else 'FALTA'}"
                )

            print("=" * 60)

            # Aserciones para test automatizado
            assert (
                composicion_visible
            ), "Componente COMPOSICION PORTAFOLIO no encontrado"
            assert (
                incidentes_visible
            ), "Componente INCIDENTES DISTRIBUCION no encontrado"
            assert top_asesores_visible, "Componente TOP ASESORES REVENUE no encontrado"

            print("\nTest Passed: Todos los componentes de Row 4 estan presentes")

        except Exception as e:
            print(f"\nERROR durante la ejecucion: {e}")
            page.screenshot(path="dashboard_error.png")
            print("Screenshot del error guardado en dashboard_error.png")
            raise

        finally:
            browser.close()


if __name__ == "__main__":
    test_dashboard_row4_components()
