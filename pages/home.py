# pages/home.py
import flet as ft
from datetime import datetime, date, timedelta
from ui.colors import APP_BG, HEADER_BG, BTN_BORDER, BTN_ICON, PILL, STAT_BORDER

# импорт БД продуктов
import sys, os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from products_db import init_products_db, list_products


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


def clock_badge() -> ft.Container:
    now = datetime.now()
    return ft.Container(
        width=120, height=66, bgcolor="#1E1E1E", border_radius=12, padding=10,
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

        # ===== Сайдбар: белый фон, без разделителя =====
        sidebar = ft.Container(
            width=96,
            bgcolor=APP_BG,
            padding=ft.padding.only(left=10, right=10, top=22, bottom=22),
            content=ft.Column(
                [
                    sidebar_btn(ft.Icons.HOME,     lambda _: page.go("/")),
                    sidebar_btn(ft.Icons.SEARCH,   lambda _: page.go("/search")),
                    sidebar_btn(ft.Icons.RESTAURANT_MENU, lambda _: page.go("/recipes")),
                    sidebar_btn(ft.Icons.SETTINGS, lambda _: page.go("/settings")),
                    sidebar_btn(ft.Icons.PERSON,   lambda _: page.go("/user")),
                    ft.Container(
                        margin=ft.margin.only(top=170),
                        content=sidebar_btn(ft.Icons.EXIT_TO_APP, lambda _: page.window_close()),
                    ),
                ],
                spacing=22,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        # ===== «Пилюля»: при наведении показываем кнопку поверх =====
        self._add_btn = ft.ElevatedButton(
            "Добавить продукт",
            icon=ft.Icons.ADD,
            bgcolor="white",
            color="#4F46E5",
            height=40,
            visible=False,  # скрыта по умолчанию
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=999),
                elevation=2,
                padding=ft.padding.symmetric(horizontal=18, vertical=0),
            ),
            on_click=lambda _: page.go("/add"),
        )

        # --- КЛИКАБЕЛЬНАЯ «ПИЛЮЛЯ» ---
        def pill_hover(e: ft.HoverEvent):
            # лёгкий hover-эффект: меняем прозрачность
            e.control.opacity = 0.95 if e.data == "true" else 1.0
            page.update()

        card_body = ft.Container(
            width=240,
            height=360,
            bgcolor=PILL,
            border_radius=18,
            padding=18,
            on_click=lambda _: page.go("/add"),  # ← клика по всей карточке ведёт на /add
            on_hover=pill_hover,                  # ← эффект наведения (без mouse_cursor/ink)
            content=ft.Column(
                [
                    ft.Text(
                        "Добавьте\nв свой\nсписок\nновые\nпродукты!",
                        size=25, weight="w700", color="white",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

        # кнопка поверх (по центру), показывается на hover
        btn_overlay = ft.Container(
            width=240, height=360, bgcolor="transparent",
            alignment=ft.alignment.center,
            content=self._add_btn,
        )

        add_stack = ft.Stack([card_body, btn_overlay])

        def on_add_hover(e: ft.HoverEvent):
            self._add_btn.visible = (e.data == "true")
            page.update()

        add_card = ft.Container(content=add_stack, on_hover=on_add_hover)

        # ===== Блок «Скоро истечёт срок годности» =====
        self.expiring_list = ft.Column(spacing=6, expand=True)
        expiring = ft.Container(
            height=220, bgcolor=PILL, border_radius=40, padding=20, expand=True,
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

        # ===== Статистика =====
        self.total_text = ft.Text("—", size=16, weight="w600")
        self.expired_text = ft.Text("—", size=16, weight="w600")

        def stat_box(title: str, value_control: ft.Control):
            return ft.Container(
                width=260, height=92, bgcolor="white",
                border=ft.border.all(3, STAT_BORDER), border_radius=12, padding=12,
                content=ft.Column([ft.Text(title, size=13), value_control], spacing=6),
            )

        stats_row = ft.Row(
            [stat_box("Всего продуктов:", self.total_text),
             stat_box("Просрочено:", self.expired_text)],
            spacing=20,
        )

        # ===== Правая часть =====
        right_body = ft.Stack(
            expand=True,
            controls=[
                ft.Column(
                    [
                        header_bar("Welcome Back,\nUser!"),
                        ft.Container(
                            padding=ft.padding.only(left=20, right=20, top=20),
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            add_card,                      # ← тут наша «пилюля»
                                            ft.Container(width=22),
                                            ft.Column(
                                                [expiring, ft.Container(height=18), stats_row, ft.Container(expand=True)],
                                                expand=True,
                                            ),
                                        ],
                                        expand=True,
                                    ),
                                ],
                                expand=True,
                            ),
                        ),
                    ],
                    spacing=0, expand=True,
                ),
                ft.Container(
                    alignment=ft.alignment.bottom_right,
                    padding=ft.padding.only(right=20, bottom=420),
                    content=clock_badge(),
                ),
            ],
        )

        root = ft.Row([sidebar, right_body], expand=True)
        super().__init__(bgcolor=APP_BG, width=1920, height=1080, content=root)

        # стартовая загрузка данных (без update)
        self._load_stats_and_expiring(initial=True)

    # ===== Подсчёт и заполнение =====
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

        self.expiring_list.controls.clear()
        if not soon:
            self.expiring_list.controls.append(
                ft.Text("Нет товаров с истекающим сроком", color="white", size=14)
            )
        else:
            for name, ds in sorted(soon, key=lambda x: self._parse_date(x[1]) or date.max)[:6]:
                self.expiring_list.controls.append(
                    ft.Row(
                        [ft.Icon(ft.Icons.WARNING_AMBER, color="white"),
                         ft.Text(f"{name} — до {ds}", color="white", size=14)],
                        spacing=8,
                    )
                )

        if (not initial) and (self.page is not None):
            self.total_text.update()
            self.expired_text.update()
            self.expiring_list.update()
