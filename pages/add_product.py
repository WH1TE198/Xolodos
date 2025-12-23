import sys, os, threading
from datetime import datetime
import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.layout import page_layout
from products_db import init_products_db, insert_product


#Страница "Добавить продукт"
class AddProductView(ft.Container):
    def __init__(self, page: ft.Page):
        init_products_db()
        name = ft.TextField(label="Название продукта", width=420)
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
        def on_save(_):
            data = {
                "name": (name.value or "").strip(),
                "category": (cat.value or "") or "",
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
            name.value = ""
            cat.value = None
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
                name,
                cat,
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
