import sys, os, threading, math
import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.layout import page_layout
from ui.colors import PILL
from products_db import init_products_db, list_products, delete_product


class SearchView(ft.Container):
    def __init__(self, page: ft.Page):
        init_products_db()

        self.page = page
        self._all = list_products(limit=500)
        self._query = ""
        self.is_dark = page.theme_mode == ft.ThemeMode.DARK

        self.tile_bg = "#171B26" if self.is_dark else "white"
        self.tile_border = "#2A3042" if self.is_dark else "#CBD5E1"
        self.text_primary = "#E9ECF5" if self.is_dark else "#111827"
        self.text_muted = "#AAB2C8" if self.is_dark else "#6B7280"
        self.delete_color = "#9AB3FF" if self.is_dark else "#1E3A8A"

        self.PAGE_SIZE = 5
        self.page_index = 0
        self.total_pages = 1

        # соответствие категорий файлам в assets/img/categories/
        self.CATEGORY_IMG = {
            "Овощи": "img/categories/Овощи.png",
            "Фрукты": "img/categories/Фрукты.png",
            "Молочное": "img/categories/Молочное.png",
            "Мясо": "img/categories/Мясо.png",
            "Морепродукты": "img/categories/Морепродукты.png",
            "Напитки": "img/categories/Напитки.png",
            "Выпечка": "img/categories/Выпечка.png",
            "Соусы/Специи": "img/categories/Соусы_Специи.png",
            "Крупы/Макароны": "img/categories/Крупы_Макароны.png",
            "Консервы": "img/categories/Консервы.png",
            "Другое": "img/categories/Другое.png",
        }
        self.DEFAULT_CAT_IMG = "img/categories/default.png"

        def show_toast(msg: str, duration_ms: int = 1600):
            bg = "#16a34a"

            def close_toast(_=None):
                if wrapper in page.overlay:
                    page.overlay.remove(wrapper)
                    page.update()

            toast = ft.Container(
                width=320,
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

        self._toast = show_toast

        self.search = ft.TextField(
            label="Поиск",
            hint_text="Введите название, категорию или дату",
            width=1000,
            on_change=self._on_search_change,
        )

        add_btn = ft.ElevatedButton(
            "Добавить",
            icon=ft.Icons.ADD,
            bgcolor=PILL,
            color="white",
            height=40,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=999),
                elevation=2,
                padding=ft.padding.symmetric(horizontal=18, vertical=0),
            ),
            on_click=lambda _: page.go("/add"),
        )

        top = ft.Row([self.search, add_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.listview = ft.ListView(expand=True, spacing=14, padding=0)

        self.prev_btn = ft.OutlinedButton("Назад", icon=ft.Icons.CHEVRON_LEFT, on_click=self._prev_page)
        self.next_btn = ft.OutlinedButton("Вперёд", icon=ft.Icons.CHEVRON_RIGHT, on_click=self._next_page)
        self.page_label = ft.Text("", size=13, color=self.text_muted)

        pager = ft.Row(
            [self.prev_btn, self.page_label, self.next_btn],
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self._render_list(initial=True)

        body = ft.Column([top, ft.Container(height=8), self.listview, ft.Container(height=8), pager], expand=True)

        super().__init__(
            expand=True,
            bgcolor=page.bgcolor,
            content=page_layout(page, "Поиск", body),
        )

    def _cat_src(self, category: str | None) -> str:
        cat = (category or "").strip()
        return self.CATEGORY_IMG.get(cat, self.DEFAULT_CAT_IMG)

    def _on_search_change(self, e: ft.ControlEvent):
        self._query = (self.search.value or "").strip().lower()
        self.page_index = 0
        self._render_list()
        self.listview.update()

    def _filter_items(self):
        if not self._query:
            return self._all
        q = self._query
        return [
            p
            for p in self._all
            if (p["name"] or "").lower().find(q) >= 0
            or (p["category"] or "").lower().find(q) >= 0
            or (p["exp_date"] or "").lower().find(q) >= 0
        ]

    def _update_pager_controls(self, total_items: int):
        self.total_pages = max(1, math.ceil(total_items / self.PAGE_SIZE))
        if self.page_index >= self.total_pages:
            self.page_index = self.total_pages - 1
        if self.page_index < 0:
            self.page_index = 0
        self.page_label.value = f"{self.page_index + 1} / {self.total_pages}"
        self.prev_btn.disabled = self.page_index == 0
        self.next_btn.disabled = self.page_index >= self.total_pages - 1

    def _render_list(self, initial: bool = False):
        self._all = list_products(limit=500)
        items = self._filter_items()

        self._update_pager_controls(len(items))
        start = self.page_index * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        page_slice = items[start:end]

        self.listview.controls.clear()

        if not items:
            self.listview.controls.append(
                ft.Container(
                    bgcolor=self.tile_bg,
                    border=ft.border.all(1, self.tile_border),
                    border_radius=12,
                    padding=16,
                    content=ft.Text("Ничего не найдено", size=16, color=self.text_muted),
                )
            )
        else:
            for p in page_slice:
                self.listview.controls.append(self._product_tile(p))

        if not initial:
            self.page_label.update()
            self.prev_btn.update()
            self.next_btn.update()
            self.listview.update()

    def _prev_page(self, e):
        if self.page_index > 0:
            self.page_index -= 1
            self._render_list()

    def _next_page(self, e):
        if self.page_index < self.total_pages - 1:
            self.page_index += 1
            self._render_list()

    def _product_tile(self, p: dict) -> ft.Container:
        left_icon = ft.Image(
        src=self._cat_src(p.get("category")),
        width=52,
        height=52,
        fit=ft.ImageFit.COVER,
    )


        name = ft.Text(p["name"] or "—", size=16, weight="w600", color=self.text_primary)
        sub = ft.Text(f"До {p['exp_date'] or '—'}", size=12, color=self.text_muted)

        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            tooltip="Удалить",
            icon_color=self.delete_color,
            on_click=lambda _: self._delete_now(p),
        )

        row = ft.Row(
            [left_icon, ft.Column([name, sub], spacing=2, expand=True), delete_btn],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        return ft.Container(
            bgcolor=self.tile_bg,
            border=ft.border.all(2, self.tile_border),
            border_radius=12,
            padding=12,
            content=row,
        )

    def _delete_now(self, p: dict):
        try:
            delete_product(p["id"])
            self._toast("Удалено")
        except Exception:
            self._toast("Удалено")
        finally:
            if self.page_index > 0 and (self.page_index * self.PAGE_SIZE) >= (len(self._filter_items()) - 1):
                self.page_index -= 1
            self._render_list()
