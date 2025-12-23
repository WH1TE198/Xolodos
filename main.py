import os, sys
import flet as ft
from router import Router
from ui.colors import APP_BG
from settings_db import init_settings_db, get_setting

def resource_path(rel_path: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)

def main(page: ft.Page):
    page.title = "FridgeMate"
    page.padding = 0
    page.window_icon = "appicon.ico"
    init_settings_db()
    theme = get_setting("theme", "light")
    page.theme_mode = ft.ThemeMode.DARK if theme == "dark" else ft.ThemeMode.LIGHT
    def apply_bg():
        page.bgcolor = "#0F1115" if page.theme_mode == ft.ThemeMode.DARK else APP_BG
    apply_bg()
    router = Router(page)
    def on_route_change(_):
        apply_bg()
        page.clean()
        page.add(router.resolve(page.route))
        page.update()
    page.on_route_change = on_route_change
    page.go("/")

if __name__ == "__main__":
    ft.app(
        target=main,
        view=ft.AppView.FLET_APP,
        assets_dir=resource_path("assets"),
    )
