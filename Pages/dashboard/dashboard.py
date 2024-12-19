import flet as ft
import sys
import os

from Pages.dashboard.support_screen import support_screen

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from Pages.dashboard.settings_screen import settings_screen
from Pages.authentication.auth_screens import auth_screen, main, save_session
from Pages.dashboard.analytics_screen import analytics_screen
from Pages.dashboard.students_screen import students_screen
from Pages.utils import language_selector
from Pages.utils import t, change_language

content = ft.Column(
        controls=[],
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )
login_view = ft.View(
        route="/auth_screen",
        controls=[]  # Создаем пустую страницу
    )

def dashboard_screen(page: ft.Page):
    page.title = "StudLog"
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.resizable = False
    page.window.maximized = True
    page.padding = ft.padding.all(0)
    page.bgcolor = ft.Colors.WHITE


    def change_screen(e):
        selected_index = rail.selected_index
        update_content(selected_index)

    def update_content(selected_index):
        content.controls.clear()
        if selected_index == 0:
            content.controls.append(students_screen(page))
        elif selected_index == 1:
            content.controls.append(analytics_screen(page))
        elif selected_index == 2:
            content.controls.append(settings_screen(page))
        elif selected_index == 3:
            content.controls.append(support_screen(page))
        page.update()

    # Define language change handler
    def on_language_change():
        update_content(rail.selected_index)

    # Attach language change handler to page
    page.on_language_change = on_language_change

    def create_rail_destination(icon, selected_icon, label):
        return ft.NavigationRailDestination(
            icon=ft.Icon(icon, size=24),
            selected_icon=selected_icon,
            label=label,
        )

    rail = ft.NavigationRail(
        bgcolor=ft.Colors.GREY_200,
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=300,
        min_extended_width=300,
        leading=ft.Column(
            controls=[
                ft.Image(
                    src="/Users/gibatolla/Documents/Практика/StudLog/assets/logo.png",
                    width=200,
                    height=200,
                ),
                ft.Divider(thickness=1, color=ft.Colors.BLACK),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        group_alignment=-0.9,
        trailing=ft.Column(
            controls=[
                ft.Divider(thickness=1, color=ft.Colors.BLACK),
                ft.Row(
                    spacing=10,
                ),
                ft.Divider(thickness=1, color=ft.Colors.BLACK),
                ft.ElevatedButton(
                    text=t("logout"),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: logout(page),  # Передаём page в функцию
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        destinations=[
            create_rail_destination(ft.icons.HOME_OUTLINED, ft.icons.HOME, t("main")),
            create_rail_destination(ft.icons.ANALYTICS_OUTLINED, ft.icons.ANALYTICS, t("analytics")),
            create_rail_destination(ft.icons.SETTINGS_OUTLINED, ft.icons.SETTINGS, t("settings")),
            create_rail_destination(ft.icons.CONTACT_SUPPORT_OUTLINED, ft.icons.CONTACT_SUPPORT, t("support")),
        ],
        on_change=change_screen,
    )

    # Store references to main content and nav rail for theme toggling
    page.main_content = content
    page.nav_rail = rail
    
    def update_container_theme():
        main_container.bgcolor = ft.colors.WHITE if page.theme_mode == "light" else ft.colors.GREY_900
        main_container.border = ft.border.all(
            1, 
            ft.colors.GREY_300 if page.theme_mode == "light" else ft.colors.GREY_700
        )
        page.update()

    # Store the update_container_theme function on the page object
    page.update_container_theme = update_container_theme
    
    main_container = ft.Container(
        content=content,
        expand=True,
        bgcolor=ft.colors.WHITE if page.theme_mode == "light" else ft.colors.GREY_900,
        padding=ft.padding.all(16),
        border_radius=ft.border_radius.all(12),
        border=ft.border.all(
            1, 
            ft.colors.GREY_300 if page.theme_mode == "light" else ft.colors.GREY_700
        ),
    )

    page.views[-1].controls.append(
        ft.Row(
            controls=[
                rail,
                main_container,
            ],
            expand=True,
        )
    )

    # Add this line to initialize the students screen immediately
    update_content(0)
    page.update()


def logout(page: ft.Page):
    from Pages.authentication.auth_screens import auth_screen

    # Закрытие текущей сессии
    save_session(False, "")
    page.views.clear()  # Удаляем все представления
    auth_view = auth_screen(page)  # Получаем представление экрана авторизации
    page.views.append(auth_view)  # Добавляем экран авторизации в список представлений
    page.go("/auth_screen")  # Переходим к маршруту авторизации

