
import flet as ft

def main(page: ft.Page):
    try:
        btn = ft.IconButton(icon=ft.Icons.MENU, size=20)
        page.add(btn)
        print("Success: IconButton created with size")
    except TypeError as e:
        print(f"Error: {e}")

ft.app(target=main)
