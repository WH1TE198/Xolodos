import sys, os, threading
from datetime import datetime
import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.layout import page_layout
from products_db import init_products_db, insert_product
from ui.product_catalog import PRODUCT_CATEGORIES, category_options, product_options


class AddProductView(ft.Container):
    def __init__(self, page: ft.Page):
        init_products_db()

        cat = ft.Dropdown(
            label="Категория",
            width=420,
            hint_text="Выберите категорию",
            options=category_options(),
        )

        name_dd = ft.Dropdown(
            label="Продукт",
            width=420,
            hint_text="Сначала выберите категорию",
            options=[],
            disabled=True,
        )

        exp = ft.TextField(label="Срок годности до (ДД.ММ.ГГГГ)", width=420)

        def show_toast(msg: str, duration_ms: int = 1800):
            bg = "#16a34a"

            def close_toast(_=None):
                if wrapper in page.overlay:
                    page.overlay.remove(wrapper)
                    page.update()

            toast = ft.Container(
                width=360,
                bgcolor=bg,
                border_radius=12,
                padding=12,
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="white"),
                        ft.Text(msg, color="white", weight="w600"),
                        ft.IconButton(ft.Icons.CLOSE, icon_color="white", on_click=close_toast),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
            wrapper = ft.Container(alignment=ft.alignment.top_center, padding=20, content=toast)
            page.overlay.append(wrapper)
            page.update()
            t = threading.Timer(duration_ms / 1000.0, close_toast)
            t.daemon = True
            t.start()

        def valid_date(s: str) -> bool:
            s = (s or "").strip()
            try:
                datetime.strptime(s, "%d.%m.%Y")
                return True
            except Exception:
                return False

        def on_category_change(_):
            category = (cat.value or "").strip()

            name_dd.value = None
            name_dd.options = product_options(category)
            name_dd.disabled = (not category)

            if category:
                name_dd.hint_text = "Выберите продукт"
            else:
                name_dd.hint_text = "Сначала выберите категорию"

            page.update()

        cat.on_change = on_category_change

        def on_save(_):
            category = (cat.value or "").strip()
            product_name = (name_dd.value or "").strip()
            exp_date = (exp.value or "").strip()

            if not category:
                show_toast("Выбери категорию")
                return

            if category not in PRODUCT_CATEGORIES:
                show_toast("Некорректная категория")
                return

            if not product_name:
                show_toast("Выбери продукт")
                return

            if not valid_date(exp_date):
                show_toast("Дата: ДД.ММ.ГГГГ")
                return

            data = {"name": product_name, "category": category, "exp_date": exp_date}
            new_id = insert_product(data)

            show_toast(f"Продукт сохранён (id={new_id})")

            cat.value = None
            name_dd.value = None
            name_dd.options = []
            name_dd.disabled = True
            name_dd.hint_text = "Сначала выберите категорию"
            exp.value = ""
            page.update()

            def go_back():
                page.go("/search")

            t = threading.Timer(0.5, go_back)
            t.daemon = True
            t.start()

        save_btn = ft.ElevatedButton("Сохранить", icon=ft.Icons.SAVE, on_click=on_save)
        cancel_btn = ft.OutlinedButton("Отмена", icon=ft.Icons.CLOSE, on_click=lambda _: page.go("/search"))

        form = ft.Column(
            [
                ft.Text("Добавить продукт", size=22, weight="bold"),
                cat,
                name_dd,
                exp,
                ft.Row([save_btn, cancel_btn], spacing=10),
            ],
            spacing=12,
        )

        super().__init__(
            expand=True,
            bgcolor=page.bgcolor,
            content=page_layout(page, "Добавить продукт", form),
        )
