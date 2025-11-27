# pages/recipes.py
import math
import flet as ft
from ui.colors import APP_BG, HEADER_BG, BTN_BORDER, BTN_ICON
from recommend import suggest_recipes
from recipes_db import (
    init_recipes_db,
    seed_demo_if_empty,
    seed_world_recipes,
    seed_more_world_recipes,
)

def sidebar_btn(icon, on_click):
    return ft.Container(
        width=76, height=60, bgcolor="white",
        border=ft.border.all(1, BTN_BORDER),
        border_radius=14, padding=12, on_click=on_click,
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
        width=96, bgcolor="white",
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
            spacing=22, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
    right = ft.Column(
        [header_bar(title),
         ft.Container(expand=True, padding=20, content=content)],
        spacing=0, expand=True,
    )
    return ft.Row([sidebar, right], expand=True,
                  vertical_alignment=ft.CrossAxisAlignment.STRETCH)

class RecipesView(ft.Container):
    PAGE_SIZE = 3

    def __init__(self, page: ft.Page):
        self.page = page

        # БД и демо-данные
        init_recipes_db()
        seed_demo_if_empty()
        seed_world_recipes()
        seed_more_world_recipes()

        # Все рекомендации
        self.items: list[dict] = suggest_recipes(top_n=100)
        self.page_index: int = 0
        self.total_pages: int = max(1, math.ceil(len(self.items) / self.PAGE_SIZE))

        # Заголовок + контейнер для карточек
        self.title_text = ft.Text("Рецепты из того, что есть", size=20, weight="w700")
        self.cards_column = ft.Column(spacing=14)  # сюда кладём 3 карточки за раз

        # Кнопки пагинации
        self.prev_btn = ft.OutlinedButton("Назад", icon=ft.Icons.CHEVRON_LEFT, on_click=self._prev_page)
        self.next_btn = ft.OutlinedButton("Вперёд", icon=ft.Icons.CHEVRON_RIGHT, on_click=self._next_page)
        self.page_label = ft.Text("", size=13, color="#6B7280")

        pager = ft.Row(
            [self.prev_btn, self.page_label, self.next_btn],
            spacing=10, alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Первый рендер без update (ещё не добавлено на страницу)
        self._render_page(initial=True)

        body = ft.Column([self.title_text, self.cards_column, ft.Container(height=8), pager],
                         spacing=14, expand=True)
        super().__init__(bgcolor=APP_BG, content=page_layout(page, "Рецепты", body))

    # ---------- построение карточки ----------
    def _pill(self, text: str, color="#111827"):
        return ft.Container(
            bgcolor="#F3F4F6", border=ft.border.all(1, "#E5E7EB"),
            border_radius=999, padding=ft.padding.symmetric(horizontal=10, vertical=4),
            content=ft.Text(text, size=12, color=color),
        )

    def _recipe_card(self, sug: dict) -> ft.Container:
        r = sug["recipe"]
        have = ", ".join([i.get("name") or "—" for i in sug.get("have", [])]) or "—"
        missing = ", ".join([i.get("name") or "—" for i in sug.get("missing", [])]) or "—"

        meta = []
        if r.get("time_min") is not None:
            meta.append(self._pill(f"{r['time_min']} мин"))
        if r.get("difficulty"):
            meta.append(self._pill(r["difficulty"]))

        btn_row = ft.Row(
            [
                ft.ElevatedButton(
                    "Готовлю", icon=ft.Icons.RESTAURANT,
                    on_click=lambda _: (
                        setattr(self.page, "snack_bar",
                                ft.SnackBar(ft.Text("Отлично! Можешь перейти к шагам рецепта."), open=True)),
                        self.page.update()
                    ),
                ),
            ],
            spacing=10,
        )

        return ft.Container(
            bgcolor="white", border=ft.border.all(1, "#E5E6EB"),
            border_radius=14, padding=16,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(r["title"], size=18, weight="w700"),
                            ft.Container(expand=True),
                            *meta, ft.Container(width=8),
                            ft.Chip(label=ft.Text(str(sug.get("score", 0))), bgcolor="#EEF2FF"),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(f"Есть: {have}", size=12, color="#16a34a"),
                    ft.Text(f"Нужно докупить: {missing}", size=12, color="#6B7280"),
                    btn_row,
                ],
                spacing=10,
            ),
        )

    # ---------- пагинация ----------
    def _render_page(self, initial: bool = False):
        self.cards_column.controls.clear()

        total = len(self.items)
        if total == 0:
            self.cards_column.controls.append(
                ft.Container(
                    bgcolor="white", border=ft.border.all(1, "#E5E6EB"),
                    border_radius=14, padding=16,
                    content=ft.Text(
                        "Пока нет подходящих рецептов. Добавь продукты или рецепты.",
                        size=14, color="#555"),
                )
            )
            self.page_label.value = "1 / 1"
            self.prev_btn.disabled = True
            self.next_btn.disabled = True
        else:
            self.total_pages = max(1, math.ceil(total / self.PAGE_SIZE))
            self.page_index = max(0, min(self.page_index, self.total_pages - 1))

            start = self.page_index * self.PAGE_SIZE
            end = start + self.PAGE_SIZE
            for sug in self.items[start:end]:
                self.cards_column.controls.append(self._recipe_card(sug))

            self.page_label.value = f"{self.page_index + 1} / {self.total_pages}"
            self.prev_btn.disabled = (self.page_index == 0)
            self.next_btn.disabled = (self.page_index >= self.total_pages - 1)

        # В init() обновлять нельзя — контрол ещё не на странице
        if not initial:
            self.cards_column.update()
            self.page_label.update()
            self.prev_btn.update()
            self.next_btn.update()

    def _prev_page(self, e):
        if self.page_index > 0:
            self.page_index -= 1
            self._render_page(initial=False)

    def _next_page(self, e):
        if self.page_index < self.total_pages - 1:
            self.page_index += 1
            self._render_page(initial=False)
