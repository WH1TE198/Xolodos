import flet as ft
from router import Router
from ui.colors import APP_BG
from settings_db import init_settings_db, get_setting

def main(page: ft.Page):
    page.window_full_screen = False
    page.window_maximized = False
    page.window_resizable = False
    page.window_maximizable = False
    W, H = 1280, 800
    page.window_width = W
    page.window_height = H
    page.window_min_width = W
    page.window_min_height = H
    page.window_max_width = W
    page.window_max_height = H
    page.window_left = None
    page.window_top = None
    page.window_centered = True

    page.title = "FridgeMate"
    page.padding = 0

    init_settings_db()
    theme = get_setting("theme", "light")
    page.theme_mode = ft.ThemeMode.DARK if theme == "dark" else ft.ThemeMode.LIGHT
    page.bgcolor = "#0F1115" if page.theme_mode == ft.ThemeMode.DARK else APP_BG
    router = Router(page)

    def on_route_change(e):
        page.bgcolor = "#0F1115" if page.theme_mode == ft.ThemeMode.DARK else APP_BG
        view = router.resolve(page.route)
        page.clean()
        page.add(view)
        page.update()

    page.on_route_change = on_route_change
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
