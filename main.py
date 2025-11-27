# main.py
import flet as ft
from router import Router
from ui.colors import APP_BG

def main(page: ft.Page):
    # --- фиксируем размер и позицию окна ---
    page.window_maximized = False
    page.window_full_screen = False
    page.window_resizable = False

    page.window_width = 1280    # <- поставь нужные тебе числа
    page.window_height = 800
    page.window_min_width = 1280
    page.window_min_height = 800
    page.window_max_width = 1280
    page.window_max_height = 800

    # необязательно, но можно задать позицию:
    page.window_left = None     # или, например, 100
    page.window_top = None      # или 80
    page.window_centered = True

    page.title = "FridgeMate"
    page.bgcolor = APP_BG
    page.padding = 0
    page.theme_mode = "light"

    router = Router(page)

    def on_route_change(e):
        view = router.resolve(page.route)
        page.clean()
        page.add(view)
        page.update()

    page.on_route_change = on_route_change
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
