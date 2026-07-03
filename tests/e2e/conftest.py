import os
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configura el contexto para capturar video y trazas de forma automática."""
    return {
        **browser_context_args,
        "record_video_dir": "test-results/videos/",
    }

@pytest.fixture(scope="session")
def auth_credentials():
    user = os.getenv("PLAYWRIGHT_TEST_USER", "jsuarcar")
    password = os.getenv("PLAYWRIGHT_TEST_PASSWORD", "velarjoan2026")
    return {"user": user, "password": password}

@pytest.fixture
def logged_in_page(page: Page, auth_credentials):
    """Fixture que provee una página autenticada y lista para probar módulos."""
    base_url = "https://extraordinary-joy-production-2fd2.up.railway.app/"
    page.goto(base_url)
    
    # Localizar inputs por el atributo name definido en el frontend
    email_input = page.locator("input[name='username']")
    email_input.fill(auth_credentials["user"])
    
    password_input = page.locator("input[name='password']")
    password_input.fill(auth_credentials["password"])
    
    # Botón de ingreso
    page.get_by_role("button", name="Acceder al Panel").click()
    
    # Esperar validación visual de ingreso exitoso (URL de dashboard o similar)
    page.wait_for_url("**/dashboard**", timeout=10000)
    
    yield page
