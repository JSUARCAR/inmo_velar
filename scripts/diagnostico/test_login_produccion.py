import asyncio
from playwright.async_api import async_playwright
import os

async def test_login():
    async with async_playwright() as p:
        print("Lanzando navegador (Visible para el usuario)...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        try:
            url = "https://inmovelar-production.up.railway.app/login"
            print(f"Navegando a {url}...")
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(1000) # Pausa para que el usuario pueda ver
            
            print("Llenando formulario de login...")
            await page.fill('input[name="username"]', 'admin')
            await page.wait_for_timeout(500)
            
            await page.fill('input[name="password"]', 'admin0123')
            await page.wait_for_timeout(1000)
            
            print("Enviando formulario...")
            await page.click('button[type="submit"]')
            
            print("Esperando navegacion...")
            try:
                await page.wait_for_url("**/dashboard", timeout=5000)
                print("¡ÉXITO! Redirección a /dashboard confirmada.")
                await page.wait_for_timeout(2000)
            except Exception as e:
                print("No se detectó redirección a /dashboard en 5 segundos.")
                await page.wait_for_timeout(3000) # Dar tiempo al usuario de ver que falló silenciosamente

        except Exception as e:
            print(f"Ocurrió un error durante la prueba: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())
