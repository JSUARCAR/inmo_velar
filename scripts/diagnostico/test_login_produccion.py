import asyncio
from playwright.async_api import async_playwright, expect
import os

async def test_login():
    async with async_playwright() as p:
        print("Lanzando navegador...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        try:
            url = "https://inmovelar-production.up.railway.app/login"
            print(f"Navegando a {url}...")
            await page.goto(url, wait_until="networkidle")
            
            print("Llenando formulario de login...")
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin0123')
            
            print("Enviando formulario...")
            await page.click('button[type="submit"]')
            
            print("Esperando navegacion...")
            try:
                await page.wait_for_url("**/dashboard", timeout=5000)
                print("¡ÉXITO! Redirección a /dashboard confirmada.")
            except Exception as e:
                print("No se detectó redirección a /dashboard en 5 segundos.")
                
                # Check for error text in the page
                # The error might be a span or div with red text, let's just dump all text content
                print("Extrayendo texto visible de la pagina...")
                body_text = await page.locator("body").inner_text()
                print("==== TEXTO DE LA PÁGINA ====")
                print(body_text)
                print("============================")

        except Exception as e:
            print(f"Ocurrió un error durante la prueba: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())
