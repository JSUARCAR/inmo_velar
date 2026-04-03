"""
Auditoría del Módulo de Reportes - Sistema Velar
================================================
Script para auditar el reporte de Recaudos.
"""

import asyncio
from playwright.async_api import async_playwright, Page, expect
import time

URL_BASE = "https://extraordinary-joy-production-2fd2.up.railway.app/"
USERNAME = "admin"
PASSWORD = "admin0123"


async def main():
    results = {
        "login": {"success": False, "error": None},
        "navigation": {"success": False, "error": None},
        "reportes_page": {"success": False, "error": None},
        "recaudos_report": {"success": False, "error": None, "data_found": []},
        "console_errors": [],
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # Capturar errores de consola
        page.on(
            "console",
            lambda msg: results["console_errors"].append(f"[{msg.type}] {msg.text}")
            if msg.type == "error"
            else None,
        )

        try:
            # 1. LOGIN
            print("\n=== FASE 1: LOGIN ===")
            await page.goto(URL_BASE, timeout=60000)
            await page.wait_for_load_state("networkidle")
            time.sleep(2)

            # Buscar campo de usuario
            username_field = page.locator(
                'input[type="text"], input[name="username"], input[placeholder*="usuario" i]'
            ).first
            await username_field.fill(USERNAME)

            # Buscar campo de contraseña
            password_field = page.locator('input[type="password"]').first
            await password_field.fill(PASSWORD)

            # Click en botón de login
            login_button = page.locator(
                'button[type="submit"], button:has-text("Iniciar"), button:has-text("Login"), button:has-text("Entrar")'
            ).first
            await login_button.click()

            await page.wait_for_load_state("networkidle")
            time.sleep(3)

            results["login"]["success"] = True
            print("[OK] Login exitoso")

            # 2. NAVEGAR A REPORTES
            print("\n=== FASE 2: NAVEGAR A REPORTES ===")

            # Buscar enlace a reportes
            reportes_link = page.locator(
                'a:has-text("Reportes"), a:has-text("reportes"), [href*="reporte"]'
            ).first
            await reportes_link.click()
            await page.wait_for_load_state("networkidle")
            time.sleep(2)

            results["navigation"]["success"] = True
            print("[OK] Navegacion a Reportes exitosa")

            # 3. ACCEDER AL REPORTE DE RECAUDOS
            print("\n=== FASE 3: REPORTE DE RECAUDOS ===")

            # Buscar el reporte de Recaudos
            try:
                reclutados_option = page.locator(
                    'text="Reporte de Recaudos", text="Recaudos"'
                ).first
                await reclutados_option.click()
                await page.wait_for_load_state("networkidle")
                time.sleep(3)
                print("[OK] Clic en Reporte de Recaudos")
            except Exception as e:
                print(f"[ERROR] Error clicking Recaudos: {e}")
                # Tomar screenshot
                await page.screenshot(path="auditoria_recaudos_step3.png")

            # 4. ANALIZAR DATOS
            print("\n=== FASE 4: ANALISIS DE DATOS ===")

            # Esperar tabla de datos
            await page.wait_for_timeout(3000)

            # Buscar tabla de datos
            tables = await page.locator("table").all()
            print(f"Tablas encontradas: {len(tables)}")

            # Buscar headers
            headers = await page.locator("th, thead td").all_text_contents()
            print(f"Headers de tabla: {headers}")

            # Buscar filas de datos
            rows = await page.locator("tbody tr, table tbody tr").all()
            print(f"Filas de datos: {len(rows)}")

            # Capturar datos de cada fila
            for i, row in enumerate(rows[:10]):  # Max 10 filas
                cells = await row.locator("td").all_text_contents()
                results["recaudos_report"]["data_found"].append(cells)
                print(f"  Fila {i + 1}: {cells}")

            # 5. VERIFICAR FILTROS
            print("\n=== FASE 5: VERIFICAR FILTROS ===")

            # Buscar selectores de filtro
            selects = await page.locator("select").all()
            print(f"Selectores de filtro encontrados: {len(selects)}")

            for sel in selects:
                label = (
                    await sel.get_attribute("name")
                    or await sel.get_attribute("id")
                    or "unnamed"
                )
                options_count = await sel.locator("option").count()
                print(f"  Filtro: {label} ({options_count} opciones)")

            # 6. TOMAR SCREENSHOT
            await page.screenshot(path="auditoria_recaudos.png", full_page=True)
            print("\n[OK] Screenshot guardado: auditoria_recaudos.png")

            results["recaudos_report"]["success"] = True

        except Exception as e:
            results["recaudos_report"]["error"] = str(e)
            print(f"\n[ERROR] Error: {e}")
            await page.screenshot(path="auditoria_error.png")

        finally:
            await browser.close()

    # RESUMEN
    print("\n" + "=" * 60)
    print("RESUMEN DE AUDITORIA")
    print("=" * 60)
    print(f"Login: {'[OK]' if results['login']['success'] else '[FAIL]'}")
    print(f"Navegacion: {'[OK]' if results['navigation']['success'] else '[FAIL]'}")
    print(
        f"Reporte Recaudos: {'[OK]' if results['recaudos_report']['success'] else '[FAIL]'}"
    )
    print(f"Datos encontrados: {len(results['recaudos_report']['data_found'])}")
    print(f"Errores de consola: {len(results['console_errors'])}")

    if results["console_errors"]:
        print("\nERRORES DE CONSOLA:")
        for err in results["console_errors"][:5]:
            print(f"  - {err}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
