
import reflex as rx
from src.presentacion.components.sidebar import Sidebar

class MockUser:
    nombre_usuario = "admin"
    rol = "Administrador"

def main(page: ft.Page):
    try:
        user = MockUser()
        sidebar = Sidebar(user, lambda x: print(x), lambda: print("logout"))
        
        # Test creation
        page.add(sidebar)
        print("Sidebar created successfully")
        
        # Test toggle
        sidebar.toggle(None)
        print("Sidebar toggled successfully")
        
    except Exception as e:
        print(f"Error: {e}")

ft.app(target=main)
