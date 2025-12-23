import math
import flet as ft
from ui.layout import page_layout
from settings_db import get_setting
from recommend import suggest_recipes
from recipes_db import (
    init_recipes_db,
    seed_demo_if_empty,
    seed_world_recipes,
    seed_more_world_recipes,
    get_all_recipes,
)


class RecipesView(ft.Container):
    PAGE_SIZE = 3

    def __init__(self, page: ft.Page):
        self.page = page

        rec_enabled = get_setting("recommend_recipes", "1") != "0"
        if not rec_enabled:
            body = ft.Column(
                [
                    ft.Text("Рекомендации рецептов выключены", size=18, weight="w700"),
                    ft.Text("Включи их в настройках, чтобы видеть подборки.", size=13),
                    ft.Container(height=12),
                    ft.ElevatedButton(
                        "Перейти в настройки",
                        icon=ft.Icons.SETTINGS,
                        on_click=lambda _: page.go("/settings"),
                    ),
                    ft.Container(expand=True),
                ],
                spacing=10,
                expand=True,
            )
            super().__init__(
                expand=True,
                bgcolor=page.bgcolor,
                content=page_layout(page, "Рецепты", body),
            )
            return

        init_recipes_db()
        seed_demo_if_empty()
        seed_world_recipes()
        seed_more_world_recipes()
        all_recipes = get_all_recipes()
        self.recipes_by_title = {r["title"].strip().lower(): r for r in all_recipes}
        self.items: list[dict] = suggest_recipes(top_n=500)
        self.page_index: int = 0
        self.total_pages: int = max(1, math.ceil(len(self.items) / self.PAGE_SIZE))

        self.title_text = ft.Text("Рецепты из того, что есть", size=20, weight="w700")
        self.cards_column = ft.Column(spacing=14)

        self.prev_btn = ft.OutlinedButton("Назад", icon=ft.Icons.CHEVRON_LEFT, on_click=self._prev_page)
        self.next_btn = ft.OutlinedButton("Следующая", icon=ft.Icons.CHEVRON_RIGHT, on_click=self._next_page)
        self.page_label = ft.Text("", size=13, color="#6B7280")

        pager = ft.Row(
            [self.prev_btn, self.page_label, self.next_btn],
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self._render_page(initial=True)

        body = ft.Column(
            [self.title_text, self.cards_column, ft.Container(height=8), pager],
            spacing=14,
            expand=True,
        )

        super().__init__(
            expand=True,
            bgcolor=page.bgcolor,
            content=page_layout(page, "Рецепты", body),
        )

    def _pill(self, text: str):
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        bg = "#222B3F" if is_dark else "#F3F4F6"
        br = "#32405A" if is_dark else "#E5E7EB"
        col = "#E9ECF5" if is_dark else "#111827"
        return ft.Container(
            bgcolor=bg,
            border=ft.border.all(1, br),
            border_radius=999,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            content=ft.Text(text, size=12, color=col),
        )

    def _close_dialog(self, e):
        if getattr(self.page, "dialog", None):
            self.page.dialog.open = False
        self.page.update()

    def _format_ingredients(self, ingredients: list[dict]) -> str:
        if not ingredients:
            return "—"
        lines = []
        for ing in ingredients:
            name = ing.get("name") or "—"
            qty = ing.get("qty")
            unit = ing.get("unit") or ""
            if qty is None:
                lines.append(f"• {name}")
            else:
                # 50.0 -> 50
                if isinstance(qty, (int, float)) and float(qty).is_integer():
                    qty_str = str(int(qty))
                else:
                    qty_str = str(qty)
                lines.append(f"• {name} — {qty_str} {unit}".strip())
        return "\n".join(lines)

    def _open_recipe_dialog(self, title: str, have: str, missing: str):
        key = (title or "").strip().lower()
        full = self.recipes_by_title.get(key)

        if full is None:
            dialog_title = title or "Рецепт"
            ingredients_text = f"Есть: {have}\nНужно докупить: {missing}"
            steps_text = "Подробный рецепт не найден в базе (проверь совпадение названий)."
            time_text = "Время приготовления: —"
            diff_text = "Сложность: —"
        else:
            dialog_title = full.get("title", title)
            ingredients_text = self._format_ingredients(full.get("ingredients") or [])
            steps_text = (full.get("steps") or "").strip() or "Пошаговое описание пока не заполнено."
            tm = full.get("time_min")
            time_text = f"Время приготовления: {tm} мин" if tm is not None else "Время приготовления: —"
            diff_text = f"Сложность: {full.get('difficulty') or '—'}"

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(dialog_title, weight="w700"),
            content=ft.Container(
                width=520,
                height=460,
                content=ft.Column(
                    [
                        ft.Text(time_text),
                        ft.Text(diff_text),
                        ft.Divider(),
                        ft.Text("Ингредиенты:", weight="w700"),
                        ft.Text(ingredients_text, selectable=True),
                        ft.Divider(),
                        ft.Text("Приготовление:", weight="w700"),
                        ft.Text(steps_text, selectable=True, size=14),
                    ],
                    spacing=10,
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[ft.TextButton("Закрыть", on_click=self._close_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if dialog not in self.page.overlay:
            self.page.overlay.append(dialog)

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _recipe_card(self, sug: dict) -> ft.Container:
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        bg = "#171B26" if is_dark else "white"
        br = "#2A3042" if is_dark else "#E5E6EB"
        text_primary = "#E9ECF5" if is_dark else "#111827"
        text_muted = "#AAB2C8" if is_dark else "#6B7280"

        r = sug["recipe"]

        have = ", ".join([i.get("name") or "—" for i in sug.get("have", [])]) or "—"
        missing = ", ".join([i.get("name") or "—" for i in sug.get("missing", [])]) or "—"

        meta = []
        if r.get("time_min") is not None:
            meta.append(self._pill(f"{r['time_min']} мин"))
        if r.get("difficulty"):
            meta.append(self._pill(r["difficulty"]))

        title = r.get("title", "Рецепт")

        return ft.Container(
            bgcolor=bg,
            border=ft.border.all(1, br),
            border_radius=14,
            padding=16,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(title, size=18, weight="w700", color=text_primary),
                            ft.Container(expand=True),
                            *meta,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(f"Есть: {have}", size=12, color="#16a34a"),
                    ft.Text(f"Нужно докупить: {missing}", size=12, color=text_muted),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Готовлю",
                                icon=ft.Icons.RESTAURANT,
                                on_click=lambda e, t=title, h=have, m=missing: self._open_recipe_dialog(t, h, m),
                            )
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
        )

    def _render_page(self, initial: bool = False):
        self.cards_column.controls.clear()

        total = len(self.items)
        self.total_pages = max(1, math.ceil(total / self.PAGE_SIZE))
        self.page_index = max(0, min(self.page_index, self.total_pages - 1))

        if total == 0:
            is_dark = self.page.theme_mode == ft.ThemeMode.DARK
            bg = "#171B26" if is_dark else "white"
            br = "#2A3042" if is_dark else "#E5E6EB"
            col = "#AAB2C8" if is_dark else "#555"

            self.cards_column.controls.append(
                ft.Container(
                    bgcolor=bg,
                    border=ft.border.all(1, br),
                    border_radius=14,
                    padding=16,
                    content=ft.Text(
                        "Пока нет подходящих рецептов. Добавь продукты или рецепты.",
                        size=14,
                        color=col,
                    ),
                )
            )
            self.page_label.value = "1 / 1"
            self.prev_btn.disabled = True
            self.next_btn.disabled = True
        else:
            start = self.page_index * self.PAGE_SIZE
            end = start + self.PAGE_SIZE
            for sug in self.items[start:end]:
                self.cards_column.controls.append(self._recipe_card(sug))

            self.page_label.value = f"{self.page_index + 1} / {self.total_pages}"
            self.prev_btn.disabled = self.page_index == 0
            self.next_btn.disabled = self.page_index >= self.total_pages - 1

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
