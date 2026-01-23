
import flet as ft
import time

def main(page: ft.Page):
    page.title = "SnackBar Test"

    def show_snackbar_old(e):
        print("Intentando SnackBar (Método Antiguo)...")
        try:
            page.snack_bar = ft.SnackBar(content=ft.Text("Hola desde Old Method!"))
            page.snack_bar.open = True
            page.update()
            print("SnackBar asignado y update llamado.")
        except Exception as ex:
            print(f"Error Old: {ex}")

    def show_snackbar_new(e):
        print("Intentando SnackBar (Método Nuevo - page.open)...")
        try:
            sb = ft.SnackBar(content=ft.Text("Hola desde New Method!"))
            page.open(sb)
            print("page.open(sb) llamado.")
        except AttributeError:
            print("page.open no existe (Flet version antigua).")
        except Exception as ex:
            print(f"Error New: {ex}")

    old_btn = ft.ElevatedButton("Old Method", on_click=show_snackbar_old)
    new_btn = ft.ElevatedButton("New Method (page.open)", on_click=show_snackbar_new)

    page.add(old_btn, new_btn)

if __name__ == "__main__":
    ft.app(target=main)
