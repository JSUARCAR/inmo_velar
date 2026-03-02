import reflex as rx
import importlib
import sys
import traceback

def test_page_compilation(page_module_path):
    print(f"Testing {page_module_path}...")
    try:
        # Import the module
        module = importlib.import_module(page_module_path)
        
        # Find components that might be pages
        for name, obj in vars(module).items():
            if isinstance(obj, rx.Component):
                print(f"  Rendering component: {name}")
                try:
                    # Try to render the component
                    obj.render()
                    print(f"  [OK] {name}")
                except Exception as e:
                    print(f"  [FAIL] {name}: {type(e).__name__}: {e}")
                    traceback.print_exc()
            elif callable(obj) and name.endswith("_page"):
                print(f"  Calling and rendering: {name}")
                try:
                    comp = obj()
                    if isinstance(comp, rx.Component):
                        comp.render()
                        print(f"  [OK] {name}")
                except Exception as e:
                    print(f"  [FAIL] {name}: {type(e).__name__}: {e}")
                    traceback.print_exc()
    except Exception as e:
        print(f"Error importing {page_module_path}: {e}")

if __name__ == "__main__":
    pages = [
        "src.presentacion_reflex.pages.configuracion",
        "src.presentacion_reflex.pages.contratos",
        "src.presentacion_reflex.pages.dashboard",
        "src.presentacion_reflex.pages.desocupaciones",
        "src.presentacion_reflex.pages.incidentes",
        "src.presentacion_reflex.pages.incrementos",
        "src.presentacion_reflex.pages.liquidacion_asesores",
        "src.presentacion_reflex.pages.liquidaciones",
        "src.presentacion_reflex.pages.login",
        "src.presentacion_reflex.pages.personas",
        "src.presentacion_reflex.pages.propiedades",
        "src.presentacion_reflex.pages.proveedores",
        "src.presentacion_reflex.pages.recaudos",
        "src.presentacion_reflex.pages.recibos",
        "src.presentacion_reflex.pages.seguros",
        "src.presentacion_reflex.pages.usuarios",
        "src.presentacion_reflex.pages.auditoria",
        "src.presentacion_reflex.pages.saldos_favor",
        "src.presentacion_reflex.pages.reportes",
    ]
    
    for p in pages:
        test_page_compilation(p)
        print("-" * 40)
