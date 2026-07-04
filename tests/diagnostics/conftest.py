import os
import pytest
from playwright.sync_api import sync_playwright, Page, BrowserContext

# URL base de producción
PROD_URL = "https://extraordinary-joy-production-2fd2.up.railway.app"

@pytest.fixture(scope="session")
def prod_credentials():
    """Retorna las credenciales desde variables de entorno."""
    user = os.environ.get("PLAYWRIGHT_PROD_USER")
    password = os.environ.get("PLAYWRIGHT_PROD_PASS")
    
    if not user or not password:
        pytest.skip("Las variables PLAYWRIGHT_PROD_USER y PLAYWRIGHT_PROD_PASS deben estar configuradas.")
        
    return {"username": user, "password": password}

@pytest.fixture(scope="function")
def context_with_interception(browser):
    """Crea un contexto con listeners para red y consola."""
    context = browser.new_context()
    
    # Listas para almacenar eventos capturados y poder inspeccionarlos si es necesario
    console_messages = []
    failed_responses = []
    
    # No podemos agregar el listener de 'response' a 'context' directamente en todas las versiones de Playwright,
    # pero podemos inyectarlo en cada nueva página creada en el contexto.
    
    yield context
    context.close()

@pytest.fixture(scope="function")
def diag_page(context_with_interception, prod_credentials):
    """
    Retorna una página autenticada y configurada con interceptores de consola y red.
    """
    page = context_with_interception.new_page()
    
    # 1. Configurar interceptores de consola
    def handle_console(msg):
        # Ignoramos warnings benignos si es necesario, pero logueamos todo en modo diagnostico
        print(f"\n[DIAG CONSOLE] {msg.type}: {msg.text}")
        
    page.on("console", handle_console)
    
    # 2. Configurar interceptores de red para errores (4xx, 5xx)
    def handle_response(response):
        if response.status >= 400:
            print(f"\n[DIAG NETWORK ERROR] {response.status} {response.request.method} {response.url}")
            
    page.on("response", handle_response)
    
    # Autenticación inicial
    print(f"\n[DIAG] Iniciando autenticación en {PROD_URL}")
    page.goto(PROD_URL)
    
    # Rellenar credenciales usando selectores nativos de Reflex
    page.locator("input[name='username']").fill(prod_credentials["username"])
    page.locator("input[name='password']").fill(prod_credentials["password"])
    page.get_by_role("button", name="Acceder al Panel").click()
    
    # Esperar a que estemos en el dashboard
    page.wait_for_url("**/dashboard**", timeout=10000)
    print("\n[DIAG] Autenticación exitosa. Entorno listo.")
    
    return page
