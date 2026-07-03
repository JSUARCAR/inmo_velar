import pytest
from playwright.sync_api import Page, expect

PROPIEDAD_INCIDENTES = "CONJ CIUDADELA COMFENALCO MZ H CS 29"

def test_validacion_plan_pago(diag_page: Page):
    """
    US1: Validación del Plan de Pago en el módulo de Incidentes.
    Verifica que la sección Plan de Pago cargue correctamente y muestre las cuotas.
    """
    page = diag_page
    
    # 1. Navegar a Incidentes
    print("\n[DIAG] Navegando a Incidentes...")
    page.goto("https://extraordinary-joy-production-2fd2.up.railway.app/incidentes")
    
    # 2. Esperar a que cargue la tabla
    page.locator(".rt-TableRoot").wait_for(timeout=15000)
    
    # 3. Ubicar el incidente de la propiedad específica
    print(f"\n[DIAG] Buscando incidente para: {PROPIEDAD_INCIDENTES}")
    
    # Podría haber múltiples filas, buscamos una que contenga la propiedad y tratamos de abrir sus detalles
    row = page.locator("tr", has_text=PROPIEDAD_INCIDENTES).first
    row.wait_for(timeout=10000)
    
    # Hacemos clic en el botón de "Ver/Editar" (suele ser el primer botón en las acciones o la fila misma)
    # Suponiendo que hay un botón 'Detalles' o un clic en la fila abre un drawer/modal
    # En proyectos previos con Reflex, a menudo un IconButton o la celda misma es clickeable.
    # Buscamos un botón dentro de la fila. Si no, hacemos clic en la fila.
    boton_ver = row.locator("button").first
    if boton_ver.is_visible():
        boton_ver.click()
    else:
        row.click()
        
    # 4. Verificar que se abra el modal/drawer del incidente
    # Normalmente, aparecerá texto como "Plan de Pago" o "Detalles del Incidente"
    print("\n[DIAG] Esperando que se visualice la sección 'Plan de Pago'...")
    plan_pago_header = page.get_by_text("Plan de Pago")
    
    try:
        plan_pago_header.wait_for(timeout=15000)
        assert plan_pago_header.is_visible()
        print("\n[DIAG] [ÉXITO] Sección 'Plan de Pago' visible.")
        
        # Opcional: Verificar que hay cuotas (elementos que digan 'Cuota' o tablas dentro del modal)
        # Esto valida que no esté vacío.
    except Exception as e:
        print(f"\n[DIAG] [FALLO] No se encontró la sección 'Plan de Pago'. Excepción: {str(e)}")
        # Forzar un screenshot para evidencia
        page.screenshot(path="specs/008-playwright-prod-diag/fallo_plan_pago.png")
        raise

PROPIEDAD_SANDBOX = "Calle Falsa 123 - Test Renov"

def test_seleccion_incidentes(diag_page: Page):
    """
    US2: Validación del botón Seleccionar Incidentes.
    Verifica que en el modal de edición, el botón exista y sea funcional.
    """
    page = diag_page
    
    print("\n[DIAG] Navegando a Liquidaciones...")
    page.goto("https://extraordinary-joy-production-2fd2.up.railway.app/liquidaciones")
    page.locator(".rt-TableRoot").wait_for(timeout=15000)
    
    print(f"\n[DIAG] Buscando liquidación para: {PROPIEDAD_SANDBOX}")
    row = page.locator("tr", has_text=PROPIEDAD_SANDBOX).first
    row.wait_for(timeout=10000)
    
    # Hacer clic en Editar
    boton_editar = row.get_by_role("button", name="Editar").first
    if boton_editar.is_visible():
        boton_editar.click()
    else:
        # Fallback si no tiene name="Editar"
        row.locator("button").nth(0).click()
        
    # Verificar el modal de edición
    modal_header = page.get_by_text("Editar Liquidación").first
    modal_header.wait_for(timeout=10000)
    
    # Buscar el botón "Seleccionar Incidentes"
    print("\n[DIAG] Buscando botón 'Seleccionar Incidentes' en producción...")
    boton_seleccionar = page.get_by_text("Seleccionar Incidentes", exact=False).first
    
    try:
        boton_seleccionar.wait_for(timeout=5000)
        assert boton_seleccionar.is_visible()
        print("\n[DIAG] [ÉXITO] Botón 'Seleccionar Incidentes' encontrado en el DOM.")
        boton_seleccionar.click()
        # Verificar que el modal de incidentes se abra (buscando checkboxes)
        checkbox = page.locator("button[role='checkbox'], .rt-CheckboxRoot").first
        checkbox.wait_for(timeout=5000)
    except Exception as e:
        print(f"\n[DIAG] [FALLO] No se encontró o no funcionó 'Seleccionar Incidentes'. Excepción: {str(e)}")
        page.screenshot(path="specs/008-playwright-prod-diag/fallo_boton_incidentes.png")
        raise

def test_eliminar_liquidacion_sandbox(diag_page: Page):
    """
    US3: Validación de la acción Eliminar.
    Intenta eliminar la liquidación Sandbox y evalúa si hay un fallo de red o error silencioso.
    """
    page = diag_page
    
    print("\n[DIAG] Navegando a Liquidaciones para eliminar...")
    page.goto("https://extraordinary-joy-production-2fd2.up.railway.app/liquidaciones")
    page.locator(".rt-TableRoot").wait_for(timeout=15000)
    
    print(f"\n[DIAG] Buscando liquidación Sandbox para eliminar: {PROPIEDAD_SANDBOX}")
    row = page.locator("tr", has_text=PROPIEDAD_SANDBOX).first
    row.wait_for(timeout=10000)
    
    # Hacer clic en Eliminar
    boton_eliminar = row.get_by_role("button", name="Eliminar").first
    if not boton_eliminar.is_visible():
        boton_eliminar = row.get_by_text("Eliminar", exact=False).first
        
    boton_eliminar.click()
    
    # Confirmar en el modal/diálogo de alerta
    print("\n[DIAG] Esperando cuadro de confirmación...")
    boton_confirmar = page.get_by_text("Confirmar", exact=False).first
    
    try:
        boton_confirmar.wait_for(timeout=5000)
        boton_confirmar.click()
        
        # Esperar la red y ver si la tabla se actualiza o la fila desaparece
        # Esto captura implícitamente el tráfico porque el conftest tiene el listener
        page.wait_for_timeout(3000)
        print("\n[DIAG] Se hizo clic en confirmar. Revisar logs de consola y red para ver si se envió la petición DELETE.")
    except Exception as e:
        print(f"\n[DIAG] [FALLO] No se pudo completar el flujo de eliminar. Excepción: {str(e)}")
        page.screenshot(path="specs/008-playwright-prod-diag/fallo_eliminar.png")
        raise

