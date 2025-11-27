import flet as ft
from ui.layout import header_bar, sidebar
from ui.colors import APP_BG

class NotFoundView(ft.Column):
    def __init__(self, page: ft.Page, route: str):
        body = ft.Column(
            [ft.Text(f"Страница '{route}' не найдена", size=20)],
            expand=True
        )
        super().__init__(expand=True, spacing=0, bgcolor=APP_BG, controls=[
            header_bar("404"),
            ft.Row([sidebar(page), ft.Container(body, expand=True, padding=20)], expand=True)
        ])
