import re
import flet as ft
import os
import json
from psycopg2 import connect
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from Pages.translations import translations
from Pages.utils import language_selector
# from Pages.utils import t

current_language = "kz"

translations = {
    "ru": {
        "login": "Вход",
        "email": "Электронная почта",
        "password": "Пароль",
        "type_password": "Введите свой пароль",
    },
    "kz": {
        "login": "Кіру",
        "email": "Электрондық пошта",
        "password": "Құпия сөз",
        "type_password": "Құпия сөзді енгізіңіз",
    }
}
def t(key):
    return translations.get(current_language, {}).get(key, key)

def change_language(page, lang):
    global current_language
    current_language = lang
    page.update()


con = connect(dbname="railway", user="postgres", password="dfFudMqjdNUrRDNEvvTVVvBaNztZfxaP",
              host="autorack.proxy.rlwy.net", port="33741")
cur = con.cursor()

SESSION_FILE = "session.json"

def is_user_logged_in():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            session = json.load(file)
            return session.get("is_logged_in", False)
    return False

def save_session(is_logged_in, email="", role="student"):
    with open(SESSION_FILE, "w") as file:
        json.dump({
            "is_logged_in": is_logged_in, 
            "user_email": email,
            "role": role
        }, file)

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
            field.error_text = "Введите корректный email"
            field.border_color = "red"
        field.update()
    
    def on_login_password_change(e):
        password = e.control.value
        if len(password) < 8:
            login_password_field.error_text = "Пароль должен быть не менее 8 символов"
            login_password_field.border_color = "red"
        elif not any(char.isupper() for char in password):
            login_password_field.error_text = "Пароль должен содержать хотя бы одну заглавную букву"
            login_password_field.border_color = "red"
        elif not any(char.islower() for char in password):
            login_password_field.error_text = "Пароль должен содержать хотя бы одну строчную букву"
            login_password_field.border_color = "red"
        elif not any(char.isdigit() for char in password):
            login_password_field.error_text = "Пароль должен содержать хотя бы одну цифру"
            login_password_field.border_color = "red"
        elif not any(char in "!@#$%^&*()~" for char in password):
            login_password_field.error_text = "Пароль должен содержать хотя бы один специальный символ (!,@,#,$,%,^,&,*,(,),~)"
            login_password_field.border_color = "red"
        else:
            login_password_field.error_text = None
            login_password_field.border_color = "green"
        login_password_field.update()

    def on_login(e: ft.ControlEvent):
        if not validate_email(login_email_field.value):
            page.snack_bar = ft.SnackBar(
                ft.Text("Пожалуйста, исправьте ошибки", color="red"), open=True
            )
            page.update()
            return
        fields = {
            login_email_field: "Поле не может быть пустым!",
            login_password_field: "Поле не может быть пустым!",
        }
        all_fields_filled = True

        for field, error_text in fields.items():
            if not field.value:
                field.helper_text = error_text
                field.helper_style = ft.TextStyle(color=ft.Colors.RED)
                all_fields_filled = False
            else:
                field.helper_text = ""
            field.update()

        if not all_fields_filled:
            return
        try:
            cur.execute(
                "SELECT password, role FROM users WHERE email = %s",
                (login_email_field.value,)
            )
            user = cur.fetchone()

            if user:
                db_password, role = user[0], user[1]
                # Проверка пароля с помощью crypt
                cur.execute(
                    "SELECT crypt(%s, %s) = %s",
                    (login_password_field.value, db_password, db_password)
                )
                is_valid = cur.fetchone()[0]

                if is_valid:
                    page.snack_bar = ft.SnackBar(ft.Text("Вход выполнен! ✅", color="green"), open=True)
                    from Pages.dashboard.dashboard import dashboard_screen
                    save_session(True, login_email_field.value, role)
                    dash_view = ft.View(route="/dashboard", controls=[])
                    page.views.append(dash_view)
                    dashboard_screen(page)
                    page.go("/dashboard")
                else:
                    login_password_field.helper_text = "Неверный пароль"
                    login_password_field.helper_style = ft.TextStyle(color=ft.Colors.RED)
            else:
                login_email_field.helper_text = "Пользователь с таким email не найден"
                login_email_field.helper_style = ft.TextStyle(color=ft.Colors.RED)

        except Exception as error:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Ошибка при входе: {error}", color="red"), open=True
            )
        finally:
            login_email_field.update()
            login_password_field.update()
            page.update()

        if user and login_password_field.value == user[0]:
            from Pages.dashboard.dashboard import dashboard_screen
            save_session(True, login_email_field.value)
            dash_view = ft.View(route="/dashboard", controls=[])
            page.views.append(dash_view) 
            dashboard_screen(page) 
            page.go("/dashboard") 
        else:
            login_password_field.helper_text = "Неверный пароль"
            login_password_field.helper_style = ft.TextStyle(color=ft.Colors.RED)
    
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
                        # Добавляем Dropdown для выбора языка
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
                                            src="/Users/gibatolla/Documents/Практика/StudLog/assets/logo.png",
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
        dash_view = ft.View(route="/dashboard", controls=[])
        page.views.append(dash_view)
        dashboard_screen(page)
        page.go("/dashboard")
        page.update()
    else:
        auth_screen_view = auth_screen(page)
        page.views.append(auth_screen_view)
        page.go("/auth_screen")

if __name__ == '__main__':
    ft.app(target=main)
    # # вебе
    # ft.app(target=main, view=ft.WEB_BROWSER)