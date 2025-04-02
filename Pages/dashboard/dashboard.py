import flet as ft
import sys
import os

from Pages.dashboard.support_screen import support_screen

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from Pages.dashboard.settings_screen import settings_screen
from Pages.authentication.auth_screens import auth_screen, save_session
from Pages.dashboard.analytics_screen import analytics_screen
from Pages.dashboard.students_screen import students_screen
from Pages.utils import language_selector
from Pages.utils import t, change_language

content = ft.Column(
        controls=[],
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )

def dashboard_screen(page: ft.Page):
    page.title = "StudLog"
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.resizable = False
    page.window.maximized = True
    page.padding = ft.padding.all(0)
    page.bgcolor = ft.Colors.WHITE

    # Get the absolute path to the assets directory
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../assets"))
    logo_path = os.path.join(assets_dir, "logo.png")

    def change_screen(e):
        selected_index = rail.selected_index
        update_content(selected_index)

    def update_content(selected_index):
        content.controls.clear()
        try:
            if selected_index == 0:
                students_component = students_screen(page)
                content.controls.append(students_component)
            elif selected_index == 1:
                analytics_component = analytics_screen(page)
                content.controls.append(analytics_component)
            elif selected_index == 2:
                settings_component = settings_screen(page)
                content.controls.append(settings_component)
            elif selected_index == 3:
                support_component = support_screen(page)
                content.controls.append(support_component)
            page.update()
        except Exception as e:
            print(f"Error updating content: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Display error message to user
            error_message = ft.Text(
                f"Error loading content: {str(e)}",
                color=ft.Colors.RED_500,
                size=16,
                weight=ft.FontWeight.BOLD
            )
            content.controls.append(error_message)
            content.controls.append(ft.ElevatedButton("Try Again", on_click=lambda _: update_content(selected_index)))
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
                    src=logo_path,
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
        main_container.bgcolor = ft.Colors.WHITE if page.theme_mode == "light" else ft.Colors.GREY_900
        main_container.border = ft.border.all(
            1, 
            ft.Colors.GREY_300 if page.theme_mode == "light" else ft.Colors.GREY_700
        )
        page.update()

    # Store the update_container_theme function on the page object
    page.update_container_theme = update_container_theme
    
    main_container = ft.Container(
        content=content,
        expand=True,
        bgcolor=ft.Colors.WHITE if page.theme_mode == "light" else ft.Colors.GREY_900,
        padding=ft.padding.all(16),
        border_radius=ft.border_radius.all(12),
        border=ft.border.all(
            1, 
            ft.Colors.GREY_300 if page.theme_mode == "light" else ft.Colors.GREY_700
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
    try:
        # Close the current session
        save_session(False, "")
        
        # Clear all views
        page.views.clear()
        
        # Import auth_screen only when needed to avoid circular imports
        from Pages.authentication.auth_screens import auth_screen
        
        # Create new auth view
        auth_view = auth_screen(page)
        
        # Add the auth view to page views
        page.views.append(auth_view)
        
        # Navigate to auth screen
        page.go("/auth_screen")
        
        # Update the page
        page.update()
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        import traceback
        traceback.print_exc()

