# pages/user.py
import sys, os
from datetime import datetime
import threading
import flet as ft
from ui.colors import APP_BG, HEADER_BG, SIDEBAR_BG, BTN_BORDER, BTN_ICON

# Гарантируем импорт db из корня проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from db import init_db, insert_profile, last_profile_or_empty


# ---------- Вспомогательные UI-функции ----------
def sidebar_btn(icon, on_click):
    return ft.Container(
        width=76, height=60,
        bgcolor="white",                 # кнопки белые
        border=ft.border.all(1, BTN_BORDER),
        border_radius=14,
        padding=12, on_click=on_click,
        content=ft.Icon(icon, size=26, color=BTN_ICON),
    )


def header_bar(text: str) -> ft.Container:
    return ft.Container(
        bgcolor=HEADER_BG, height=96,
        alignment=ft.alignment.center_left,
        padding=ft.padding.only(left=18, right=18, top=14, bottom=14),
        content=ft.Text(text, size=24, color="white", weight="bold"),
    )


def page_layout(page: ft.Page, title: str, content: ft.Control) -> ft.Row:
    sidebar = ft.Container(
        width=96,
        bgcolor="white",
        padding=ft.padding.only(left=10, right=10, top=22, bottom=22),
        content=ft.Column(
            [
                sidebar_btn(ft.Icons.HOME,            lambda _: page.go("/")),
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


    # СЕРЫЙ столбик под иконками + тонкая правая граница
    sidebar = ft.Container(
        width=96,
        bgcolor=SIDEBAR_BG,                                  # ← серый фон столбика
        border=ft.border.only(right=ft.BorderSide(1, "#E5E7EB")),  # тонкий разделитель справа
        padding=ft.padding.only(left=10, right=10, top=22, bottom=22),
        content=ft.Column(
            [top_btns, ft.Container(expand=True), exit_btn],
            spacing=136,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
    )

    right = ft.Column(
        [
            header_bar(title),
            ft.Container(height=8, bgcolor="#00000022"),
            ft.Container(expand=True, padding=ft.padding.all(20), content=content),
        ],
        spacing=0,
        expand=True,
    )

    return ft.Row([sidebar, right], expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH)


# ------------- Страница "Пользователь" -------------
class UserView(ft.Container):
    def __init__(self, page: ft.Page):
        # Инициализируем БД и подставляем последние значения (если есть)
        init_db()
        data = last_profile_or_empty()

        # --- Поля формы ---
        avatar = ft.Container(
            width=140, height=140, bgcolor="#D0D3DA",
            border_radius=999,
            alignment=ft.alignment.center,
            content=ft.Icon(ft.Icons.PERSON, size=90, color="white"),
        )
        name = ft.TextField(label="Имя", width=520, value=data.get("name", ""))
        gender_group = ft.RadioGroup(
            value=(data.get("gender") or None),
            content=ft.Row(
                [ft.Radio(value="m", label="Мужской"),
                 ft.Radio(value="f", label="Женский")],
                spacing=30
            )
        )
        birth = ft.TextField(
            label="Дата рождения", hint_text="ДД.ММ.ГГГГ",
            width=520, value=data.get("birth", "") or ""
        )
        height_field = ft.TextField(
            label="Рост", hint_text="СМ", width=250,
            value="" if data.get("height_cm") is None else str(data.get("height_cm"))
        )
        weight_field = ft.TextField(
            label="Вес", hint_text="КГ", width=250,
            value="" if data.get("weight_kg") is None else str(data.get("weight_kg"))
        )

        # --- Зелёный тост (компактный, автоисчезает) ---
        def show_toast(msg: str, duration_ms: int = 2200):
            bg = "#16a34a"
            ic = ft.Icons.CHECK_CIRCLE_OUTLINE

            def close_toast(_=None):
                if wrapper in page.overlay:
                    page.overlay.remove(wrapper)
                    page.update()

            toast_box = ft.Container(
                width=360,
                bgcolor=bg,
                border_radius=12,
                padding=12,
                content=ft.Row(
                    [
                        ft.Icon(ic, color="white"),
                        ft.Text(msg, color="white", weight="w600"),
                        ft.IconButton(ft.Icons.CLOSE, icon_color="white",
                                      on_click=close_toast, tooltip="Закрыть"),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
            wrapper = ft.Container(
                alignment=ft.alignment.top_center,
                padding=20,
                content=toast_box,
            )

            page.overlay.append(wrapper)
            page.update()

            timer = threading.Timer(duration_ms / 1000.0, close_toast)
            timer.daemon = True
            timer.start()

        def notify(msg: str):
            show_toast(msg)

        # --- Валидации ---
        def to_float(s: str):
            s = (s or "").strip()
            if not s:
                return None
            try:
                return float(s.replace(",", "."))
            except ValueError:
                return None

        def validate_birth(s: str) -> bool:
            s = (s or "").strip()
            if not s:
                return True
            try:
                datetime.strptime(s, "%d.%m.%Y")
                return True
            except ValueError:
                return False

        # --- Кнопка «Сохранить» и обработчик ---
        save_btn = ft.ElevatedButton(
            text="Сохранить", bgcolor="#1E1E1E", color="white", width=180
        )

        def on_save(e: ft.ControlEvent):
            save_btn.disabled = True
            page.update()

            profile = {
                "name": (name.value or "").strip(),
                "gender": gender_group.value if gender_group.value in ("m", "f") else None,
                "birth": (birth.value or "").strip(),
                "height_cm": to_float(height_field.value),
                "weight_kg": to_float(weight_field.value),
            }

            if not profile["name"]:
                notify("Укажи имя")
                save_btn.disabled = False
                page.update()
                return

            if not validate_birth(profile["birth"]):
                notify("Некорректная дата (ДД.ММ.ГГГГ)")
                save_btn.disabled = False
                page.update()
                return

            try:
                new_id = insert_profile(profile)
                notify(f"Профиль сохранён (id={new_id})")
            except Exception:
                notify("Данные сохранены")
            finally:
                save_btn.disabled = False
                page.update()

        save_btn.on_click = on_save

        # --- Разметка формы ---
        form = ft.Column(
            [
                ft.Row([avatar, ft.Container(width=24), ft.Text("Имя"), name], alignment="start"),
                ft.Row([ft.Text("Пол"), gender_group]),
                ft.Row([ft.Text("Дата рождения"), birth]),
                ft.Row([ft.Text("Рост"), height_field, ft.Container(width=24), ft.Text("Вес"), weight_field]),
                ft.Container(height=10),
                ft.Row([save_btn], alignment="end"),
                ft.Container(expand=True),
            ],
            spacing=14,
        )

        super().__init__(bgcolor=APP_BG, content=page_layout(page, "Пользователь", form))
