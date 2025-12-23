import flet as ft
from ui.layout import page_layout
from settings_db import set_setting, get_setting

class SettingsView(ft.Container):
    def __init__(self, page: ft.Page):

        def on_theme_change(e: ft.ControlEvent):
            is_dark = e.control.value
            page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
            set_setting("theme", "dark" if is_dark else "light")
            page.go(page.route)

        def on_rec_change(e: ft.ControlEvent):
            enabled = e.control.value
            set_setting("recommend_recipes", "1" if enabled else "0")
            page.snack_bar = ft.SnackBar(
                ft.Text("Рекомендации включены" if enabled else "Рекомендации выключены"),
                open=True,
            )
            page.update()

        rec_enabled = get_setting("recommend_recipes", "1") != "0"

        body = ft.Column(
            [
                ft.Text("Основные", size=20, weight="w700"),
                ft.Row(
                    [
                        ft.Text("Тёмная тема"),
                        ft.Switch(
                            value=(page.theme_mode == ft.ThemeMode.DARK),
                            on_change=on_theme_change,
                        ),
                    ],
                    spacing=20,
                ),
                ft.Container(height=22),
                ft.Text("Управление", size=20, weight="w700"),
                ft.Row(
                    [
                        ft.Text("Рекомендации рецептов"),
                        ft.Switch(value=rec_enabled, on_change=on_rec_change),
                    ],
                    spacing=18,
                ),
            ],
            spacing=14,
        )

        super().__init__(
            expand=True,
            bgcolor=page.bgcolor,
            content=page_layout(page, "Настройки", body),
        )
