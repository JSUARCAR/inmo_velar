"""
Auditoria Detallada del Módulo de Reportes
==========================================
Exploracion profunda de la interfaz.
"""

import asyncio
from playwright.async_api import async_playwright
import time
import json

URL_BASE = "https://extraordinary-joy-production-2fd2.up.railway.app/"
USERNAME = "admin"
PASSWORD = "admin0123"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Headless para ver
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        errors = []
        page.on(
            "console",
            lambda msg: errors.append(msg.text) if msg.type == "error" else None,
        )

        try:
            # 1. LOGIN
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

            # 2. IR A REPORTES
            print("\n=== NAVEGAR A REPORTES ===")

            # Buscar todos los enlaces
            all_links = await page.locator("a").all()
            print(f"Total de enlaces: {len(all_links)}")

            for link in all_links:
                href = await link.get_attribute("href")
                text = await link.text_content()
                if text and ("reporte" in text.lower() or "report" in text.lower()):
                    print(f"  Link reporte: '{text}' -> {href}")

            # Intentar hacer clic en el menu de reportes
            reportes_nav = page.locator(
                'a[href*="reporte"], a:has-text("Reporte"), nav :has-text("Reporte")'
            )

            # Tomar HTML del sidebar
            sidebar = page.locator(
                'aside, nav, [class*="sidebar"], [class*="menu"]'
            ).first
            sidebar_html = (
                await sidebar.inner_html()
                if await sidebar.count() > 0
                else "No sidebar"
            )

            # Guardar para analisis
            with open("sidebar_content.html", "w", encoding="utf-8") as f:
                f.write(sidebar_html)
            print("[OK] Sidebar guardado en sidebar_content.html")

            # Navegar directamente si hay URL
            current_url = page.url
            if "reporte" not in current_url.lower():
                # Probar URLs comunes
                urls_to_try = [
                    f"{URL_BASE}/reportes",
                    f"{URL_BASE}/reportes/",
                    f"{URL_BASE}/reporte",
                ]
                for url in urls_to_try:
                    try:
                        await page.goto(url, timeout=10000)
                        await page.wait_for_load_state("networkidle")
                        time.sleep(2)
                        if "reporte" in page.url.lower():
                            print(f"[OK] Navegado a: {url}")
                            break
                    except:
                        pass

            # 3. ANALIZAR PAGINA DE REPORTES
            print("\n=== ANALIZAR PAGINA DE REPORTES ===")

            # Buscar todos los elementos clickeables
            clickables = await page.locator(
                'button, [role="button"], [onclick], a'
            ).all()
            print(f"Elementos clickeables: {len(clickables)}")

            # Lista de reportes
            report_items = page.locator(
                '[class*="report"], [class*="card"]:has-text("Reporte"), [class*="item"]:has-text("Reporte")'
            )
            report_count = await report_items.count()
            print(f"Items de reporte encontrados: {report_count}")

            # Extraer texto de todos los elementos de la sidebar
            sidebar_items = page.locator(
                "aside li, aside button, aside a, nav li, nav a"
            ).all()
            print(f"\nItems en sidebar/nav: {len(sidebar_items)}")
            for item in sidebar_items[:30]:
                text = await item.text_content()
                if text and text.strip():
                    print(f"  - {text.strip()[:50]}")

            # 4. TOMAR SCREENSHOT COMPLETO
            await page.screenshot(path="auditoria_full.png", full_page=True)
            print("\n[OK] Screenshot guardado")

            # 5. VOLCAR HTML DE LA PAGINA
            html = await page.content()
            with open("page_content.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("[OK] HTML guardado en page_content.html")

        except Exception as e:
            print(f"[ERROR] {e}")
            await page.screenshot(path="error_screenshot.png")
        finally:
            await browser.close()

        # Errores
        if errors:
            print(f"\n=== ERRORES DE CONSOLA ({len(errors)}) ===")
            for err in errors[:10]:
                print(f"  {err[:200]}")


if __name__ == "__main__":
    asyncio.run(main())
