# pages/search.py
import sys, os, threading, math
import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.colors import APP_BG, HEADER_BG, BTN_BORDER, BTN_ICON, PILL
from products_db import init_products_db, list_products, delete_product


# ---- Общий макет (как на других страницах) ----
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

    return ft.Row(
        [sidebar, right],
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )


# ------------- Страница "Поиск" с пагинацией -------------
class SearchView(ft.Container):
    def __init__(self, page: ft.Page):
        init_products_db()

        self.page = page
        self._all = list_products(limit=500)
        self._query = ""

        # ---- ПАГИНАЦИЯ ----
        self.PAGE_SIZE = 5
        self.page_index = 0  # нумерация с 0
        self.total_pages = 1

        # компактный зелёный тост
        def show_toast(msg: str, duration_ms: int = 1600):
            bg = "#16a34a"
            def close_toast(_=None):
                if wrapper in page.overlay:
                    page.overlay.remove(wrapper)
                    page.update()
            toast = ft.Container(
                width=320, bgcolor=bg, border_radius=12, padding=12,
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

        self._toast = show_toast

        self.search = ft.TextField(
            label="Поиск",
            hint_text="Введите название, категорию или дату",
            width=1000,
            on_change=self._on_search_change,
        )

        # Фиолетовая «пилюля» Добавить
        add_btn = ft.ElevatedButton(
            "Добавить",
            icon=ft.Icons.ADD,
            bgcolor=PILL,           # фирменный фиолетовый
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

        # Список и панель пагинации
        self.listview = ft.ListView(expand=True, spacing=14, padding=0)

        self.prev_btn = ft.OutlinedButton("Назад", icon=ft.Icons.CHEVRON_LEFT, on_click=self._prev_page)
        self.next_btn = ft.OutlinedButton("Вперёд", icon=ft.Icons.CHEVRON_RIGHT, icon_color="#111827", on_click=self._next_page)
        self.page_label = ft.Text("", size=13, color="#6B7280")

        pager = ft.Row(
            [self.prev_btn, self.page_label, self.next_btn],
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self._render_list(initial=True)

        body = ft.Column([top, ft.Container(height=8), self.listview, ft.Container(height=8), pager], expand=True)

        super().__init__(bgcolor=APP_BG, content=page_layout(page, "Поиск", body))

    # --- логика ---
    def _on_search_change(self, e: ft.ControlEvent):
        self._query = (self.search.value or "").strip().lower()
        self.page_index = 0  # при новом запросе — на первую страницу
        self._render_list()
        self.listview.update()

    def _filter_items(self):
        if not self._query:
            return self._all
        q = self._query
        return [
            p for p in self._all
            if (p["name"] or "").lower().find(q) >= 0
            or (p["category"] or "").lower().find(q) >= 0
            or (p["exp_date"] or "").lower().find(q) >= 0
        ]

    def _update_pager_controls(self, total_items: int):
        self.total_pages = max(1, math.ceil(total_items / self.PAGE_SIZE))
        # держим индекс в допустимом диапазоне
        if self.page_index >= self.total_pages:
            self.page_index = self.total_pages - 1
        if self.page_index < 0:
            self.page_index = 0

        self.page_label.value = f"{self.page_index + 1} / {self.total_pages}"
        self.prev_btn.disabled = (self.page_index == 0)
        self.next_btn.disabled = (self.page_index >= self.total_pages - 1)

    def _render_list(self, initial: bool = False):
        # перечитываем из БД (видим новые/удалённые)
        self._all = list_products(limit=500)

        items = self._filter_items()
        self._update_pager_controls(len(items))

        # какие элементы показываем на текущей странице
        start = self.page_index * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        page_slice = items[start:end]

        self.listview.controls.clear()

        if not items:
            self.listview.controls.append(
                ft.Container(
                    bgcolor="white",
                    border=ft.border.all(1, "#D2D5DC"),
                    border_radius=12,
                    padding=16,
                    content=ft.Text("Ничего не найдено", size=16, color="#555"),
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
        left_icon = ft.Container(
            width=52, height=52, bgcolor="#EEF2FF",
            border=ft.border.all(2, "#C7D2FE"),
            border_radius=12,
            alignment=ft.alignment.center,
            content=ft.Icon(ft.Icons.IMAGE, color="#64748B"),
        )
        name = ft.Text(p["name"] or "—", size=16, weight="w600")
        sub = ft.Text(f"До {p['exp_date'] or '—'}", size=12, color="#6B7280")

        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            tooltip="Удалить",
            icon_color="#1E3A8A",
            on_click=lambda _: self._delete_now(p),
        )

        row = ft.Row(
            [left_icon, ft.Column([name, sub], spacing=2, expand=True), delete_btn],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        return ft.Container(
            bgcolor="white",
            border=ft.border.all(2, "#CBD5E1"),
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
            # если удалили последний элемент на странице — откатимся на предыдущую страницу
            if self.page_index > 0 and (self.page_index * self.PAGE_SIZE) >= (len(self._filter_items()) - 1):
                self.page_index -= 1
            self._render_list()
