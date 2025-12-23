import flet as ft
from datetime import datetime, date, timedelta
import sys, os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from products_db import init_products_db, list_products
from ui.layout import page_layout
from ui.colors import PILL, STAT_BORDER

def clock_badge() -> ft.Container:
    now = datetime.now()
    return ft.Container(
        width=120,
        height=66,
        bgcolor="#1E1E1E",
        border_radius=12,
        padding=10,
        content=ft.Column(
            [
                ft.Text(now.strftime("%H:%M"), size=18, color="white", weight="bold"),
                ft.Text(now.strftime("%d.%m.%Y"), size=12, color="white"),
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

class HomeView(ft.Container):
    def __init__(self, page: ft.Page):
        init_products_db()
        self.page = page
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        surface = "#171B26" if is_dark else "white"
        border = "#2A3042" if is_dark else STAT_BORDER
        text_primary = "#E9ECF5" if is_dark else "#111827"
        text_muted = "#AAB2C8" if is_dark else "#6B7280"
        self._add_btn = ft.ElevatedButton(
            "Добавить продукт",
            icon=ft.Icons.ADD,
            bgcolor="white",
            color="#4F46E5",
            height=40,
            visible=False,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=999),
                elevation=2,
                padding=ft.padding.symmetric(horizontal=18, vertical=0),
            ),
            on_click=lambda _: page.go("/add"),
        )
        def pill_hover(e: ft.HoverEvent):
            e.control.opacity = 0.95 if e.data == "true" else 1.0
            page.update()
        card_body = ft.Container(
            width=260,
            height=380,
            bgcolor=PILL,
            border_radius=18,
            padding=18,
            on_click=lambda _: page.go("/add"),
            on_hover=pill_hover,
            content=ft.Column(
                [
                    ft.Text(
                        "Добавьте\nв свой\nсписок\nновые\nпродукты!",
                        size=25,
                        weight="w700",
                        color="white",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
        btn_overlay = ft.Container(
            width=260,
            height=380,
            bgcolor="transparent",
            alignment=ft.alignment.center,
            content=self._add_btn,
        )
        add_stack = ft.Stack([card_body, btn_overlay])
        def on_add_hover(e: ft.HoverEvent):
            self._add_btn.visible = (e.data == "true")
            page.update()
        add_card = ft.Container(content=add_stack, on_hover=on_add_hover)
        self.expiring_left = ft.Column(spacing=6, expand=True)
        self.expiring_right = ft.Column(spacing=6, expand=True)
        self.expiring_list = ft.Row(
            [self.expiring_left, self.expiring_right],
            spacing=24,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        expiring = ft.Container(
            height=240,
            bgcolor=PILL,
            border_radius=40,
            padding=20,
            expand=True,
            on_click=lambda _: page.go("/search"),
            content=ft.Column(
                [
                    ft.Text("Скоро истечет срок годности:", size=25, weight="w700", color="white"),
                    ft.Container(height=10),
                    self.expiring_list,
                ],
                expand=True,
            ),
        )

        #Статистика
        self.total_text = ft.Text("—", size=16, weight="w600", color=text_primary)
        self.expired_text = ft.Text("—", size=16, weight="w600", color=text_primary)
        def stat_box(title: str, value_control: ft.Control):
            return ft.Container(
                width=260,
                height=92,
                bgcolor=surface,
                border=ft.border.all(3, border),
                border_radius=12,
                padding=12,
                content=ft.Column(
                    [ft.Text(title, size=13, color=text_muted), value_control],
                    spacing=6,
                ),
            )
        stats_row = ft.Row(
            [
                stat_box("Всего продуктов:", self.total_text),
                stat_box("Просрочено:", self.expired_text),
            ],
            spacing=20,
        )

        #то, что справа
        body = ft.Stack(
            expand=True,
            controls=[
                ft.Column(
                    [
                        ft.Row(
                            [
                                add_card,
                                ft.Container(width=22),
                                ft.Column(
                                    [expiring, ft.Container(height=18), stats_row, ft.Container(expand=True)],
                                    expand=True,
                                ),
                            ],
                            expand=True,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.Container(
                    alignment=ft.alignment.bottom_right,
                    padding=ft.padding.only(right=20, bottom=20),
                    content=clock_badge(),
                ),
            ],
        )
        super().__init__(
            expand=True,
            bgcolor=page.bgcolor,
            content=page_layout(page, "Welcome back.\nUser", body),
        )
        self._load_stats_and_expiring(initial=True)
    #Подсчёт и заполнение
    def _parse_date(self, s: str):
        s = (s or "").strip()
        try:
            return datetime.strptime(s, "%d.%m.%Y").date()
        except Exception:
            return None
    def _load_stats_and_expiring(self, initial: bool = False):
        items = list_products(limit=2000)
        today = date.today()
        soon_limit = today + timedelta(days=3)
        total = len(items)
        expired = 0
        soon = []
        for p in items:
            d = self._parse_date(p.get("exp_date"))
            if not d:
                continue
            if d < today:
                expired += 1
            elif today <= d <= soon_limit:
                soon.append((p.get("name") or "—", p.get("exp_date") or ""))
        self.total_text.value = str(total)
        self.expired_text.value = str(expired)
        self.expiring_left.controls.clear()
        self.expiring_right.controls.clear()
        sorted_soon = sorted(soon, key=lambda x: self._parse_date(x[1]) or date.max)
        MAX_PER_COL = 4
        if not sorted_soon:
            self.expiring_left.controls.append(
                ft.Text("Нет товаров с истекающим сроком", color="white", size=14)
            )
        else:
            shown = sorted_soon[: MAX_PER_COL * 2]
            for i, (name, ds) in enumerate(shown):
                item = ft.Row(
                    [
                        ft.Icon(ft.Icons.WARNING_AMBER, color="white"),
                        ft.Text(f"{name} — до {ds}", color="white", size=14),
                    ],
                    spacing=8,
                )
                (self.expiring_left if i < MAX_PER_COL else self.expiring_right).controls.append(item)
            rest = len(sorted_soon) - len(shown)
            if rest > 0:
                self.expiring_right.controls.append(
                    ft.Text(f"ещё {rest}…", color="white", size=14, weight="w600")
                )
        if (not initial) and (self.page is not None):
            self.total_text.update()
            self.expired_text.update()
            self.expiring_left.update()
            self.expiring_right.update()
