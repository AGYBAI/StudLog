import flet as ft
from psycopg2 import connect

con = connect(dbname="nw", user="postgres", password="1234", host="127.0.0.1", port="5432")
cur = con.cursor()

def main(page: ft.Page):
    page.title = 'StudLog'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.resizable = False
    page.window.maximized = True
    page.padding = ft.padding.all(0)
    page.bgcolor = ft.colors.WHITE

    field_width = 400
    field_height = 50
    button_border_radius = 8
    

    def logar(e: ft.ControlEvent):
        page.remove(register)
        page.add(login)
    
    def registar(e: ft.ControlEvent):
        page.remove(login)
        page.add(register)

    def on_register(e: ft.ControlEvent):
        fio_value = register_fio_field.value
        email_value = register_email_field.value
        phone_value = register_phone_field.value
        group_code_value = register_group_code_field.value
        password_value = register_password_field.value
        confirm_password_value = register_confirm_password_field.value

        error_message = ft.Text("Это обязательное поле!", text_align=ft.TextAlign.RIGHT, color=ft.Colors.RED)
        if not fio_value:
            register_fio_field.helper_text = "Поле не может быть пустым!"
            register_fio_field.helper_style = ft.TextStyle(color=ft.Colors.RED)
        else:
            register_fio_field.helper_text = ""

        if not email_value:
            register_email_field.helper_text = "Поле не может быть пустым!"
            register_email_field.helper_style = ft.TextStyle(color=ft.Colors.RED)
        else:
            register_email_field.helper_text = ""

        if not phone_value:
            register_phone_field.helper_text = "Поле не может быть пустым!"
            register_phone_field.helper_style = ft.TextStyle(color=ft.Colors.RED)
        else:
            register_phone_field.helper_text = ""

        if not group_code_value:
            register_group_code_field.helper_text = "Поле не может быть пустым!"
            register_group_code_field.helper_style = ft.TextStyle(color=ft.Colors.RED)
        else:
            register_group_code_field.helper_text = ""

        if not password_value:
            register_password_field.helper_text = "Поле не может быть пустым!"
            register_password_field.helper_style = ft.TextStyle(color=ft.Colors.RED)
        else:
            register_password_field.helper_text = ""

        if not confirm_password_value:
            register_confirm_password_field.helper_text = "Поле не может быть пустым!"
            register_confirm_password_field.helper_style = ft.TextStyle(color=ft.Colors.RED)
        else:
            register_confirm_password_field.helper_text = ""

        register_fio_field.update()
        register_email_field.update()
        register_phone_field.update()
        register_group_code_field.update()
        register_password_field.update()
        register_confirm_password_field.update()

        if not (register_fio_field.value and
                register_email_field.value and
                register_phone_field.value and
                register_group_code_field.value and
                register_password_field.value and
                register_confirm_password_field.value):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Все поля должны быть заполнены!"),
                bgcolor=ft.colors.RED
            )
            page.snack_bar.open = True
            page.update()
        else:
            cur.execute("""INSERT INTO users(full_name, email, phone_number, password)
            VALUES(%s, %s, %s, %s)""", (fio_value, email_value, phone_value, password_value))
            con.commit()



    login = ft.Column(
        controls=[
            ft.Container(
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                width= 550,
                height= 420,
                padding=ft.padding.all(10),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            value='Вход',
                            weight='bold',
                            size=20,
                            color=ft.colors.BLACK
                        ),
                        ft.Divider(
                            height=1,
                            color=ft.colors.with_opacity(0.25, ft.colors.GREY),
                            thickness=1
                        ),
                        ft.Column(
                            controls=[
                                ft.TextField(
                                    label = 'Адрес e-mail',
                                    hint_text='example@gmail.com',
                                    text_vertical_align=-0.30,
                                    border=ft.InputBorder.OUTLINE,
                                    border_width=1,
                                    hint_style=ft.TextStyle(
                                        size=12,
                                        weight='bold',
                                        color=ft.colors.with_opacity(0.4, ft.colors.BLACK)
                                    ),
                                    text_style=ft.TextStyle(
                                        size=12,
                                        weight='bold',
                                        color=ft.colors.with_opacity(0.9, ft.colors.BLACK)
                                    )
                                ),
                                ft.TextField(
                                    label = 'Пароль',
                                    hint_text='Введите свой пароль',
                                    text_vertical_align=-0.30,
                                    border=ft.InputBorder.OUTLINE,
                                    border_width=1,
                                    hint_style=ft.TextStyle(
                                        size=12,
                                        weight='bold',
                                        color=ft.colors.with_opacity(0.4, ft.colors.BLACK)
                                    ),
                                    text_style=ft.TextStyle(
                                        size=12,
                                        weight='bold',
                                        color=ft.colors.with_opacity(0.9, ft.colors.BLACK)
                                    ),
                                    password=True,
                                    can_reveal_password=True
                                ),
                                ft.Row(
                            controls=[
                                ft.TextButton(
                                    text='Восстановить пароль'
                                ),
                            ],
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
                            shape=ft.RoundedRectangleBorder(radius=button_border_radius)  # Закругленные углы
                        )
                    ),
                    alignment=ft.alignment.center,  
                )
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    text='Создать новую учетную запись',
                                    on_click=lambda e: registar(e)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    register_fio_field = ft.TextField(label='ФИО', hint_text='ФИО')
    register_email_field = ft.TextField(label='Адрес e-mail', hint_text='example@gmail.com')
    register_phone_field = ft.TextField(label='Номер телефона', hint_text='+7')
    register_group_code_field = ft.TextField(label='Код группы', hint_text='###-###-###')
    register_password_field = ft.TextField(label='Пароль', hint_text='Введите свой пароль', password=True)
    register_confirm_password_field = ft.TextField(label='Повторите пароль', hint_text='Введите пароль', password=True)

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