import re
import flet as ft
import os
import json
from psycopg2 import connect
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

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

    # Сохраняем сессию
def save_session(is_logged_in, email=""):
            with open(SESSION_FILE, "w") as file:
                json.dump({"is_logged_in": is_logged_in, "user_email": email}, file)
dash_view = ft.View(
        route="/dashboard",
        controls=[]  # Создаем пустую страницу
    )
def main(page: ft.Page):
    route = "/",
    page.title = 'StudLog'
    if is_user_logged_in():
        from Pages.dashboard.dashboard import dashboard_screen
        page.views.append(dash_view)  # Добавляем новое представление
        dashboard_screen(page)  # Добавляем содержимое на страницу
        page.go("/dashboard") # Если авторизован, показываем Dashboard
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.resizable = False
    page.window.maximized = True
    page.padding = ft.padding.all(0)
    page.bgcolor = ft.colors.WHITE

    field_width = 400
    field_height = 50
    button_border_radius = 8

    global content
    content = ft.Column()

    # Проверка состояния пользователя
    # if is_user_logged_in():
    #     update_auth_content(2)  # Переход на dashboard
    # else:
    #     update_auth_content(0)  # Показать экран входа

    # page.add(content)


    # def update_auth_content(selected_index):
    #         content.controls.clear(),
    #         if selected_index == 0:  # Экран входа
    #             content.controls.append((on_login)),
    #         elif selected_index == 1:  # Экран регистрации
    #             content.controls.append((on_register)),
    #         elif selected_index == 2:  # После входа, переход на dashboard
    #             from Pages.dashboard.dashboard import dashboard_screen
    #             content.controls.append(dashboard_screen())
    #         content.update()

    
# вход
       # Функция для проверки валидности email
    def validate_email(email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    # Обработчик изменения текста в поле email
    def email_change(e, field):
        if validate_email(e.control.value):
            field.error_text = None
            field.border_color = "green"
        else:
            field.error_text = "Введите корректный email"
            field.border_color = "red"
        field.update()
    
    def on_login_password_change(e):
        if len(e.control.value) >= 8:
            login_password_field.error_text = None
            login_password_field.border_color = "green"
        else:
            login_password_field.error_text = "Пароль должен быть не менее 8 символов"
            login_password_field.border_color = "red"
        login_password_field.update()
# регистрация
    
    # Проверка подтверждения пароля
    def on_password_register_change(e):
        if len(register_password_field.value) >= 8:
            register_password_field.error_text = None
            register_password_field.border_color = "green"
        else:
            register_password_field.error_text = "Пароль должен быть не менее 8 символов"
            register_password_field.border_color = "red"
        register_password_field.update()

        # Проверяем совпадение паролей при изменении
        validate_confirm_password()

    # Проверка совпадения пароля и подтверждения
    def on_confirm_password_change(e):
        validate_confirm_password()
    #
    # # Вспомогательная функция для проверки совпадения паролей
    def validate_confirm_password():
        if register_confirm_password_field.value == register_password_field.value and len(register_password_field.value) >= 6:
            register_confirm_password_field.error_text = None
            register_confirm_password_field.border_color = "green"
        else:
            register_confirm_password_field.error_text = "Пароли не совпадают"
            register_confirm_password_field.border_color = "red"
        register_confirm_password_field.update()

        # Проверка ФИО (цифры запрещены)
    def name_change(e, field):
        if re.match(r"^[а-яА-ЯёЁa-zA-Z\s]+$", field.value):
            field.error_text = None
            field.border_color = "green"
        else:
            field.error_text = "ФИО не должно содержать цифр или специальных символов"
            field.border_color = "red"
        field.update()

  

    def phone_change(e, field):
        value = field.value
        formatted = re.sub(r"[^\d]", "", value)
        if len(formatted) > 1:
            formatted = "+7 " + formatted[1:]
        if len(formatted) > 6:
                formatted = formatted[:6] + "-" + formatted[6:]
        if len(formatted) > 10:
                formatted = formatted[:10] + "-" + formatted[10:]
        if len(formatted) > 15:
            formatted = formatted[:15] + "-" + formatted[15:]
        field.value = formatted[:15]
        field.update()

        if len(formatted) == 15:
            field.error_text = None
            field.border_color = "green"
        else:
            field.error_text = "Введите номер в формате +7 777-777-7777"
            field.border_color = "red"
        field.update()


        # Проверка кода группы
    def group_code_change(e, field):
        # Шаблон: ###-###-###
        value = field.value
        formatted = re.sub(r"[^\w]", "", value)  # Удаляем всё, кроме букв и цифр
        if len(formatted) > 3:
            formatted = formatted[:3] + "-" + formatted[3:]
        if len(formatted) > 7:
            formatted = formatted[:7] + "-" + formatted[7:]
        field.value = formatted[:11]  # Ограничиваем длину
        field.update()

        if re.match(r"^\w{3}-\w{3}-\w{3}$", formatted):
            field.error_text = None
            field.border_color = "green"
        else:
            field.error_text = "Код группы должен быть в формате ###-###-###"
            field.border_color = "red"
        field.update()

    

    # Обработчик нажатия кнопки
    # def on_login_click(e):
    #     if (
    #         validate_email(login_email_field.value)
    #         and len(login_password_field.value) >= 6
    #     ):
    #         page.snack_bar = ft.SnackBar(ft.Text("Вход выполнен! ✅"), open=True)
    #     else:
    #         page.snack_bar = ft.SnackBar(
    #             ft.Text("Пожалуйста, исправьте ошибки", color="red"), open=True
    #         )
    #     page.update()

    def logar(e: ft.ControlEvent):
        page.route = "/login"
        page.remove(register)
        page.add(login)
    
    def registar(e: ft.ControlEvent):
        page.remove(login)
        page.add(register)

    def on_login(e: ft.ControlEvent):
       # Проверка формата email и длины пароля
        if not validate_email(login_email_field.value) or len(login_password_field.value) < 6:
            page.snack_bar = ft.SnackBar(
                ft.Text("Пожалуйста, исправьте ошибки", color="red"), open=True
            )
            page.update()
            return

        # Проверка на заполненность полей
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

        # Проверка данных пользователя в базе
        try:
            cur.execute(
                """SELECT password FROM users WHERE email = %s""",
                (login_email_field.value,),
            )
            user = cur.fetchone()

            if user:
                db_password = user[0]
                if login_password_field.value == db_password:
                    page.snack_bar = ft.SnackBar(ft.Text("Вход выполнен! ✅", color="green"), open=True)
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
            page.views.append(dash_view)  # Добавляем новое представление
            dashboard_screen(page)  # Добавляем содержимое на страницу
            page.go("/dashboard")  # Переходим к маршруту
        else:
            login_password_field.helper_text = "Неверный пароль"
            login_password_field.helper_style = ft.TextStyle(color=ft.Colors.RED)

    def on_register(e: ft.ControlEvent):
    # Проверяем, что все поля заполнены и не содержат ошибок
        required_fields = [
            register_fio_field,
            register_email_field,
            register_phone_field,
            register_group_code_field,
            register_password_field,
            register_confirm_password_field,
        ]

    # Флаг для проверки всех полей
        all_valid = True

        for field in required_fields:
            if not field.value:  # Поле пустое
                field.error_text = "Поле не может быть пустым!"
                field.border_color = "red"
                all_valid = False
            elif field.error_text:  # У поля уже есть ошибка
                all_valid = False
            field.update()

        # Если все проверки пройдены, добавляем пользователя в базу данных
        if all_valid:
            try:
                cur.execute(
                    """INSERT INTO users (full_name, email, phone_number, password)
                    VALUES (%s, %s, %s, %s)""",
                    (
                        register_fio_field.value,
                        register_email_field.value,
                        register_phone_field.value,
                        register_password_field.value,
                    ),
                )
                con.commit()
                page.snack_bar = ft.SnackBar(
                    ft.Text("Регистрация прошла успешно! ✅", color="green"),
                    open=True,
                )
                from Pages.dashboard.dashboard import dashboard_screen
                save_session(True, login_email_field.value)
                page.views.append(dash_view)  # Добавляем новое представление
                dashboard_screen(page)  # Добавляем содержимое на страницу
                page.go("/dashboard")  # Переходим к маршруту
            except Exception as error:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Ошибка регистрации: {error}", color="red"),
                    open=True,
                )
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("Проверьте введенные данные!", color="red"),
                open=True,
            )

        page.update()

        
        # fields = {
        #     register_fio_field: "Поле не может быть пустым!",
        #     register_email_field: "Поле не может быть пустым!",
        #     register_phone_field: "Поле не может быть пустым!",
        #     register_group_code_field: "Поле не может быть пустым!",
        #     register_password_field: "Поле не может быть пустым!",
        #     register_confirm_password_field: "Поле не может быть пустым!"
        # }


        # all_fields_filled = True

        # for field, error_text in fields.items():
        #     if not field.value:
        #         field.helper_text = error_text
        #         field.helper_style = ft.TextStyle(color=ft.Colors.RED)
        #         all_fields_filled = False
        #     else:
        #         field.helper_text = ""
        #     field.update()

        # if all_fields_filled:
        #     cur.execute("""INSERT INTO users(full_name, email, phone_number, password)
        #                    VALUES(%s, %s, %s, %s)""",
        #                 (register_fio_field.value,
        #                  register_email_field.value,
        #                  register_phone_field.value,
        #                  register_password_field.value))
        #     con.commit()

        # 123
        # if not (register_fio_field.value and
        #         register_email_field.value and
        #         register_phone_field.value and
        #         register_group_code_field.value and
        #         register_password_field.value and
        #         register_confirm_password_field.value):
        #     page.snack_bar = ft.SnackBar(
        #         content=ft.Text("Все поля должны быть заполнены!"),
        #         bgcolor=ft.colors.RED
        #     )
        #     page.snack_bar.open = True
        #     page.update()
        # else:
        #     cur.execute("""INSERT INTO users(full_name, email, phone_number, password)
        #     VALUES(%s, %s, %s, %s)""", (fio_value, email_value, phone_value, password_value))
        #     con.commit()


    login_email_field = ft.TextField(
        label='Адрес e-mail',
        hint_text='example@gmail.com',
        on_change=lambda e: email_change(e, login_email_field),
        text_vertical_align=-0.30,
        border=ft.InputBorder.OUTLINE,
        border_width=1,
        hint_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.4, ft.colors.BLACK)),
        text_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.9, ft.colors.BLACK))
    )

    login_password_field = ft.TextField(
        label='Пароль',
        hint_text='Введите свой пароль',
        on_change=on_login_password_change,
        text_vertical_align=-0.30,
        border=ft.InputBorder.OUTLINE,
        border_width=1,
        hint_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.4, ft.colors.BLACK)),
        text_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.9, ft.colors.BLACK)),
        password=True,
        can_reveal_password=True
    )

    login = ft.Column(
        controls=[
            ft.Container(
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                width=550,
                height=420,
                padding=ft.padding.all(10),
                content=ft.Column(
                    controls=[
                        ft.Text(value='Вход', weight='bold', size=20, color=ft.colors.BLACK),
                        ft.Divider(height=1, color=ft.colors.with_opacity(0.25, ft.colors.GREY), thickness=1),
                        ft.Column(
                            controls=[login_email_field, login_password_field,
                                      ft.Row(
                                          controls=[ft.TextButton(text='Восстановить пароль')],
                                          alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                      ),
                                      ft.Container(
                                          content=ft.ElevatedButton(
                                              text='Вход',
                                              color=ft.colors.WHITE,
                                              bgcolor=ft.colors.BLUE_600,
                                              width=550,
                                              height=50,
                                              style=ft.ButtonStyle(
                                                  shape=ft.RoundedRectangleBorder(radius=button_border_radius)
                                              ),
                                              on_click=on_login
                                          ),
                                          alignment=ft.alignment.center
                                      )
                                      ],
                            spacing=15,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Row(
                            controls=[
                                ft.TextButton(text='Создать новую учетную запись', on_click=lambda e: registar(e))],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    register_fio_field = ft.TextField(label='ФИО', hint_text='ФИО', on_change=lambda e: name_change(e, register_fio_field), border=ft.InputBorder.OUTLINE, border_width=1,
                                      hint_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.4, ft.colors.BLACK)),
                                      text_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.9, ft.colors.BLACK)))
    register_email_field = ft.TextField(label='Адрес e-mail', hint_text='example@gmail.com', on_change=lambda e: email_change(e, register_email_field), border=ft.InputBorder.OUTLINE, border_width=1,
                                      hint_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.4, ft.colors.BLACK)),
                                      text_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.9, ft.colors.BLACK)))
    register_phone_field = ft.TextField(label='Номер телефона', hint_text='+7', on_change=lambda e: phone_change(e, register_phone_field), border=ft.InputBorder.OUTLINE, border_width=1,
                                      hint_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.4, ft.colors.BLACK)),
                                      text_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.9, ft.colors.BLACK)))
    register_group_code_field = ft.TextField(label='Код группы', hint_text='###-###-###', on_change=lambda e: group_code_change(e, register_group_code_field), border=ft.InputBorder.OUTLINE, border_width=1,
                                      hint_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.4, ft.colors.BLACK)),
                                      text_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.9, ft.colors.BLACK)))
    register_password_field = ft.TextField(label='Пароль', hint_text='Введите свой пароль', on_change=on_password_register_change, password=True, border=ft.InputBorder.OUTLINE, border_width=1,
                                      hint_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.4, ft.colors.BLACK)),
                                      text_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.9, ft.colors.BLACK)))
    register_confirm_password_field = ft.TextField(label='Повторите пароль', hint_text='Введите пароль', on_change= on_confirm_password_change, password=True, border=ft.InputBorder.OUTLINE, border_width=1,
                                      hint_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.4, ft.colors.BLACK)),
                                      text_style=ft.TextStyle(size=12, weight='bold', color=ft.colors.with_opacity(0.9, ft.colors.BLACK)))

    register = ft.Column(
        controls=[
            ft.Container(
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                width=550,
                padding=ft.padding.all(10),
                content=ft.Column(
                    controls=[
                        ft.Text(value='Регистрация', weight='bold', size=20, color=ft.colors.BLACK),
                        ft.Divider(height=1, color=ft.colors.with_opacity(0.25, ft.colors.GREY), thickness=1),
                        ft.Column(
                            controls=[
                                register_fio_field,
                                register_email_field,
                                register_phone_field,
                                register_group_code_field,
                                register_password_field,
                                register_confirm_password_field,
                                ft.ElevatedButton(
                                    text='Регистрация',
                                    color=ft.colors.WHITE,
                                    bgcolor=ft.colors.BLUE_600,
                                    width=550,
                                    height=50,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=button_border_radius)
                                    ),
                                    on_click=on_register
                                )
                            ],
                            spacing=15
                        ),
                        ft.Row(
                            controls=[ft.TextButton(text='У меня уже есть аккаунт', on_click=logar)],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(login)

if __name__ == '__main__':
    ft.app(target=main)