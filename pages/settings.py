# pages/settings.py
import flet as ft
from ui.colors import APP_BG, HEADER_BG, SIDEBAR_BG, BTN_BORDER, BTN_ICON

# карточка-кнопка в сайдбаре
def sidebar_btn(icon, on_click):
    return ft.Container(
        width=76, height=60, bgcolor="white",
        border=ft.border.all(1, BTN_BORDER), border_radius=14,
        padding=12, on_click=on_click,
        content=ft.Icon(icon, size=26, color=BTN_ICON),
    )

# шапка
def header_bar(text: str) -> ft.Container:
    return ft.Container(
        bgcolor=HEADER_BG, height=96,
        alignment=ft.alignment.center_left,
        padding=ft.padding.only(left=18, right=18, top=14, bottom=14),
        content=ft.Text(text, size=24, color="white", weight="bold"),
    )

# общий каркас страницы: левый сайдбар + правая колонка
def page_layout(page: ft.Page, title: str, content: ft.Control) -> ft.Row:
    sidebar = ft.Container(
        width=96,
        bgcolor="white",
        padding=ft.padding.only(left=10, right=10, top=22, bottom=22),
        content=ft.Column(
            [
                sidebar_btn(ft.Icons.HOME,            lambda _: page.go("/home")),
                sidebar_btn(ft.Icons.SEARCH,          lambda _: page.go("/search")),
                sidebar_btn(ft.Icons.RESTAURANT_MENU, lambda _: page.go("/recipes")),
                sidebar_btn(ft.Icons.SETTINGS,        lambda _: page.go("/settings")),
                sidebar_btn(ft.Icons.PERSON,          lambda _: page.go("/user")),
                ft.Container(
                    margin=ft.margin.only(top=170),
                    content=sidebar_btn(ft.Icons.EXIT_TO_APP, lambda _: page.window_close()),
                ),
            ],
            spacing=22,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    right = ft.Column(
        [
            header_bar(title),
            ft.Container(expand=True, padding=ft.padding.all(20), content=content),
        ],
        spacing=0,
        expand=True,
    )

    return ft.Row([sidebar, right], expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH)


    # выход — прижат к самому низу
    exit_btn = sidebar_btn(ft.Icons.EXIT_TO_APP, lambda _: page.window_close())

    sidebar = ft.Container(
        width=96,
        bgcolor=APP_BG,
        padding=ft.padding.only(left=10, right=10, top=22, bottom=22),
        content=ft.Column(
            [
                top_btns,
                ft.Container(expand=True),   # растяжка, которая вытолкнет выход вниз
                exit_btn,                    # кнопка в самом низу
            ],
            spacing=136,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
    )

    right = ft.Column(
        [
            header_bar(title),                        # шапка строго сверху
            ft.Container(height=8, bgcolor="#00000022"),
            ft.Container(expand=True, padding=ft.padding.all(20), content=content),
        ],
        spacing=0,
        expand=True,
    )

    return ft.Row(
        [sidebar, right],
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

# -------- страница "Настройки" --------
class SettingsView(ft.Container):
    def __init__(self, page: ft.Page):
        body = ft.Column(
            [
                ft.Text("Основные", size=20, weight="w700"),
                ft.Row([ft.Text("Тема"), ft.TextField(value="Светлая", width=220)], spacing=20),
                ft.Container(height=22),
                ft.Text("Управление", size=20, weight="w700"),
                ft.Row([ft.Text("Рекомендации рецептов"), ft.Switch(value=False)], spacing=18),
                ft.Row([ft.Text("Уведомления"), ft.Switch(value=False)], spacing=18),
                ft.Container(expand=True),
            ],
            spacing=14,
        )

        super().__init__(
            bgcolor=APP_BG,
            content=page_layout(page, "Настройки", body),
        )
