# pages/add_product.py
import sys, os, threading
from datetime import datetime
import flet as ft

# доступ к корню проекта (для импорта БД)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.colors import APP_BG, HEADER_BG, SIDEBAR_BG, BTN_BORDER, BTN_ICON
from products_db import init_products_db, insert_product


# ---- Компоненты общего макета ----
def sidebar_btn(icon, on_click):
    return ft.Container(
        width=76, height=60, bgcolor="white",
        border=ft.border.all(1, BTN_BORDER), border_radius=14,
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
    # левый сайдбар (белый фон, единый порядок кнопок; Exit снизу)
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

    # правая часть: шапка + контент
    right = ft.Column(
        [
            header_bar(title),
            ft.Container(expand=True, padding=ft.padding.all(20), content=content),
        ],
        spacing=0,
        expand=True,
    )

    return ft.Row([sidebar, right], expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH)


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


# ------------- Страница "Добавить продукт" -------------
class AddProductView(ft.Container):
    def __init__(self, page: ft.Page):
        init_products_db()

        # поля формы
        name = ft.TextField(label="Название продукта", width=420)

        # ВЫПАДАЮЩИЙ СПИСОК КАТЕГОРИЙ
        cat = ft.Dropdown(
            label="Категория",
            width=420,
            hint_text="Выберите категорию",
            options=[
                ft.dropdown.Option("Овощи"),
                ft.dropdown.Option("Фрукты"),
                ft.dropdown.Option("Молочное"),
                ft.dropdown.Option("Мясо"),
                ft.dropdown.Option("Морепродукты"),
                ft.dropdown.Option("Напитки"),
                ft.dropdown.Option("Выпечка"),
                ft.dropdown.Option("Соусы/Специи"),
                ft.dropdown.Option("Другое"),
            ],
        )

        exp  = ft.TextField(label="Срок годности до (ДД.ММ.ГГГГ)", width=420)

        # зелёный тост (узкий, автоисчезает)
        def show_toast(msg: str, duration_ms: int = 1800):
            bg = "#16a34a"
            def close_toast(_=None):
                if wrapper in page.overlay:
                    page.overlay.remove(wrapper)
                    page.update()
            toast = ft.Container(
                width=360, bgcolor=bg, border_radius=12, padding=12,
                content=ft.Row(
                    [ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="white"),
                     ft.Text(msg, color="white", weight="w600"),
                     ft.IconButton(ft.Icons.CLOSE, icon_color="white", on_click=close_toast)],
                    spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
            wrapper = ft.Container(alignment=ft.alignment.top_center, padding=20, content=toast)
            page.overlay.append(wrapper); page.update()
            t = threading.Timer(duration_ms/1000.0, close_toast); t.daemon = True; t.start()

        def valid_date(s: str) -> bool:
            s = (s or "").strip()
            try:
                datetime.strptime(s, "%d.%m.%Y")
                return True
            except Exception:
                return False

        def on_save(_):
            data = {
                "name": (name.value or "").strip(),
                "category": (cat.value or "") or "",      # значение из Dropdown
                "exp_date": (exp.value or "").strip(),
            }
            if not data["name"]:
                show_toast("Укажи название")
                return
            if not valid_date(data["exp_date"]):
                show_toast("Дата: ДД.ММ.ГГГГ")
                return

            new_id = insert_product(data)
            show_toast(f"Продукт сохранён (id={new_id})")

            # очистим поля
            name.value = ""; cat.value = None; exp.value = ""; page.update()

            # мягкий редирект назад в поиск
            def go_back():
                page.go("/search")
            t = threading.Timer(0.5, go_back); t.daemon = True; t.start()

        save_btn   = ft.ElevatedButton("Сохранить", icon=ft.Icons.SAVE, on_click=on_save)
        cancel_btn = ft.OutlinedButton("Отмена",   icon=ft.Icons.CLOSE, on_click=lambda _: page.go("/search"))

        form = ft.Column(
            [
                ft.Text("Добавить продукт", size=22, weight="bold"),
                name, cat, exp,
                ft.Row([save_btn, cancel_btn], spacing=10),
            ],
            spacing=12,
        )

        super().__init__(bgcolor=APP_BG, content=page_layout(page, "Добавить продукт", form))
