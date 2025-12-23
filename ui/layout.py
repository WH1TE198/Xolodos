import flet as ft

def _is_dark(page: ft.Page) -> bool:
    return page.theme_mode == ft.ThemeMode.DARK

def _palette(page: ft.Page) -> dict:
    dark = _is_dark(page)
    return {
        "sidebar_bg": "#121624" if dark else "#FFFFFF",
        "header_bg":  "#2B2F3A" if dark else "#3A4050",
        "card_bg":    "#1B2233" if dark else "#FFFFFF",
        "border":     "#2A3042" if dark else "#E3E6EF",
        "icon":       "#E9ECF5" if dark else "#3A4050",
    }

def sidebar_btn(page: ft.Page, icon, on_click):
    p = _palette(page)
    return ft.Container(
        width=76,
        height=60,
        bgcolor=p["card_bg"],
        border=ft.border.all(1, p["border"]),
        border_radius=14,
        padding=12,
        on_click=on_click,
        content=ft.Icon(icon, size=26, color=p["icon"]),
    )

def header_bar(page: ft.Page, text: str) -> ft.Container:
    p = _palette(page)
    return ft.Container(
        bgcolor=p["header_bg"],
        height=96,
        alignment=ft.alignment.center_left,
        padding=ft.padding.only(left=18, right=18, top=14, bottom=14),
        content=ft.Text(text, size=24, color="white", weight="bold"),
    )

def page_layout(page: ft.Page, title: str, content: ft.Control) -> ft.Row:
    p = _palette(page)

    top_btns = ft.Column(
        [
            sidebar_btn(page, ft.Icons.HOME,            lambda _: page.go("/home")),
            sidebar_btn(page, ft.Icons.SEARCH,          lambda _: page.go("/search")),
            sidebar_btn(page, ft.Icons.RESTAURANT_MENU, lambda _: page.go("/recipes")),
            sidebar_btn(page, ft.Icons.SETTINGS,        lambda _: page.go("/settings")),
            sidebar_btn(page, ft.Icons.PERSON,          lambda _: page.go("/user")),
        ],
        spacing=22,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    sidebar = ft.Container(
        width=96,
        bgcolor=p["sidebar_bg"],
        padding=ft.padding.only(left=10, right=10, top=22, bottom=22),
        content=ft.Column(
            [top_btns],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
    )

    right = ft.Column(
        [
            header_bar(page, title),
            ft.Container(expand=True, padding=ft.padding.all(20), content=content),
        ],
        spacing=0,
        expand=True,
    )

    return ft.Row([sidebar, right], expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH)

def scaffold(page: ft.Page, title: str, content: ft.Control) -> ft.Row:
    return page_layout(page, title, content)
