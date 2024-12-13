import flet as ft
import re

# Валидация ввода

def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

def validate_phone(phone):
    pattern = r'^\+?\d{10,15}$'
    return re.match(pattern, phone)

def validate_password(password):
    return len(password) >= 8 and any(c.isdigit() for c in password) and any(c in '!?.,;:@#$%^&*' for c in password)

def validate_name(name):
    return name.isalpha()

def main(page: ft.Page):
    # Переменная для отслеживания текущей страницы
    def navigate_to(page_name):
        if page_name == "login":
            page.clean()
            page.add(render_login())
        elif page_name == "register":
            page.clean()
            page.add(render_register())

    # Обработка ошибок
    def display_error(error_message):
        error_text.value = error_message
        error_text.update()

    # Рендер страницы входа
    def render_login():
        def on_login(e):
            email = email_input.value
            password = password_input.value

            if not email or not password:
                display_error("Все поля обязательны к заполнению.")
                return

            if not validate_email(email):
                display_error("Введите корректный email.")
                return

            # Простая проверка авторизации
            if email in accounts and accounts[email]["password"] == password:
                display_error("Успешный вход!")
            else:
                display_error("Неправильный email или пароль.")

        email_input = ft.TextField(label="Адрес e-mail", width=400)
        password_input = ft.TextField(label="Пароль", password=True, can_reveal_password=True, width=400)
        error_text = ft.Text(value="", color="red")

        return ft.Column([
            ft.Text("Вход", size=24, weight="bold"),
            email_input,
            password_input,
            error_text,
            ft.Row([
                ft.ElevatedButton("Войти", on_click=on_login),
                ft.TextButton("Создать новую учетную запись", on_click=lambda e: navigate_to("register")),
            ])
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # Рендер страницы регистрации
    def render_register():
        def on_register(e):
            name = name_input.value
            email = email_input.value
            phone = phone_input.value
            group_code = group_code_input.value
            password = password_input.value
            confirm_password = confirm_password_input.value

            if not all([name, email, phone, group_code, password, confirm_password]):
                display_error("Все поля обязательны к заполнению.")
                return

            if not validate_name(name):
                display_error("ФИО должно содержать только буквы.")
                return

            if not validate_email(email):
                display_error("Введите корректный email.")
                return

            if not validate_phone(phone):
                display_error("Введите корректный номер телефона.")
                return

            if not validate_password(password):
                display_error("Пароль должен содержать минимум 8 символов, хотя бы одну цифру и один знак препинания.")
                return

            if password != confirm_password:
                display_error("Пароли не совпадают.")
                return

            # Сохранение пользователя (в данном случае в память)
            accounts[email] = {"name": name, "phone": phone, "group_code": group_code, "password": password}
            display_error("Регистрация прошла успешно! Теперь войдите.")
            navigate_to("login")

        name_input = ft.TextField(label="ФИО", width=400)
        email_input = ft.TextField(label="Адрес e-mail", width=400)
        phone_input = ft.TextField(label="Номер телефона", width=400)
        group_code_input = ft.TextField(label="Код группы", width=400)
        password_input = ft.TextField(label="Пароль", password=True, can_reveal_password=True, width=400)
        confirm_password_input = ft.TextField(label="Повторите пароль", password=True, can_reveal_password=True, width=400)
        error_text = ft.Text(value="", color="red")

        return ft.Column([
            ft.Text("Регистрация", size=24, weight="bold"),
            name_input,
            email_input,
            phone_input,
            group_code_input,
            password_input,
            confirm_password_input,
            error_text,
            ft.Row([
                ft.ElevatedButton("Зарегистрироваться", on_click=on_register),
                ft.TextButton("У меня уже есть аккаунт", on_click=lambda e: navigate_to("login")),
            ])
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # Список пользователей (простейшая реализация базы данных)
    accounts = {}

    # Начальная страница
    page.title = "Авторизация и Регистрация"
    navigate_to("login")

ft.app(target=main)
