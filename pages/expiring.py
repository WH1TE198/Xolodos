import flet as ft
from ui.layout import page_layout
class ExpiringView(ft.Container):
    def __init__(self, page: ft.Page):
        lst = ft.ListView(
            expand=True,
            controls=[
                ft.ListTile(title=ft.Text("Продукт 1"), subtitle=ft.Text("до 18.09.2025")),
                ft.ListTile(title=ft.Text("Продукт 2"), subtitle=ft.Text("до 19.09.2025")),
            ],
        )
        super().__init__(
            expand=True,
            bgcolor=page.bgcolor,
            content=page_layout(page, "Скоро истекают", lst),
        )
