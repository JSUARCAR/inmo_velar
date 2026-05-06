"""
Auditoria Simple del Módulo de Reportes
======================================
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
            print("=== LOGIN ===")
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

            # IR A REPORTES
            print("\n=== NAVEGAR A REPORTES ===")
            await page.locator('a:has-text("Reportes")').first.click()
            await page.wait_for_load_state("networkidle")
            time.sleep(3)
            print(f"[OK] URL actual: {page.url}")

            # OBTENER TODO EL TEXTO
            print("\n=== CONTENIDO DE LA PAGINA ===")
            body_text = await page.locator("body").inner_text()

            # Guardar
            with open("reporte_audit.txt", "w", encoding="utf-8") as f:
                f.write(body_text)
            print("[OK] Contenido guardado en reporte_audit.txt")

            # Buscar "Recaudos" en el texto
            if "Recaudos" in body_text or "recaudos" in body_text:
                print("\n[ENCONTRADO] 'Recaudos' en la pagina")
                # Encontrar la linea exacta
                lines = body_text.split("\n")
                for i, line in enumerate(lines):
                    if "ecaudos" in line.lower():
                        print(f"  Linea {i}: {line.strip()}")
            else:
                print("\n[NO ENCONTRADO] 'Recaudos' no esta en la pagina")

            # Buscar "OPERACIONES" (categoria)
            if "OPERACIONES" in body_text or "Operaciones" in body_text:
                print("\n[ENCONTRADO] Categoria 'Operaciones'")
            else:
                print("\n[NO ENCONTRADO] Categoria 'Operaciones'")

            # Tomar screenshot
            await page.screenshot(path="reporte_audit.png", full_page=True)
            print("\n[OK] Screenshot guardado")

            time.sleep(5)  # Esperar para ver el navegador

        except Exception as e:
            print(f"[ERROR] {e}")
            await page.screenshot(path="error.png")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
