import flet as ft
from Pages.utils import t

def toggle_theme(page: ft.Page, e):
    if page.theme_mode == "light":
        page.theme_mode = "dark"
        page.bgcolor = ft.colors.GREY_900
        page.window.bgcolor = ft.colors.GREY_900
        # Update navigation rail and content background
        if hasattr(page, 'main_content'):
            page.main_content.bgcolor = ft.colors.GREY_800
        if hasattr(page, 'nav_rail'):
            page.nav_rail.bgcolor = ft.colors.GREY_900
    else:
        page.theme_mode = "light"
        page.bgcolor = ft.colors.WHITE
        page.window.bgcolor = ft.colors.WHITE
        # Reset background colors
        if hasattr(page, 'main_content'):
            page.main_content.bgcolor = ft.colors.WHITE
        if hasattr(page, 'nav_rail'):
            page.nav_rail.bgcolor = ft.colors.GREY_200
    
    # Update container theme
    if hasattr(page, 'update_container_theme'):
        page.update_container_theme()
    
    page.update()

def settings_screen(page: ft.Page):
    return ft.Container(
        content=ft.Column([
            ft.Text(
                t("settings"),
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Divider(height=20),
            ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(
                            ft.icons.DARK_MODE,
                            color=ft.colors.BLUE_600,
                        ),
                        title=ft.Text(
                            t("theme_mode"),
                            color=ft.colors.BLUE_600 if page.theme_mode == "light" else ft.colors.WHITE,
                        ),
                        trailing=ft.Switch(
                            value=page.theme_mode == "dark",
                            on_change=lambda e: toggle_theme(page, e),
                            active_color=ft.colors.BLUE_600,
                        ),
                    ),
                ]),
                padding=20,
                border_radius=10,
                bgcolor=ft.colors.WHITE if page.theme_mode == "light" else ft.colors.GREY_800,
                border=ft.border.all(1, ft.colors.GREY_400),
            ),
        ]),
        padding=20,
        bgcolor=ft.colors.WHITE if page.theme_mode == "light" else ft.colors.GREY_900,
    )
