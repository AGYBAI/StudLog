import flet as ft

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

    register = ft.Column(
        controls=[
            ft.Container(
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                width= 550,
                padding=ft.padding.all(10),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            value='Регистрация',
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
                                    label = 'ФИО',
                                    hint_text='ФИО',
                                    text_vertical_align=-0.30,
                                    border=ft.InputBorder.OUTLINE,
                                    border_width=1,
                                    hint_style=ft.TextStyle(
                                        size=14,
                                        weight='bold',
                                        color=ft.colors.with_opacity(0.4, ft.colors.BLACK)
                                    ),
                                    text_style=ft.TextStyle(
                                        size=14,
                                        weight='bold',
                                        color=ft.colors.with_opacity(0.9, ft.colors.BLACK)
                                    )
                                ),
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
                                    ),
                                    keyboard_type=ft.KeyboardType.EMAIL
                                ),
                                ft.TextField(
                                    label = 'Номер телефона',
                                    hint_text='+7',
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
                                    keyboard_type=ft.KeyboardType.PHONE
                                ),
                                ft.TextField(
                                    label = 'Код группы',
                                    hint_text='###-###-###',
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
                                    keyboard_type=ft.KeyboardType.PHONE
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
                                ft.TextField(
                                    label = 'Повторите пароль',
                                    hint_text='Введите пароль',
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
                                ft.Container(  
                    content=ft.ElevatedButton(
                        text='Регистрация',
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_600,
                        width=550,
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=button_border_radius)  
                        )
                    ),
                    alignment=ft.alignment.center,  
                )
                            ],
                            spacing=15
                        ),
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    text='У меня уже есть аккаунт',
                                    on_click=lambda e: logar(e)
                                )
                            ],
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