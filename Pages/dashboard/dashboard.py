import flet as ft
import sys
import os
import traceback

from Pages.dashboard.support_screen import support_screen

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from Pages.dashboard.settings_screen import settings_screen
from Pages.authentication.auth_screens import auth_screen, save_session
from Pages.dashboard.analytics_screen import analytics_screen
from Pages.dashboard.students_screen import students_screen
from Pages.utils import language_selector
from Pages.utils import t, change_language
from Pages.utils import is_admin

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
                print("Загрузка компонента students_screen...")
                students_component = students_screen(page)
                content.controls.append(students_component)
                print("Компонент students_screen добавлен в content")
            elif selected_index == 1:
                analytics_component = analytics_screen(page)
                content.controls.append(analytics_component)
            elif selected_index == 2:
                settings_component = settings_screen(page)
                content.controls.append(settings_component)
            elif selected_index == 3:
                support_component = support_screen(page)
                content.controls.append(support_component)
            
            # Убедимся, что страница обновится после добавления компонента
            page.update()
            print(f"Контент обновлен для вкладки {selected_index}")
        except Exception as e:
            print(f"Error updating content: {str(e)}")
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
        traceback.print_exc()


def create_dashboard_page(page):
    print("Creating dashboard page")
    active_tab = "home"  # Default tab
    
    def change_active_tab(e, tab):
        nonlocal active_tab
        active_tab = tab
        update_content(page, tab)
        page.update()

    # Navbar with Astana IT University logo
    logo = ft.Row(
        [
            ft.Image(
                src="/images/aitu_logo.png",
                width=120,
                height=120,
                fit=ft.ImageFit.CONTAIN,
            ),
            ft.Column(
                [
                    ft.Container(
                        ft.Text("ASTANA IT", size=20, weight=ft.FontWeight.BOLD),
                        padding=ft.padding.only(top=20),
                    ),
                    ft.Text("UNIVERSITY", size=20, weight=ft.FontWeight.BOLD),
                ],
                spacing=0,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=2,
    )

    # Navigation links
    nav_items = [
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.HOME),
                    ft.Text(t("home")),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
            padding=20,
            border_radius=8,
            bgcolor=ft.colors.BLUE_50 if active_tab == "home" else None,
            on_click=lambda e: change_active_tab(e, "home"),
            expand=True,
        ),
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.BAR_CHART),
                    ft.Text(t("analytics")),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
            padding=20,
            border_radius=8,
            bgcolor=ft.colors.BLUE_50 if active_tab == "analytics" else None,
            on_click=lambda e: change_active_tab(e, "analytics"),
            expand=True,
        ),
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.SETTINGS),
                    ft.Text(t("parameters")),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
            padding=20,
            border_radius=8,
            bgcolor=ft.colors.BLUE_50 if active_tab == "parameters" else None,
            on_click=lambda e: change_active_tab(e, "parameters"),
            expand=True,
        ),
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.QUESTION_MARK),
                    ft.Text(t("help")),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
            padding=20,
            border_radius=8,
            bgcolor=ft.colors.BLUE_50 if active_tab == "help" else None,
            on_click=lambda e: change_active_tab(e, "help"),
            expand=True,
        ),
    ]

    # Create container for content that will be updated based on active tab
    content_container = ft.Container(expand=True)
    
    def update_content(page, tab):
        try:
            print(f"Updating content for tab: {tab}")
            if tab == "home":
                content_container.content = home_screen(page)
            elif tab == "analytics":
                content_container.content = students_screen(page)
            elif tab == "parameters":
                content_container.content = parameters_screen(page)
            elif tab == "help":
                content_container.content = help_screen(page)
            
            # Важное дополнение: мы должны явно обновить страницу здесь,
            # чтобы обеспечить правильную отрисовку UserControl
            page.update()
            
        except Exception as e:
            print(f"Error updating content: {e}")
            traceback.print_exc()
            content_container.content = ft.Text(f"Error loading content: {str(e)}")

    # Sign out button
    sign_out_button = ft.ElevatedButton(
        t("logout"),
        icon=ft.icons.LOGOUT,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        on_click=lambda e: page.go("/"),
    )

    # Dashboard layout
    sidebar = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Divider(height=2, color=ft.Colors.GREY_400),
                ft.Container(height=10),  # Spacer
                ft.Column(nav_items, spacing=10),
                ft.Container(
                    content=sign_out_button,
                    padding=20,
                    alignment=ft.alignment.center,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=0,
        ),
        width=280,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.GREY_300)),
    )

    # Initialize with home screen
    def initialize_page():
        update_content(page, active_tab)
    
    # Call initialize after page is rendered
    page.on_mount = lambda _: initialize_page()

    # Main layout
    return ft.Row(
        [
            sidebar,
            ft.VerticalDivider(width=1),
            content_container,
        ],
        expand=True,
    )

def home_screen(page):
    is_admin_user = is_admin()
    
    # Welcome message
    welcome_text = ft.Text(
        "Welcome to Student Management System!",
        size=28,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.BLUE_800,
    )
    
    # Quick access cards
    students_card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.icons.PERSON, size=32, color=ft.colors.BLUE_500),
                ft.Text(t("students"), size=20, weight=ft.FontWeight.BOLD),
                ft.Text(t("manage_students"), color=ft.colors.GREY_700),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.alignment.center,
        width=200,
        height=150,
        border_radius=10,
        bgcolor=ft.colors.BLUE_50,
        ink=True,
        on_click=lambda e: change_active_tab(e, "analytics"),
    )
    
    analytics_card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.icons.BAR_CHART, size=32, color=ft.colors.GREEN_500),
                ft.Text(t("analytics"), size=20, weight=ft.FontWeight.BOLD),
                ft.Text(t("analytics_desc"), color=ft.colors.GREY_700),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.alignment.center,
        width=200,
        height=150,
        border_radius=10,
        bgcolor=ft.colors.GREEN_50,
        ink=True,
        on_click=lambda e: change_active_tab(e, "analytics"),
    )
    
    settings_card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.icons.SETTINGS, size=32, color=ft.colors.AMBER_500),
                ft.Text(t("parameters"), size=20, weight=ft.FontWeight.BOLD),
                ft.Text(t("parameters_desc"), color=ft.colors.GREY_700),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.alignment.center,
        width=200,
        height=150,
        border_radius=10,
        bgcolor=ft.colors.AMBER_50,
        ink=True,
        on_click=lambda e: change_active_tab(e, "parameters"),
    )
    
    # Card row
    cards_row = ft.Row(
        [students_card, analytics_card, settings_card],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=30,
    )
    
    # Admin panel card - only shown for admins
    admin_panel = None
    if is_admin_user:
        admin_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS, size=24, color=ft.colors.RED_500),
                            ft.Text(t("admin_panel"), size=18, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(height=2, color=ft.colors.RED_200),
                    ft.Text(t("admin_desc"), color=ft.colors.GREY_700),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                t("manage_students"),
                                icon=ft.icons.PEOPLE,
                                bgcolor=ft.colors.RED_400,
                                color=ft.colors.WHITE,
                                on_click=lambda e: change_active_tab(e, "analytics"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=10,
                width=500,
            ),
            padding=20,
            border_radius=10,
            bgcolor=ft.colors.RED_50,
            border=ft.border.all(1, ft.colors.RED_200),
            margin=ft.margin.only(top=40),
        )
    
    def change_active_tab(e, tab):
        # This function needs to be defined in the local scope to access the page
        page.session.set("active_tab", tab)
        update_dashboard_content(page)
    
    def update_dashboard_content(page):
        # Refresh the dashboard with the new active tab
        page.controls.clear()
        page.add(create_dashboard_page(page))
        page.update()
    
    # Create the homepage content
    content_components = [
        welcome_text,
        ft.Container(height=40),
        cards_row,
    ]
    
    # Add admin panel if user is admin
    if admin_panel:
        content_components.append(admin_panel)
    
    # Return the homepage content
    return ft.Container(
        content=ft.Column(
            content_components,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        padding=40,
        expand=True,
    )

def parameters_screen(page):
    return ft.Text("Параметры")

def help_screen(page):
    return ft.Text("Справка")

