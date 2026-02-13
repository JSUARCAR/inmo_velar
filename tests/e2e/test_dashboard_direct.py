
import reflex as rx
from src.dominio.entidades.usuario import Usuario
from src.presentacion.views.dashboard_view import crear_dashboard_view
from src.presentacion.theme import colors

def main(page: ft.Page):
    print("DEBUG: Iniciando test directo dashboard")
    page.title = "Test Dashboard"
    page.bgcolor = colors.BACKGROUND
    page.window_width = 1366
    page.window_height = 768
    
    # Mock user
    admin_user = Usuario(id_usuario=1, nombre_usuario="admin", rol="Administrador")
    
    def on_logout():
        print("Logout clicked")

    try:
        dash = crear_dashboard_view(page, admin_user, on_logout)
        page.add(dash)
        page.update()
        print("DEBUG: Dashboard added to page")
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ft.app(target=main)
