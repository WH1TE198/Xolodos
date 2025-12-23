import flet as ft
from ui.layout import page_layout
class NotFoundView(ft.Container):
    def __init__(self, page: ft.Page, route: str):
        body = ft.Column(
            [ft.Text(f"Страница '{route}' не найдена", size=20)],
            expand=True,
        )
        super().__init__(
            expand=True,
            bgcolor=page.bgcolor,
            content=page_layout(page, "404", body),
        )
