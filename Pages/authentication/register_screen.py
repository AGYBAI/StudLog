import flet as ft
import re
from psycopg2 import connect
import sys
import os
import traceback

# Add parent directory to Python path
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

def connect_to_db():
    try:
        return connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

def register_screen(page: ft.Page):
    def validate_email(email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def validate_password(password):
        if len(password) < 8:
            return t("password_min_length")
        if not any(char.isupper() for char in password):
            return t("password_uppercase")
        if not any(char.islower() for char in password):
            return t("password_lowercase")
        if not any(char.isdigit() for char in password):
            return t("password_digit")
        if not any(char in "!@#$%^&*()~" for char in password):
            return t("password_special")
        return None

    def on_register(e):
        error = False
        
        # Validate email
        if not validate_email(email_field.value):
            email_field.error_text = t("invalid_email")
            error = True
            
        # Validate password
        password_error = validate_password(password_field.value)
        if password_error:
            password_field.error_text = password_error
            error = True
            
        # Check if passwords match
        if password_field.value != confirm_password_field.value:
            confirm_password_field.error_text = t("passwords_dont_match")
            error = True
            
        # Validate full name
        if not full_name_field.value or len(full_name_field.value.split()) < 2:
            full_name_field.error_text = t("enter_full_name")
            error = True

        if error:
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
            
            # Check if email exists
            cur.execute("""
                SELECT 1 FROM users WHERE LOWER(email) = LOWER(%s)
            """, (email_field.value,))
            
            if cur.fetchone():
                email_field.error_text = t("email_already_registered")
                page.update()
                return

            # Insert new user with standardized password hashing
            cur.execute("""
                INSERT INTO users (email, password, full_name, role)
                VALUES (
                    LOWER(%s), 
                    crypt(%s, gen_salt('bf')),
                    %s, 
                    %s
                ) RETURNING id, email;
            """, (
                email_field.value,
                password_field.value,
                full_name_field.value,
                role_dropdown.value
            ))
            
            new_user = cur.fetchone()
            print(f"DEBUG - New user registered: ID={new_user[0]}, Email={new_user[1]}")

            conn.commit()
            
            # Show success message and redirect
            page.snack_bar = ft.SnackBar(
                content=ft.Text(t("registration_success"), color="green"),
                open=True
            )
            
            try:
                # Clear views and redirect to login
                page.views.clear()
                from Pages.authentication.auth_screens import auth_screen
                auth_view = auth_screen(page)
                page.views.append(auth_view)
                page.go("/auth_screen")
            except Exception as nav_error:
                print(f"DEBUG - Navigation error: {str(nav_error)}")
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Navigation error: {str(nav_error)}", color="red"),
                    open=True
                )
            
        except Exception as error:
            print(f"DEBUG - Registration error: {str(error)}")
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{t('registration_error')}: {str(error)}", color="red"),
                open=True
            )
        finally:
            if conn:
                conn.close()
            page.update()

    def go_to_login(e):
        try:
            from Pages.authentication.auth_screens import auth_screen
            auth_view = auth_screen(page)
            page.views.clear()
            page.views.append(auth_view)
            page.go("/auth_screen")
            page.update()
        except Exception as nav_error:
            print(f"DEBUG - Navigation error: {str(nav_error)}")
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Navigation error: {str(nav_error)}", color="red"),
                open=True
            )
            page.update()

    button_border_radius = 8  # Такой же как в auth_screen

    # Обновляем стили полей ввода для соответствия auth_screen
    email_field = ft.TextField(
        label=t("email"),
        hint_text="example@gmail.com",
        text_vertical_align=-0.30,
        border=ft.InputBorder.OUTLINE,
        border_width=1,
        width=550,  # Увеличиваем ширину как в auth_screen
    )

    password_field = ft.TextField(
        label=t("password"),
        hint_text=t("type_password"),
        text_vertical_align=-0.30,
        border=ft.InputBorder.OUTLINE,
        border_width=1,
        width=550,
        password=True,
        can_reveal_password=True,
    )

    confirm_password_field = ft.TextField(
        label=t("confirm_password"),
        hint_text=t("confirm_password_hint"),
        text_vertical_align=-0.30,
        border=ft.InputBorder.OUTLINE,
        border_width=1,
        width=550,
        password=True,
        can_reveal_password=True,
    )

    full_name_field = ft.TextField(
        label=t("full_name"),
        hint_text=t("full_name_hint"),
        text_vertical_align=-0.30,
        border=ft.InputBorder.OUTLINE,
        border_width=1,
        width=550,
    )

    role_dropdown = ft.Dropdown(
        label=t("select_role"),
        width=550,
        border=ft.InputBorder.OUTLINE,
        options=[
            ft.dropdown.Option("student", t("student_role")),
            ft.dropdown.Option("admin", t("admin_role"))
        ],
        value="student"
    )

    # Get the absolute path to the assets directory
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../assets"))
    logo_path = os.path.join(assets_dir, "logo.png")

    register_view = ft.View(
        route="/register",
        controls=[
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.WHITE,
                border_radius=0,
                padding=ft.padding.all(0),
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[language_selector(page)],
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
                                    ft.Text(
                                        value=t("register"),
                                        weight="bold",
                                        size=20,
                                        color=ft.Colors.BLACK
                                    ),
                                    ft.Divider(
                                        height=2,
                                        color=ft.Colors.with_opacity(0.25, ft.Colors.GREY),
                                        thickness=1
                                    ),
                                    ft.Container(
                                        content=ft.ListView(
                                            controls=[
                                                email_field,
                                                password_field,
                                                confirm_password_field,
                                                full_name_field,
                                                role_dropdown,
                                                ft.Container(
                                                    content=ft.ElevatedButton(
                                                        text=t("register"),
                                                        color=ft.Colors.WHITE,
                                                        bgcolor=ft.Colors.BLUE_600,
                                                        width=550,
                                                        style=ft.ButtonStyle(
                                                            shape=ft.RoundedRectangleBorder(radius=button_border_radius)
                                                        ),
                                                        on_click=on_register,
                                                    ),
                                                    alignment=ft.alignment.center,
                                                    padding=ft.padding.only(top=15),
                                                ),
                                                ft.Container(
                                                    content=ft.TextButton(
                                                        text=t("have_account"),
                                                        on_click=go_to_login,
                                                        style=ft.ButtonStyle(
                                                            color=ft.Colors.BLUE_600,
                                                            padding=ft.padding.all(10),
                                                        ),
                                                    ),
                                                    alignment=ft.alignment.center,
                                                    padding=ft.padding.only(top=10, bottom=10),
                                                ),
                                            ],
                                            spacing=15,
                                            height=420, # Increase height to ensure all content is visible
                                            width=550,
                                            auto_scroll=True,
                                        ),
                                        alignment=ft.alignment.center,
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

    return register_view


def main(page: ft.Page):
    page.theme_mode = "light"
    page.window.bgcolor = ft.Colors.WHITE
    page.title = 'StudLog'
    page.window.resizable = False
    page.window.maximized = True
    page.padding = ft.padding.all(0)
    page.bgcolor = ft.Colors.WHITE
    page.views.append(register_screen(page))
    page.go("/register")
    page.update()

if __name__ == '__main__':
    ft.app(target=main)
    # ft.app(target=main, view=ft.WEB_BROWSER)  # For web version
