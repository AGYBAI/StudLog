import flet as ft

def dashboard_screen(page: ft.Page):
    page.title = 'StudLog'
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.resizable = False
    page.window.maximized = True
    page.padding = ft.padding.all(0)
    page.bgcolor = ft.colors.WHITE

    # Функция для смены контента на экране
    def change_screen(e):
        selected_index = rail.selected_index
        update_content(selected_index)

    # Функция для обновления контента на правой стороне
    def update_content(selected_index):
        content.controls.clear()  # Очистка текущего контента
        if selected_index == 0:
            content.controls.append(ft.Text("Вы на главной странице", size=20, color=ft.colors.BLACK))
        elif selected_index == 1:
            content.controls.append(ft.Text("Профиль пользователя", size=20, color=ft.colors.BLACK))
        elif selected_index == 2:
            content.controls.append(ft.Text("Статистика использования", size=20, color=ft.colors.BLACK))
        elif selected_index == 3:
            content.controls.append(ft.Text("Настройки приложения", size=20, color=ft.colors.BLACK))
        elif selected_index == 4:
            content.controls.append(ft.Text("Поддержка пользователей", size=20, color=ft.colors.BLACK))
        content.update()

    # Функция для создания пункта в NavigationRail
    def create_rail_destination(icon, selected_icon, label):
        return ft.NavigationRailDestination(
            icon=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(icon, size=24),
                        ft.Text(label, expand=True, size=16, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                ),
                expand=True,
                bgcolor=ft.colors.GREY_100,
                padding=10,
                border_radius=8,
                alignment=ft.alignment.center_left,
            ),
            selected_icon=selected_icon,
            label='',
        )

    # Создаём NavigationRail
    rail = ft.NavigationRail(
        bgcolor=ft.colors.GREY_100,
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=256,
        min_extended_width=400,
        leading=ft.Column(
            [
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
        destinations=[
            create_rail_destination(ft.icons.HOME_OUTLINED, ft.icons.HOME, "Главная"),
            create_rail_destination(ft.icons.ACCOUNT_BOX_OUTLINED, ft.icons.ACCOUNT_BOX, "Профиль"),
            create_rail_destination(ft.icons.ANALYTICS_OUTLINED, ft.icons.ANALYTICS, "Статистика"),
            create_rail_destination(ft.icons.SETTINGS_OUTLINED, ft.icons.SETTINGS, "Настройки"),
            create_rail_destination(ft.icons.CONTACT_SUPPORT_OUTLINED, ft.icons.CONTACT_SUPPORT, "Поддержка"),
        ],
        on_change=change_screen,  # Вызываем функцию при смене экрана
    )

    # Контейнер для динамического контента
    content = ft.Column(
        controls=[ft.Text("Вы на главной странице", size=20, color=ft.colors.BLACK)],
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )

    # Основной макет
    page.add(
        ft.Row(
            controls=[
                rail,  # NavigationRail остаётся на месте
                content,  # Правая часть с динамическим контентом
            ],
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=dashboard_screen)