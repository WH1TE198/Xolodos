import math
import flet as ft
from ui.layout import page_layout
from settings_db import get_setting
from recommend import suggest_recipes
from recipes_db import init_recipes_db, seed_demo_if_empty, seed_world_recipes, seed_more_world_recipes

# Подробные рецепты по названию блюда.
# Можно дополнять и редактировать по своему вкусу.
RECIPE_DETAILS = {
    "Салат греческий": {
        "instructions": """\
1. Подготовьте овощи.
   Огурцы вымойте, при желании очистите от кожицы и нарежьте крупными полукольцами или крупным кубиком.

2. Нарежьте помидоры.
   Помидоры вымойте и нарежьте дольками или крупными кусочками.

3. Добавьте лук и маслины.
   Красный лук нарежьте тонкими полукольцами, маслины оставьте целыми или нарежьте кружочками.

4. Подготовьте сыр.
   Сыр фета нарежьте кубиками или аккуратно разломайте руками.

5. Соберите салат.
   Смешайте в миске огурцы, помидоры, лук, маслины и сыр.

6. Заправьте.
   Полейте оливковым маслом, при желании добавьте немного лимонного сока,
   слегка посолите, поперчите и посыпьте сухим орегано.

7. Подача.
   Подавайте салат сразу, пока овощи остаются свежими и хрустящими."""
    },

    "Салат с тунцом": {
        "instructions": """\
1. Отварите яйца вкрутую (8–10 минут), охладите в холодной воде и очистите.

2. Подготовьте огурец.
   Вымойте и нарежьте его небольшими кубиками.

3. Подготовьте тунец.
   Откройте банку, слейте жидкость и разомните тунец вилкой.

4. Добавьте кукурузу.
   Слейте рассол и высыпьте зерна в миску.

5. Нарежьте яйца кубиками и добавьте к остальным ингредиентам.

6. Заправьте салат майонезом (можно смешать майонез с йогуртом),
   посолите и поперчите по вкусу, аккуратно перемешайте.

7. Подача.
   Дайте салату немного настояться в холодильнике или подавайте сразу,
   при желании посыпав его рубленой зеленью."""
    },

    "Салат с крабовыми палочками": {
        "instructions": """\
1. При необходимости разморозьте крабовые палочки и нарежьте их небольшими кубиками.

2. Отварите яйца вкрутую, охладите и нарежьте кубиками.

3. Добавьте консервированную кукурузу, слив рассол из банки.

4. При желании добавьте отварной рис и/или свежий огурец,
   нарезанный мелким кубиком.

5. Заправьте салат майонезом, посолите по вкусу и хорошо перемешайте.

6. Подача.
   Переложите салат в салатницу или разложите по порционным тарелкам,
   украсьте зеленью и подавайте к столу."""
    },
}


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

        # Инициализация БД рецептов и рекомендаций
        init_recipes_db()
        seed_demo_if_empty()
        seed_world_recipes()
        seed_more_world_recipes()

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

    # ---------- вспомогательные элементы ----------

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

    # ---------- диалог с подробным рецептом ----------

    def _open_recipe_dialog(self, recipe: dict, have: str, missing: str):
        title = recipe.get("title", "Рецепт")
        details = RECIPE_DETAILS.get(title)

        # Берём шаги из словаря, либо показываем заглушку
        if details is not None:
            instructions = details["instructions"]
        else:
            instructions = (
                "Подробный пошаговый рецепт для этого блюда пока не добавлен.\n\n"
                f"Имеющиеся продукты: {have}\n"
                f"Нужно докупить: {missing}"
            )

        time_text = (
            f"Время приготовления: {recipe['time_min']} мин"
            if recipe.get("time_min") is not None
            else "Время приготовления: —"
        )
        diff_text = f"Сложность: {recipe.get('difficulty') or '—'}"

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight="w700"),
            content=ft.Column(
                [
                    ft.Text(time_text),
                    ft.Text(diff_text),
                    ft.Divider(),
                    ft.Text(instructions, selectable=True, size=14),
                ],
                tight=True,
                scroll="auto",
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=self._close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self, e):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    # ---------- карточка рецепта ----------

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

        return ft.Container(
            bgcolor=bg,
            border=ft.border.all(1, br),
            border_radius=14,
            padding=16,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(r["title"], size=18, weight="w700", color=text_primary),
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
                                on_click=lambda e, rec=r, h=have, m=missing: self._open_recipe_dialog(
                                    rec, h, m
                                ),
                            )
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
        )

    # ---------- пагинация ----------

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
