import flet as ft


# Для запуска примера используйте следующую функцию:
def dashboard_screen(page: ft.Page):
    page.title = 'StudLog'
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.resizable = False
    page.window.maximized = True
    page.padding = ft.padding.all(0)
    page.bgcolor = ft.colors.WHITE
    page.add(example())

def example():
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=256,
        min_extended_width=400,
        # leading=ft.Image(src="/Users/gibatolla/Documents/Практика/StudLog/assets/logo.png", width=48, height=48),  # Замените URL на ваш путь к изображению
        leading=ft.FloatingActionButton(icon=ft.icons.CREATE, text="Add"),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.FAVORITE_BORDER,
                selected_icon=ft.icons.FAVORITE,
                label="First",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.BOOKMARK_BORDER,
                selected_icon=ft.icons.BOOKMARK,
                label="Second",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon=ft.icons.SETTINGS,
                label="Settings",
            ),
        ],
        on_change=lambda e: print("Selected destination:", e.control.selected_index),
    )

    return ft.Row(
        controls=[
            rail,
            ft.VerticalDivider(width=1),
            ft.Column(
                controls=[ft.Text("Body!")],
                alignment=ft.MainAxisAlignment.START,
                expand=True,
            ),
        ],
        expand=True,  
                )


if __name__ == "__main__":
    ft.app(target=dashboard_screen)