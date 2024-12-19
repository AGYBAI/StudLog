import flet as ft
from Pages.utils import t

def open_telegram_bot(e):
    # TODO: Replace 'your_bot_username' with your actual Telegram bot username
    import webbrowser
    webbrowser.open('https://t.me/your_bot_username')

def support_screen(page: ft.Page):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    t("support"),
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20),
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    name=ft.icons.TELEGRAM,
                                    color=ft.colors.WHITE,
                                    size=24,
                                ),
                                ft.Text(
                                    t("contact_support"),
                                    color=ft.colors.WHITE,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        bgcolor=ft.colors.BLUE_600,
                        height=50,
                        width=300,
                        on_click=open_telegram_bot,
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
        bgcolor=ft.colors.WHITE if page.theme_mode == "light" else ft.colors.GREY_900,
    )