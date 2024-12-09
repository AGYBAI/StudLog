import flet as ft
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from Pages.dashboard.profile_screen import profile_screen
from Pages.dashboard.students_screen import students_screen

# def dashboard_screen(page: ft.Page):
#     page.views[-1].controls.append(
#         ft.Row(
#             controls=[
#                 ft.Text("Добро пожаловать в StudLog!"),
#                 # Добавьте остальные элементы интерфейса
#             ]
#         )
#     )
#     page.update()

def dashboard_screen(page: ft.Page):
    page.title = "StudLog"
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.resizable = False
    page.window.maximized = True
    page.padding = ft.padding.all(0)
    page.bgcolor = ft.colors.WHITE

    def change_screen(e):
        selected_index = rail.selected_index
        update_content(selected_index)

    def update_content(selected_index):
        content.controls.clear()
        if selected_index == 0:
            content.controls.append(students_screen())
        elif selected_index == 1:
            content.controls.append(profile_screen())
        elif selected_index == 2:
            content.controls.append(ft.Text("Статистика использования", size=20, color=ft.colors.BLACK))
        elif selected_index == 3:
            content.controls.append(ft.Text("Настройки приложения", size=20, color=ft.colors.BLACK))
        elif selected_index == 4:
            content.controls.append(ft.Text("Поддержка пользователей", size=20, color=ft.colors.BLACK))
        content.update()

    def create_rail_destination(icon, selected_icon, label):
        return ft.NavigationRailDestination(
            icon=ft.Icon(icon, size=24),
            selected_icon=selected_icon,
            label=label,
        )

    rail = ft.NavigationRail(
        bgcolor=ft.colors.GREY_200,
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
                ft.Divider(thickness=1, color=ft.colors.BLACK),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        group_alignment=-0.9,
        trailing=ft.Column(
            controls=[
                ft.Divider(thickness=1, color=ft.colors.BLACK),
                ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text("ДК"),
                            radius=40,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Данияр Канатов", weight=ft.FontWeight.BOLD),
                                ft.Text("example@gmail.com", size=12)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Divider(thickness=1, color=ft.colors.BLACK),
                ft.ElevatedButton(
                    text="Выйти",
                    bgcolor=ft.colors.RED,
                    color=ft.colors.WHITE,
                    on_click=lambda e: page.go("/")  # Возврат на экран авторизации
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        destinations=[
            create_rail_destination(ft.icons.HOME_OUTLINED, ft.icons.HOME, "Главная"),
            create_rail_destination(ft.icons.ACCOUNT_BOX_OUTLINED, ft.icons.ACCOUNT_BOX, "Профиль"),
            create_rail_destination(ft.icons.ANALYTICS_OUTLINED, ft.icons.ANALYTICS, "Статистика"),
            create_rail_destination(ft.icons.SETTINGS_OUTLINED, ft.icons.SETTINGS, "Настройки"),
            create_rail_destination(ft.icons.CONTACT_SUPPORT_OUTLINED, ft.icons.CONTACT_SUPPORT, "Поддержка"),
        ],
        on_change=change_screen,
    )

    content = ft.Column(
        controls=[students_screen()],
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )

    page.views[1].controls.append(
        ft.Row(
            controls=[
                rail,
                ft.Container(
                    content,
                    expand=True,
                    bgcolor=ft.colors.WHITE,
                    padding=ft.padding.all(16),
                    border_radius=ft.border_radius.all(12),
                ),
            ],
            expand=True,
        )

    )
    page.update()