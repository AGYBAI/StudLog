import re
import flet as ft
import os
import json
from psycopg2 import connect
import sys
import traceback

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from Pages.translations import translations
from Pages.utils import t, change_language, language_selector

# Database configuration
DB_CONFIG = {
    "dbname": "railway",
    "user": "postgres",
    "password": "dfFudMqjdNUrRDNEvvTVVvBaNztZfxaP",
    "host": "autorack.proxy.rlwy.net",
    "port": "33741"
}

# Session file path 
SESSION_FILE = "session.json"

def connect_to_db():
    try:
        return connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

def is_user_logged_in():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as file:
                session = json.load(file)
                return session.get("is_logged_in", False)
        except Exception as e:
            print(f"Error reading session file: {str(e)}")
    return False

def save_session(is_logged_in, email="", role="student"):
    try:
        with open(SESSION_FILE, "w") as file:
            json.dump({
                "is_logged_in": is_logged_in, 
                "user_email": email,
                "role": role
            }, file)
    except Exception as e:
        print(f"Error saving session: {str(e)}")

def auth_screen(page: ft.Page):
    
    button_border_radius = 8

    def validate_email(email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def email_change(e, field):
        if validate_email(e.control.value):
            field.error_text = None
            field.border_color = "green"
        else:
            field.error_text = t("invalid_email")
            field.border_color = "red"
        field.update()
    
    def on_login_password_change(e):
        password = e.control.value
        if len(password) < 8:
            login_password_field.error_text = t("password_min_length")
            login_password_field.border_color = "red"
        elif not any(char.isupper() for char in password):
            login_password_field.error_text = t("password_uppercase")
            login_password_field.border_color = "red"
        elif not any(char.islower() for char in password):
            login_password_field.error_text = t("password_lowercase")
            login_password_field.border_color = "red"
        elif not any(char.isdigit() for char in password):
            login_password_field.error_text = t("password_digit")
            login_password_field.border_color = "red"
        elif not any(char in "!@#$%^&*()~" for char in password):
            login_password_field.error_text = t("password_special")
            login_password_field.border_color = "red"
        else:
            login_password_field.error_text = None
            login_password_field.border_color = "green"
        login_password_field.update()

    def on_login(e: ft.ControlEvent):
        if not validate_email(login_email_field.value):
            page.snack_bar = ft.SnackBar(
                ft.Text(t("fix_errors"), color="red"), open=True
            )
            page.update()
            return

        if not login_email_field.value or not login_password_field.value:
            page.snack_bar = ft.SnackBar(
                ft.Text(t("fill_all_fields"), color="red"), open=True
            )
            page.update()
            return

        try:
            conn = connect_to_db()
            if not conn:
                page.snack_bar = ft.SnackBar(
                    ft.Text(t("connection_error"), color="red"), open=True
                )
                page.update()
                return
                
            cur = conn.cursor()
            
            print(f"DEBUG - Attempting login for email: {login_email_field.value}")
            
            # Simplify the login query
            cur.execute("""
                SELECT id, email, role 
                FROM users 
                WHERE LOWER(email) = LOWER(%s) 
                AND password = crypt(%s, password);
            """, (login_email_field.value, login_password_field.value))
            
            user = cur.fetchone()
            
            if user:
                user_id, email, role = user
                print(f"DEBUG - Login successful for user: {email}, role: {role}")
                
                page.snack_bar = ft.SnackBar(ft.Text(t("login_success"), color="green"), open=True)
                save_session(True, email, role)
                
                try:
                    # Clear views and navigate to dashboard
                    page.views.clear()
                    
                    from Pages.dashboard.dashboard import dashboard_screen
                    dash_view = ft.View(
                        route="/dashboard",
                        controls=[]
                    )
                    page.views.append(dash_view)
                    dashboard_screen(page)
                    page.go("/dashboard")
                except Exception as nav_error:
                    print(f"DEBUG - Navigation error: {str(nav_error)}")
                    traceback.print_exc()
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Navigation error: {str(nav_error)}", color="red"), open=True
                    )
            else:
                # Check if user exists
                cur.execute("SELECT 1 FROM users WHERE LOWER(email) = LOWER(%s)", (login_email_field.value,))
                if cur.fetchone():
                    print(f"DEBUG - Invalid password for user: {login_email_field.value}")
                    login_password_field.error_text = t("invalid_password")
                else:
                    print(f"DEBUG - User not found: {login_email_field.value}")
                    login_email_field.error_text = t("user_not_found")
                page.update()

            cur.close()
            conn.close()

        except Exception as error:
            print(f"DEBUG - Login error: {str(error)}")
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(
                ft.Text(f"{t('login_error')}: {str(error)}", color="red"), open=True
            )
        finally:
            page.update()
    
    def go_to_register(e):
        from Pages.authentication.register_screen import register_screen
        register_view = register_screen(page)
        page.views.clear()
        page.views.append(register_view)
        page.go("/register")
        page.update()

    login_email_field = ft.TextField(
        label=t("email"), 
        hint_text="example@gmail.com",
        text_vertical_align=-0.30,
        border=ft.InputBorder.OUTLINE,
        border_width=1,
        on_change=lambda e: email_change(e, login_email_field),
    )
    page.update()

    login_password_field = ft.TextField(
        label=t("password"), 
        hint_text=t("type_password"),
        text_vertical_align=-0.30,
        border=ft.InputBorder.OUTLINE,
        border_width=1,
        password=True,
        on_change=on_login_password_change
    )
    page.update()

    # Get the absolute path to the assets directory
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../assets"))
    logo_path = os.path.join(assets_dir, "logo.png")

    login_view = ft.View(
        route="/auth_screen",
        controls=[
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.WHITE,
                border_radius=0,
                padding=ft.padding.all(0),
                content=ft.Column(
                    controls=[
                        # Add language selector
                        ft.Row(
                            controls=[
                                language_selector(page),
                            ],
                            alignment=ft.MainAxisAlignment.END,  
                        ),
                        ft.Container(
                            bgcolor=ft.Colors.WHITE,
                            border_radius=10,
                            width=550,
                            height=650,
                            padding=ft.padding.all(10),
                            content=ft.Column(
                                controls=[
                                    ft.Image(
                                            src=logo_path,
                                            width=200,
                                            height=200,
                                        ),
                                    ft.Text(value=t("login"), weight="bold", size=20, color=ft.Colors.BLACK),
                                    ft.Divider(height=2, color=ft.Colors.with_opacity(0.25, ft.Colors.GREY),
                                               thickness=1),
                                    ft.Column(
                                        controls=[
                                            login_email_field,
                                            login_password_field,
                                            ft.Row(
                                                controls=[
                                                ],
                                                alignment=ft.MainAxisAlignment.CENTER,
                                            ),
                                            ft.Container(
                                                content=ft.ElevatedButton(
                                                    text=t("login"), 
                                                    color=ft.Colors.WHITE,
                                                    bgcolor=ft.Colors.BLUE_600,
                                                    width=550,
                                                    height=50,
                                                    style=ft.ButtonStyle(
                                                        shape=ft.RoundedRectangleBorder(radius=button_border_radius)
                                                    ),
                                                    on_click=on_login,
                                                ),
                                                alignment=ft.alignment.center,
                                            ),
                                            # Update register button
                                            ft.Container(
                                                content=ft.TextButton(
                                                    text=t("no_account"),
                                                    on_click=go_to_register
                                                ),
                                                alignment=ft.alignment.center,
                                            ),
                                        ],
                                        spacing=15,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                ],
                                spacing=10,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ),
                    ],
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        ],
    )
    page.update()

    return login_view

def main(page: ft.Page):
    page.theme_mode = "light"
    page.window.bgcolor = ft.Colors.WHITE
    page.title = 'StudLog'
    page.window.resizable = False
    page.window.maximized = True
    page.padding = ft.padding.all(0)
    page.bgcolor = ft.Colors.WHITE

    if is_user_logged_in():
        from Pages.dashboard.dashboard import dashboard_screen
        page.views.clear()  # Очищаем все представления
        dash_view = ft.View(route="/dashboard", controls=[])
        page.views.append(dash_view)
        dashboard_screen(page)
        page.go("/dashboard")
    else:
        from Pages.authentication.register_screen import register_screen
        page.views.clear()  # Очищаем все представления
        auth_view = auth_screen(page)
        register_view = register_screen(page)
        page.views.extend([auth_view, register_view])
        page.go("/auth_screen")
    page.update()

if __name__ == '__main__':
    ft.app(target=main)
    # # вебе
    # ft.app(target=main, view=ft.WEB_BROWSER)