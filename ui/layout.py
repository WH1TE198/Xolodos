import flet as ft
from datetime import datetime
from .colors import *

# ---- Шапка ----
def header_bar(title: str) -> ft.Container:
    return ft.Container(
        bgcolor=HEADER_BG,
        padding=ft.padding.only(left=18, right=18, top=12, bottom=12),
        content=ft.Text(title, size=22, color="white", weight="bold"),
    )

# ---- Кнопка сайдбара ----
def _sidebar_btn(icon, tip, on_click):
    return ft.Container(
        bgcolor="white",
        border=ft.border.all(1, "#E5E6EB"),
        border_radius=14,
        padding=12,
        on_click=on_click,
        content=ft.Icon(icon, color="#7A7D85", size=22),
    )

# ---- Сайдбар ----
def sidebar(page) -> ft.Container:
    def go(route): page.go(route)
    return ft.Container(
        width=76,
        bgcolor="#F4F5FA",
        padding=10,
        content=ft.Column(
            [
                ft.Column(
                    [
                        _sidebar_btn(ft.Icons.HOME, "Главная", lambda _: go("/")),
                        _sidebar_btn(ft.Icons.SEARCH, "Поиск", lambda _: go("/search")),
                        _sidebar_btn(ft.Icons.RESTAURANT_MENU, lambda _: go("/recipes")),
                        _sidebar_btn(ft.Icons.SETTINGS, "Настройки", lambda _: go("/settings")),
                        _sidebar_btn(ft.Icons.PERSON, "Профиль", lambda _: go("/user")),
                    ],
                    spacing=18,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                _sidebar_btn(ft.Icons.EXIT_TO_APP, "Выход", lambda _: page.window_close()),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
        ),
    )

# ---- Карточка статистики ----
def stats_card(title: str, value: str = "—") -> ft.Container:
    return ft.Container(
        bgcolor="white",
        border=ft.border.all(2, "#8E8E8E"),
        border_radius=10,
        padding=12,
        width=230,
        height=85,
        content=ft.Column(
            [ft.Text(title, size=12), ft.Text(value, size=16, weight="w600")],
            spacing=6,
        ),
    )

# ---- Мини-бэйдж времени/даты ----
def clock_badge() -> ft.Container:
    now = datetime.now()
    return ft.Container(
        width=100,
        height=60,
        bgcolor="#1E1E1E",
        border_radius=8,
        padding=ft.padding.all(8),
        content=ft.Column(
            [
                ft.Text(now.strftime("%H:%M"), size=16, color="white", weight="bold"),
                ft.Text(now.strftime("%d.%m.%Y"), size=11, color="white"),
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

# ---- Основной шаблон ----
def scaffold(page: ft.Page, title: str, body: ft.Control) -> ft.Container:
    return ft.Container(
        bgcolor=APP_BG,
        expand=True,
        content=ft.Column(
            [
                header_bar(title),
                ft.Row(
                    [
                        sidebar(page),
                        ft.Container(body, expand=True, padding=20),
                    ],
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        ),
    )
