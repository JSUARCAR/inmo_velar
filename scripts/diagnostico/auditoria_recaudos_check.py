"""
Auditoria Completa - Verificar datos y UI del Reporte de Recaudos
================================================================
"""

import asyncio
from playwright.async_api import async_playwright
import time

URL_BASE = "https://extraordinary-joy-production-2fd2.up.railway.app/"
USERNAME = "admin"
PASSWORD = "admin0123"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            # LOGIN
            print("=== FASE 1: LOGIN ===")
            await page.goto(URL_BASE, timeout=60000)
            await page.wait_for_load_state("networkidle")
            time.sleep(2)

            await page.locator('input[type="text"], input[name="username"]').first.fill(
                USERNAME
            )
            await page.locator('input[type="password"]').first.fill(PASSWORD)
            await page.locator('button[type="submit"]').first.click()
            await page.wait_for_load_state("networkidle")
            time.sleep(3)
            print("[OK] Login")

            # IR A RECAUDOS DIRECTAMENTE
            print("\n=== FASE 2: NAVEGAR A RECAUDOS ===")
            await page.locator('a:has-text("Recaudos")').first.click()
            await page.wait_for_load_state("networkidle")
            time.sleep(3)
            print(f"[OK] URL actual: {page.url}")

            # Esperar que carguen los datos
            print("\n=== FASE 3: ESPERAR DATOS ===")
            await page.wait_for_timeout(5000)

            # Tomar screenshot
            await page.screenshot(path="recaudos_view.png", full_page=True)
            print("[OK] Screenshot guardado: recaudos_view.png")

            # Obtener texto de la pagina
            body_text = await page.locator("body").inner_text()
            with open("recaudos_body.txt", "w", encoding="utf-8") as f:
                f.write(body_text)
            print("[OK] Texto guardado")

            # Verificar si hay datos
            if "0 registros" in body_text or "Total: 0" in body_text:
                print("\n[ALERTA] No hay datos en el reporte (0 registros)")
            else:
                print("\n[INFO] Hay datos en el reporte")
                # Contar filas
                rows = await page.locator("tbody tr").all()
                print(f"Filas en tabla: {len(rows)}")

            # Hacer clic en el modulo de Reportes
            print("\n=== FASE 4: IR A REPORTES ===")
            await page.locator('a:has-text("Reportes")').first.click()
            await page.wait_for_load_state("networkidle")
            time.sleep(3)

            # Buscar y hacer clic en "Reporte de Recaudos"
            print("\n=== FASE 5: SELECCIONAR REPORTE DE RECAUDOS ===")

            # Buscar todos los elementos que contengan "Recaudos"
            recaudos_elements = page.locator('text="Reporte de Recaudos"')
            count = await recaudos_elements.count()
            print(f"Elementos 'Reporte de Recaudos' encontrados: {count}")

            if count > 0:
                await page.locator('text="Reporte de Recaudos"').first.click()
                await page.wait_for_load_state("networkidle")
                time.sleep(5)
                print("[OK] Clic en Reporte de Recaudos")
            else:
                # Buscar de otra forma
                print("Buscando 'Recaudos'...")
                all_text = await page.locator("body").inner_text()
                if "Recaudos" in all_text:
                    print("[INFO] 'Recaudos' encontrado en la pagina")
                    # Intentar clic en el elemento mas cercano
                    try:
                        await page.locator('div:has-text("Recaudos")').first.click()
                        time.sleep(3)
                    except:
                        pass

            # Esperar datos del reporte
            await page.wait_for_timeout(5000)

            # Capturar resultado
            await page.screenshot(path="reporte_recaudos_view.png", full_page=True)

            final_text = await page.locator("body").inner_text()
            with open("reporte_final.txt", "w", encoding="utf-8") as f:
                f.write(final_text)

            print("\n[INFO] Contenido final de la pagina:")
            print(final_text[:2000])

            # Guardar HTML
            html = await page.content()
            with open("reporte_html.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("\n[OK] HTML guardado")

            time.sleep(5)

        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback

            traceback.print_exc()
            await page.screenshot(path="error.png")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
